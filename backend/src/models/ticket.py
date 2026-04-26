"""Ticket data models."""
from datetime import datetime
from typing import Dict, Any, Optional
from pydantic import BaseModel, Field
from config.industry_configs import Priority
from src.core.constants import TicketStatus, TicketCategory


class Ticket(BaseModel):
    """Support ticket model."""

    ticket_id: str
    conversation_id: str
    customer_id: str
    priority: Priority
    category: TicketCategory
    title: str
    description: str
    agent_summary: str  # What the AI tried
    status: TicketStatus = TicketStatus.OPEN
    assigned_to: Optional[str] = None
    resolution: Optional[str] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    resolved_at: Optional[datetime] = None

    class Config:
        use_enum_values = True

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for MongoDB."""
        return self.model_dump(mode='json')

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Ticket":
        """Create from dictionary."""
        return cls(**data)

    def assign(self, agent_id: str) -> None:
        """Assign ticket to an agent."""
        self.assigned_to = agent_id
        self.status = TicketStatus.ASSIGNED
        self.updated_at = datetime.utcnow()

    def resolve(self, resolution: str) -> None:
        """Mark ticket as resolved."""
        self.resolution = resolution
        self.status = TicketStatus.RESOLVED
        self.resolved_at = datetime.utcnow()
        self.updated_at = datetime.utcnow()


class TicketCreate(BaseModel):
    """Schema for creating a new ticket."""

    conversation_id: str
    customer_id: str
    priority: Priority
    category: TicketCategory
    title: str
    description: str
    agent_summary: str

    class Config:
        use_enum_values = True


class TicketResponse(BaseModel):
    """Schema for ticket response."""

    ticket_id: str
    priority: str
    category: str
    title: str
    status: str
    created_at: datetime

    @classmethod
    def from_ticket(cls, ticket: Ticket) -> "TicketResponse":
        """Create response from ticket."""
        return cls(
            ticket_id=ticket.ticket_id,
            priority=ticket.priority,
            category=ticket.category,
            title=ticket.title,
            status=ticket.status,
            created_at=ticket.created_at
        )
