"""Application constants and enumerations."""
from enum import Enum


class ConversationStatus(str, Enum):
    """Conversation status types."""
    ACTIVE = "active"
    RESOLVED = "resolved"
    ESCALATED = "escalated"
    CLOSED = "closed"


class MessageRole(str, Enum):
    """Message role types."""
    USER = "user"
    ASSISTANT = "assistant"
    SYSTEM = "system"
    TOOL = "tool"


class Channel(str, Enum):
    """Communication channels."""
    WEB = "web"
    WHATSAPP = "whatsapp"
    API = "api"
    SMS = "sms"


class TicketStatus(str, Enum):
    """Ticket status types."""
    OPEN = "open"
    ASSIGNED = "assigned"
    IN_PROGRESS = "in_progress"
    WAITING_CUSTOMER = "waiting_customer"
    RESOLVED = "resolved"
    CLOSED = "closed"


class TicketCategory(str, Enum):
    """Ticket category types."""
    ORDER = "order"
    PAYMENT = "payment"
    TECHNICAL = "technical"
    ACCOUNT = "account"
    BILLING = "billing"
    GENERAL = "general"


class AgentType(str, Enum):
    """Agent types."""
    ORCHESTRATOR = "orchestrator"
    TECHNICAL = "technical"
    ACCOUNT = "account"
    ORDER = "order"
    PAYMENT = "payment"
    QUERY = "query"
    ESCALATION = "escalation"


class IntentCategory(str, Enum):
    """Intent categories for routing."""
    TECHNICAL_SUPPORT = "technical_support"
    ACCOUNT_MANAGEMENT = "account_management"
    ORDER_TRACKING = "order_tracking"
    PAYMENT_ISSUES = "payment_issues"
    BILLING_QUERY = "billing_query"
    GENERAL_QUERY = "general_query"
    ESCALATION = "escalation"


class OrderStatus(str, Enum):
    """Order status types."""
    PENDING = "pending"
    CONFIRMED = "confirmed"
    PROCESSING = "processing"
    SHIPPED = "shipped"
    DELIVERED = "delivered"
    CANCELLED = "cancelled"
    REFUNDED = "refunded"


class PaymentStatus(str, Enum):
    """Payment status types."""
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    REFUNDED = "refunded"
    CANCELLED = "cancelled"


class SubscriptionPlan(str, Enum):
    """SaaS subscription plans."""
    FREE = "free"
    BASIC = "basic"
    PRO = "pro"
    ENTERPRISE = "enterprise"


class SubscriptionStatus(str, Enum):
    """Subscription status types."""
    ACTIVE = "active"
    INACTIVE = "inactive"
    CANCELLED = "cancelled"
    SUSPENDED = "suspended"
    TRIAL = "trial"


# Collection names
COLLECTION_CONVERSATIONS = "conversations"
COLLECTION_CUSTOMERS = "customers"
COLLECTION_TICKETS = "tickets"
COLLECTION_KNOWLEDGE_BASE = "knowledge_base"
COLLECTION_ORDERS = "orders"
COLLECTION_SUBSCRIPTIONS = "subscriptions"

# Agent configuration
DEFAULT_AGENT_TEMPERATURE = 0.7
MAX_TOOL_ITERATIONS = 5
AGENT_RESPONSE_TIMEOUT = 30

# Vector search configuration
VECTOR_SEARCH_TOP_K = 5
VECTOR_SEARCH_MIN_SCORE = 0.7

# Cache TTL (seconds)
CACHE_TTL_CONVERSATION = 3600  # 1 hour
CACHE_TTL_CUSTOMER = 7200  # 2 hours
CACHE_TTL_KNOWLEDGE = 86400  # 24 hours

# Rate limiting
DEFAULT_RATE_LIMIT = "100/minute"
BURST_RATE_LIMIT = "20/second"
