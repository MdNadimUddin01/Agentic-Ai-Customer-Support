"""Customer data models."""
from datetime import datetime
from typing import Dict, Any, Optional
from pydantic import BaseModel, EmailStr, Field
from src.core.constants import SubscriptionPlan, SubscriptionStatus


class Customer(BaseModel):
    """Customer model."""

    customer_id: str
    name: str
    email: EmailStr
    password_hash: Optional[str] = None
    phone: Optional[str] = None
    channel_ids: Dict[str, str] = Field(default_factory=dict)
    preferences: Dict[str, Any] = Field(default_factory=dict)
    crm_id: Optional[str] = None
    industry: str = "saas"
    metadata: Dict[str, Any] = Field(default_factory=dict)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for MongoDB."""
        return self.model_dump(mode='json')

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Customer":
        """Create from dictionary."""
        return cls(**data)


class Subscription(BaseModel):
    """SaaS subscription model."""

    customer_id: str
    plan: SubscriptionPlan
    status: SubscriptionStatus
    start_date: datetime
    end_date: Optional[datetime] = None
    renewal_date: Optional[datetime] = None
    monthly_price: float
    features: Dict[str, Any] = Field(default_factory=dict)
    usage: Dict[str, Any] = Field(default_factory=dict)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        use_enum_values = True

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for MongoDB."""
        return self.model_dump(mode='json')

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Subscription":
        """Create from dictionary."""
        return cls(**data)


class CustomerCreate(BaseModel):
    """Schema for creating a new customer."""

    name: str
    email: EmailStr
    phone: Optional[str] = None
    industry: str = "saas"
    metadata: Dict[str, Any] = Field(default_factory=dict)


class CustomerResponse(BaseModel):
    """Schema for customer response."""

    customer_id: str
    name: str
    email: str
    phone: Optional[str]
    industry: str
    created_at: datetime

    @classmethod
    def from_customer(cls, customer: Customer) -> "CustomerResponse":
        """Create response from customer."""
        return cls(
            customer_id=customer.customer_id,
            name=customer.name,
            email=customer.email,
            phone=customer.phone,
            industry=customer.industry,
            created_at=customer.created_at
        )
