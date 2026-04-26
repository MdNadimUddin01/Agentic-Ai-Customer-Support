"""Custom exceptions for the application."""


class BaseAppException(Exception):
    """Base exception for all application exceptions."""

    def __init__(self, message: str, details: dict = None):
        self.message = message
        self.details = details or {}
        super().__init__(self.message)


class DatabaseException(BaseAppException):
    """Exception raised for database errors."""
    pass


class VectorStoreException(BaseAppException):
    """Exception raised for vector store errors."""
    pass


class AgentException(BaseAppException):
    """Exception raised for agent errors."""
    pass


class ToolException(BaseAppException):
    """Exception raised for tool execution errors."""
    pass


class IntegrationException(BaseAppException):
    """Exception raised for external integration errors."""
    pass


class ValidationException(BaseAppException):
    """Exception raised for validation errors."""
    pass


class AuthenticationException(BaseAppException):
    """Exception raised for authentication errors."""
    pass


class RateLimitException(BaseAppException):
    """Exception raised when rate limit is exceeded."""
    pass


class ConversationNotFoundException(BaseAppException):
    """Exception raised when conversation is not found."""
    pass


class CustomerNotFoundException(BaseAppException):
    """Exception raised when customer is not found."""
    pass


class TicketCreationException(BaseAppException):
    """Exception raised when ticket creation fails."""
    pass


class ConfigurationException(BaseAppException):
    """Exception raised for configuration errors."""
    pass
