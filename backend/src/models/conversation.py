"""Conversation data models."""
from datetime import datetime
from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field
from src.core.constants import ConversationStatus, MessageRole, Channel


class Message(BaseModel):
    """Individual message in a conversation."""

    role: MessageRole
    content: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    metadata: Dict[str, Any] = Field(default_factory=dict)

    class Config:
        use_enum_values = True


class Conversation(BaseModel):
    """Conversation model."""

    conversation_id: str
    customer_id: str
    channel: Channel
    industry: str = "saas"
    messages: List[Message] = Field(default_factory=list)
    context: Dict[str, Any] = Field(default_factory=dict)
    status: ConversationStatus = ConversationStatus.ACTIVE
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        use_enum_values = True

    def add_message(self, role: MessageRole, content: str, metadata: Optional[Dict[str, Any]] = None) -> None:
        """Add a message to the conversation."""
        message = Message(
            role=role,
            content=content,
            metadata=metadata or {}
        )
        self.messages.append(message)
        self.updated_at = datetime.utcnow()

    def get_recent_messages(self, count: int = 10) -> List[Message]:
        """Get recent messages."""
        return self.messages[-count:]

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for MongoDB."""
        return self.model_dump(mode='json')

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Conversation":
        """Create from dictionary."""
        return cls(**data)


class ConversationCreate(BaseModel):
    """Schema for creating a new conversation."""

    customer_id: str
    channel: Channel
    industry: str = "saas"
    initial_message: Optional[str] = None

    class Config:
        use_enum_values = True


class ConversationResponse(BaseModel):
    """Schema for conversation response."""

    conversation_id: str
    customer_id: str
    channel: str
    status: str
    message_count: int
    created_at: datetime
    updated_at: datetime

    @classmethod
    def from_conversation(cls, conv: Conversation) -> "ConversationResponse":
        """Create response from conversation."""
        return cls(
            conversation_id=conv.conversation_id,
            customer_id=conv.customer_id,
            channel=conv.channel,
            status=conv.status,
            message_count=len(conv.messages),
            created_at=conv.created_at,
            updated_at=conv.updated_at
        )
