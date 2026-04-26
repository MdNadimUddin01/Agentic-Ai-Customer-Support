"""Order data models."""
from datetime import datetime
from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field
from src.core.constants import OrderStatus, PaymentStatus


class OrderItem(BaseModel):
    """Order item model."""

    product_id: str
    name: str
    quantity: int
    price: float
    metadata: Dict[str, Any] = Field(default_factory=dict)


class Order(BaseModel):
    """E-commerce order model."""

    order_id: str
    customer_id: str
    items: List[OrderItem]
    subtotal: float
    tax: float
    shipping: float
    total: float
    status: OrderStatus
    payment_status: PaymentStatus
    tracking_number: Optional[str] = None
    courier: Optional[str] = None
    shipping_address: Dict[str, Any] = Field(default_factory=dict)
    billing_address: Dict[str, Any] = Field(default_factory=dict)
    notes: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    shipped_at: Optional[datetime] = None
    delivered_at: Optional[datetime] = None

    class Config:
        use_enum_values = True

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for MongoDB."""
        return self.model_dump(mode='json')

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Order":
        """Create from dictionary."""
        return cls(**data)

    def update_status(self, status: OrderStatus) -> None:
        """Update order status."""
        self.status = status
        self.updated_at = datetime.utcnow()

        if status == OrderStatus.SHIPPED:
            self.shipped_at = datetime.utcnow()
        elif status == OrderStatus.DELIVERED:
            self.delivered_at = datetime.utcnow()


class ShippingStatus(BaseModel):
    """Shipping status from courier."""

    tracking_number: str
    courier: str
    status: str
    location: Optional[str] = None
    estimated_delivery: Optional[datetime] = None
    events: List[Dict[str, Any]] = Field(default_factory=list)
    last_updated: datetime = Field(default_factory=datetime.utcnow)


class OrderResponse(BaseModel):
    """Schema for order response."""

    order_id: str
    customer_id: str
    total: float
    status: str
    tracking_number: Optional[str]
    created_at: datetime

    @classmethod
    def from_order(cls, order: Order) -> "OrderResponse":
        """Create response from order."""
        return cls(
            order_id=order.order_id,
            customer_id=order.customer_id,
            total=order.total,
            status=order.status,
            tracking_number=order.tracking_number,
            created_at=order.created_at
        )
