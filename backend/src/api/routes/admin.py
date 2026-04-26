"""Admin endpoints for system management."""
from fastapi import APIRouter, HTTPException, status, Query, Depends
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime
from config import logger
from src.core.database import (
    get_collection,
    COLLECTION_TICKETS,
    COLLECTION_CONVERSATIONS,
    COLLECTION_KNOWLEDGE_BASE,
    COLLECTION_CUSTOMERS,
    COLLECTION_SUBSCRIPTIONS,
    COLLECTION_ORDERS,
)
from src.core.vector_store import add_knowledge_entry
from src.models.ticket import Ticket
from src.models.customer import Customer
from src.api.routes.auth import get_current_customer

router = APIRouter()
ADMIN_EMAIL = "mdnadimuddin62063@gmail.com"


def require_admin(current_customer: Customer = Depends(get_current_customer)) -> Customer:
    """Allow only the configured admin user to access admin routes."""
    if (current_customer.email or "").lower() != ADMIN_EMAIL:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access only"
        )
    return current_customer


class KnowledgeEntry(BaseModel):
    """Knowledge base entry schema."""
    content: str = Field(..., min_length=10, description="Content text")
    category: str = Field(..., description="Category (authentication, billing, etc.)")
    industry: str = Field(default="saas", description="Industry")


class TicketResponse(BaseModel):
    """Ticket response schema."""
    ticket_id: str
    customer_id: str
    priority: str
    category: str
    status: str
    title: str
    created_at: datetime
    confidence_score: Optional[float] = None
    source_intent: Optional[str] = None
    escalation_reason: Optional[str] = None


@router.post("/knowledge")
async def add_knowledge(entry: KnowledgeEntry):
    """
    Add entry to knowledge base.

    Args:
        entry: Knowledge entry

    Returns:
        Entry ID
    """
    try:
        logger.info(f"Adding knowledge entry: {entry.category}")

        # Add to vector store
        entry_id = add_knowledge_entry(
            content=entry.content,
            category=entry.category,
            industry=entry.industry
        )

        logger.info(f"Knowledge entry added: {entry_id}")

        return {
            "entry_id": entry_id,
            "category": entry.category,
            "status": "added"
        }

    except Exception as e:
        logger.error(f"Error adding knowledge entry: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.get("/tickets", response_model=List[TicketResponse])
async def list_tickets(
    status_filter: Optional[str] = Query(None, description="Filter by status"),
    priority: Optional[str] = Query(None, description="Filter by priority"),
    limit: int = Query(50, le=100, description="Number of tickets to return")
):
    """
    List support tickets.

    Args:
        status_filter: Filter by status
        priority: Filter by priority
        limit: Maximum tickets to return

    Returns:
        List of tickets
    """
    try:
        tickets_coll = get_collection(COLLECTION_TICKETS)

        # Build filter
        query_filter = {}
        if status_filter:
            query_filter["status"] = status_filter
        if priority:
            query_filter["priority"] = priority

        # Get tickets
        tickets = list(
            tickets_coll.find(query_filter)
            .sort("created_at", -1)
            .limit(limit)
        )

        # Convert to response model
        ticket_responses = []
        for ticket_data in tickets:
            meta = ticket_data.get("metadata", {})
            ticket_responses.append(TicketResponse(
                ticket_id=ticket_data["ticket_id"],
                customer_id=ticket_data["customer_id"],
                priority=ticket_data["priority"],
                category=ticket_data["category"],
                status=ticket_data["status"],
                title=ticket_data["title"],
                created_at=ticket_data["created_at"],
                confidence_score=meta.get("confidence_score"),
                source_intent=meta.get("source_intent"),
                escalation_reason=meta.get("escalation_reason"),
            ))

        logger.info(f"Retrieved {len(ticket_responses)} tickets")
        return ticket_responses

    except Exception as e:
        logger.error(f"Error listing tickets: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.get("/tickets/{ticket_id}")
async def get_ticket(ticket_id: str):
    """
    Get ticket details.

    Args:
        ticket_id: Ticket ID

    Returns:
        Ticket details
    """
    try:
        tickets_coll = get_collection(COLLECTION_TICKETS)
        ticket_data = tickets_coll.find_one({"ticket_id": ticket_id})

        if not ticket_data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Ticket not found"
            )

        # Remove MongoDB _id
        ticket_data.pop("_id", None)

        return ticket_data

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error retrieving ticket: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.get("/stats")
async def get_stats():
    """
    Get system statistics.

    Returns:
        System stats
    """
    try:
        conversations_coll = get_collection(COLLECTION_CONVERSATIONS)
        tickets_coll = get_collection(COLLECTION_TICKETS)

        # Count conversations
        total_conversations = conversations_coll.count_documents({})
        active_conversations = conversations_coll.count_documents({"status": "active"})
        escalated_conversations = conversations_coll.count_documents({"status": "escalated"})

        # Count tickets
        total_tickets = tickets_coll.count_documents({})
        open_tickets = tickets_coll.count_documents({"status": "open"})
        resolved_tickets = tickets_coll.count_documents({"status": "resolved"})

        # Calculate escalation rate
        escalation_rate = (escalated_conversations / total_conversations * 100) if total_conversations > 0 else 0

        stats = {
            "conversations": {
                "total": total_conversations,
                "active": active_conversations,
                "escalated": escalated_conversations
            },
            "tickets": {
                "total": total_tickets,
                "open": open_tickets,
                "resolved": resolved_tickets
            },
            "metrics": {
                "escalation_rate": round(escalation_rate, 2),
                "resolution_rate": round((resolved_tickets / total_tickets * 100) if total_tickets > 0 else 0, 2)
            },
            "timestamp": datetime.utcnow()
        }

        logger.info("System stats retrieved")
        return stats

    except Exception as e:
        logger.error(f"Error getting stats: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.get("/test-data")
async def get_test_data_overview():
    """
    Get seeded test-data overview for quick QA verification.

    Returns:
        Counts and sample records for key collections
    """
    try:
        customers_coll = get_collection(COLLECTION_CUSTOMERS)
        subscriptions_coll = get_collection(COLLECTION_SUBSCRIPTIONS)
        orders_coll = get_collection(COLLECTION_ORDERS)
        conversations_coll = get_collection(COLLECTION_CONVERSATIONS)
        knowledge_coll = get_collection(COLLECTION_KNOWLEDGE_BASE)

        seeded_accounts = list(
            customers_coll.find(
                {},
                {
                    "_id": 0,
                    "customer_id": 1,
                    "name": 1,
                    "email": 1,
                    "industry": 1,
                }
            ).sort("created_at", -1).limit(10)
        )

        sample_orders = list(
            orders_coll.find(
                {},
                {
                    "_id": 0,
                    "order_id": 1,
                    "customer_id": 1,
                    "status": 1,
                    "payment_status": 1,
                    "total": 1,
                }
            ).sort("created_at", -1).limit(10)
        )

        return {
            "counts": {
                "customers": customers_coll.count_documents({}),
                "subscriptions": subscriptions_coll.count_documents({}),
                "orders": orders_coll.count_documents({}),
                "conversations": conversations_coll.count_documents({}),
                "knowledge_entries": knowledge_coll.count_documents({}),
            },
            "seeded_accounts": seeded_accounts,
            "sample_orders": sample_orders,
            "timestamp": datetime.utcnow(),
        }

    except Exception as e:
        logger.error(f"Error getting test data overview: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.patch("/tickets/{ticket_id}/status")
async def update_ticket_status(ticket_id: str, body: Dict[str, Any]):
    """
    Update ticket status (admin action).
    Body: {"status": "resolved" | "in_progress" | "assigned" | "closed"}
    """
    try:
        new_status = body.get("status", "").lower()
        valid = {"open", "assigned", "in_progress", "waiting_customer", "resolved", "closed"}
        if new_status not in valid:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail=f"Invalid status. Must be one of: {', '.join(sorted(valid))}"
            )

        tickets_coll = get_collection(COLLECTION_TICKETS)
        update_fields: Dict[str, Any] = {"status": new_status, "updated_at": datetime.utcnow()}
        if new_status == "resolved":
            update_fields["resolved_at"] = datetime.utcnow()

        result = tickets_coll.update_one(
            {"ticket_id": ticket_id},
            {"$set": update_fields}
        )

        if result.matched_count == 0:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Ticket not found")

        logger.info(f"Ticket {ticket_id} status updated to {new_status}")
        return {"ticket_id": ticket_id, "status": new_status, "updated_at": update_fields["updated_at"]}

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating ticket status: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.get("/customers")
async def list_customers(limit: int = Query(50, le=200)):
    """Return all customers with their subscription plan for the lookup UI."""
    try:
        customers_coll = get_collection(COLLECTION_CUSTOMERS)
        subscriptions_coll = get_collection(COLLECTION_SUBSCRIPTIONS)

        customers = list(
            customers_coll.find({}, {"_id": 0, "password_hash": 0})
            .sort("created_at", -1)
            .limit(limit)
        )

        # Attach subscription plan to each customer
        for c in customers:
            sub = subscriptions_coll.find_one(
                {"customer_id": c["customer_id"]},
                {"_id": 0, "plan": 1, "status": 1, "monthly_price": 1}
            )
            c["subscription"] = sub or {}

        return customers

    except Exception as e:
        logger.error(f"Error listing customers: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.get("/customers/{customer_id}")
async def get_customer_profile(customer_id: str):
    """
    Full customer profile: personal info, subscription, all orders,
    all tickets, all conversations with message count and summary.
    Used by the admin Customer Lookup page to verify bot responses.
    """
    try:
        customers_coll = get_collection(COLLECTION_CUSTOMERS)
        subscriptions_coll = get_collection(COLLECTION_SUBSCRIPTIONS)
        orders_coll = get_collection(COLLECTION_ORDERS)
        tickets_coll = get_collection(COLLECTION_TICKETS)
        conversations_coll = get_collection(COLLECTION_CONVERSATIONS)

        customer = customers_coll.find_one(
            {"customer_id": customer_id},
            {"_id": 0, "password_hash": 0}
        )
        if not customer:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Customer not found")

        subscription = subscriptions_coll.find_one(
            {"customer_id": customer_id}, {"_id": 0}
        )

        orders = list(orders_coll.find({"customer_id": customer_id}, {"_id": 0}).sort("created_at", -1))
        tickets = list(tickets_coll.find({"customer_id": customer_id}, {"_id": 0}).sort("created_at", -1))

        # Conversations: include message count + last user and assistant messages as preview
        raw_convs = list(conversations_coll.find({"customer_id": customer_id}, {"_id": 0}).sort("created_at", -1))
        conversations = []
        for conv in raw_convs:
            messages = conv.get("messages", [])
            last_user = next((m["content"] for m in reversed(messages) if m.get("role") == "user"), None)
            last_bot = next((m["content"] for m in reversed(messages) if m.get("role") == "assistant"), None)
            conversations.append({
                "conversation_id": conv.get("conversation_id"),
                "status": conv.get("status"),
                "channel": conv.get("channel"),
                "message_count": len(messages),
                "last_user_message": (last_user or "")[:200],
                "last_bot_message": (last_bot or "")[:300],
                "created_at": conv.get("created_at"),
                "updated_at": conv.get("updated_at"),
            })

        # Computed billing totals for the showcase verification panel
        completed_orders = [o for o in orders if o.get("payment_status") == "completed"]
        total_spend = round(sum(o.get("total", 0) for o in completed_orders), 2)
        monthly_price = (subscription or {}).get("monthly_price", 0) or 0
        subscription_payments = round(monthly_price * max(1, len(completed_orders)), 2)

        return {
            "customer": customer,
            "subscription": subscription,
            "orders": orders,
            "tickets": tickets,
            "conversations": conversations,
            "summary": {
                "total_orders": len(orders),
                "completed_orders": len(completed_orders),
                "total_spend": total_spend,
                "subscription_payments": subscription_payments,
                "monthly_price": monthly_price,
                "open_tickets": sum(1 for t in tickets if t.get("status") == "open"),
                "active_conversations": sum(1 for c in conversations if c.get("status") == "active"),
            }
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting customer profile: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.delete("/conversations/{conversation_id}")
async def delete_conversation(conversation_id: str):
    """
    Delete a conversation (admin only).

    Args:
        conversation_id: Conversation ID

    Returns:
        Deletion confirmation
    """
    try:
        conversations_coll = get_collection(COLLECTION_CONVERSATIONS)
        result = conversations_coll.delete_one({"conversation_id": conversation_id})

        if result.deleted_count == 0:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Conversation not found"
            )

        logger.info(f"Deleted conversation: {conversation_id}")
        return {"status": "deleted", "conversation_id": conversation_id}

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting conversation: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )
