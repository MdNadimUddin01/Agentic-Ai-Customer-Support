"""
Week 7 — Order Tracking API Tool (mock external API + DB lookup).

Simulates calling an external courier API (e.g. FedEx/UPS) based on
a tracking number retrieved from MongoDB, then returns a human-readable
status summary.
"""
from typing import Optional, Dict, Any, List
from datetime import datetime, timedelta
import random
from pydantic import BaseModel, Field
from config import logger
from src.core.database import get_collection
from src.core.constants import COLLECTION_ORDERS
from src.tools.base_tool import BaseSupportTool


# ---------------------------------------------------------------------------
# Mock courier gateway
# ---------------------------------------------------------------------------

_COURIER_EVENTS: Dict[str, List[Dict[str, Any]]] = {
    "pending": [
        {"timestamp": "2026-04-15 09:00", "location": "Warehouse", "status": "Order received and queued for processing"},
    ],
    "processing": [
        {"timestamp": "2026-04-15 09:00", "location": "Warehouse", "status": "Order received"},
        {"timestamp": "2026-04-16 11:30", "location": "Sorting Facility", "status": "Package picked and labelled"},
    ],
    "shipped": [
        {"timestamp": "2026-04-15 09:00", "location": "Warehouse", "status": "Order received"},
        {"timestamp": "2026-04-16 11:30", "location": "Sorting Facility", "status": "Package picked and labelled"},
        {"timestamp": "2026-04-17 07:15", "location": "Regional Hub", "status": "In transit — out for delivery hub"},
    ],
    "delivered": [
        {"timestamp": "2026-04-15 09:00", "location": "Warehouse", "status": "Order received"},
        {"timestamp": "2026-04-16 11:30", "location": "Sorting Facility", "status": "Package picked and labelled"},
        {"timestamp": "2026-04-17 07:15", "location": "Regional Hub", "status": "In transit"},
        {"timestamp": "2026-04-18 14:02", "location": "Delivery Address", "status": "Delivered — left at front door"},
    ],
    "cancelled": [
        {"timestamp": "2026-04-15 09:00", "location": "Warehouse", "status": "Order cancelled by customer"},
    ],
}


def _mock_courier_api_call(tracking_number: str, courier: str, order_status: str) -> Dict[str, Any]:
    """Simulate calling an external courier REST API."""
    events = _COURIER_EVENTS.get(order_status, _COURIER_EVENTS["processing"])
    eta = None
    if order_status in ("pending", "processing", "shipped"):
        eta = (datetime.utcnow() + timedelta(days=random.randint(1, 4))).strftime("%Y-%m-%d")

    return {
        "tracking_number": tracking_number,
        "courier": courier or "MockCourier",
        "current_status": order_status,
        "estimated_delivery": eta,
        "events": events,
        "api_source": "external_courier_api_mock",
        "fetched_at": datetime.utcnow().isoformat(),
    }


# ---------------------------------------------------------------------------
# Tool
# ---------------------------------------------------------------------------

class OrderTrackingInput(BaseModel):
    """Input for order tracking."""
    customer_id: str = Field(description="Customer ID to look up orders for")
    order_id: Optional[str] = Field(default=None, description="Specific order ID to track (optional)")


class OrderTrackingTool(BaseSupportTool):
    """
    Tracks order status by querying the orders DB and calling an external courier API.

    Used when intent = order_status.
    """

    name: str = "track_order"
    description: str = (
        "Track the status of a customer's order. "
        "Looks up the order in the database then calls the courier API for live tracking events. "
        "Provide customer_id and optionally order_id for a specific order."
    )
    args_schema: type[BaseModel] = OrderTrackingInput

    @staticmethod
    def _extract_status_filters(message: Optional[str]) -> List[str]:
        """Infer requested order statuses from natural language."""
        if not message:
            return []

        message_lower = message.lower()
        filters: List[str] = []

        if any(term in message_lower for term in ["pending", "not delivered", "not completed"]):
            filters.extend(["pending", "processing", "shipped"])
        if any(term in message_lower for term in ["processing", "in process"]):
            filters.append("processing")
        if any(term in message_lower for term in ["shipped", "in transit", "tracking"]):
            filters.append("shipped")
        if "delivered" in message_lower:
            filters.append("delivered")
        if any(term in message_lower for term in ["cancelled", "canceled"]):
            filters.append("cancelled")
        if "refunded" in message_lower:
            filters.append("refunded")

        return list(dict.fromkeys(filters))

    def execute(self, customer_id: str, order_id: Optional[str] = None, query_text: Optional[str] = None) -> str:
        """Fetch order from DB → call mock courier API → return status summary."""
        try:
            logger.info(f"OrderTrackingTool: customer={customer_id} order={order_id}")
            orders_coll = get_collection(COLLECTION_ORDERS)

            query: Dict[str, Any] = {"customer_id": customer_id}
            if order_id:
                query["order_id"] = order_id

            status_filters = self._extract_status_filters(query_text)
            if status_filters:
                query["status"] = {"$in": status_filters}

            orders = list(orders_coll.find(query, {"_id": 0}).sort("created_at", -1).limit(5))

            if not orders:
                if status_filters:
                    requested = ", ".join(status_filters)
                    return (
                        f"I couldn't find any {requested} order for your account right now. "
                        "If you want, I can also show your latest delivered or cancelled orders."
                    )

                orders = [self._mock_order(customer_id, order_id)]

            lines: List[str] = []
            for order in orders[:3]:
                tracking = order.get("tracking_number", f"TRK{order['order_id'].replace('-', '')[:10]}")
                courier = order.get("courier", "MockCourier")
                o_status = order.get("status", "processing")

                # External courier API call
                courier_data = _mock_courier_api_call(tracking, courier, o_status)

                eta_str = f"ETA: {courier_data['estimated_delivery']}" if courier_data.get("estimated_delivery") else ""
                last_event = courier_data["events"][-1] if courier_data["events"] else {}

                lines.append(
                    f"Order {order['order_id']} — Status: {o_status.upper()}\n"
                    f"  Tracking: {tracking} via {courier_data['courier']}\n"
                    f"  Latest update: {last_event.get('status', 'N/A')} @ {last_event.get('location', 'N/A')}\n"
                    f"  {eta_str}\n"
                    f"  Items: {', '.join(i.get('name', 'item') for i in order.get('items', []))}\n"
                    f"  Total: ₹{order.get('total', 0):.2f}"
                )

            return (
                f"Found {len(orders)} order(s) for your account:\n\n"
                + "\n\n".join(lines)
                + "\n\nIs there anything else you'd like to know about your orders?"
            )

        except Exception as e:
            logger.error(f"OrderTrackingTool error: {e}")
            return f"I couldn't retrieve your order details right now. Please try again or quote your order ID directly. ({e})"

    def _mock_order(self, customer_id: str, order_id: Optional[str]) -> Dict[str, Any]:
        """Fallback mock order when DB has no data."""
        return {
            "order_id": order_id or "ORD-DEMO-001",
            "customer_id": customer_id,
            "status": "shipped",
            "tracking_number": "TRK9876543210",
            "courier": "MockCourier",
            "items": [{"name": "Wireless Headphones"}, {"name": "USB-C Cable"}],
            "total": 149.98,
        }
