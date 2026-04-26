"""
Application configuration management using Pydantic Settings.
"""
from typing import List, Optional
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field


class Settings(BaseSettings):
    """Main application settings."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="allow"
    )

    # Application
    app_name: str = "AI Customer Support System"
    environment: str = "development"
    debug: bool = True
    log_level: str = "INFO"

    # API
    api_host: str = "0.0.0.0"
    api_port: int = 8000
    api_secret_key: str = "change-this-secret-key-in-production"
    api_token_expire_minutes: int = 1440
    cors_origins: List[str] = [
        "http://localhost:3000",
        "http://localhost:8000",
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ]

    # MongoDB
    mongodb_uri: str = "mongodb://localhost:27017"
    mongodb_db_name: str = "ai_support_system"
    mongodb_max_pool_size: int = 10
    mongodb_min_pool_size: int = 1

    # Redis
    redis_host: str = "localhost"
    redis_port: int = 6379
    redis_db: int = 0
    redis_password: Optional[str] = None

    # Google Gemini
    google_api_key: str = ""
    gemini_model: str = "gemini-1.5-pro"
    gemini_temperature: float = 0.7
    gemini_max_tokens: int = 2048

    # Embeddings
    embedding_model: str = "all-MiniLM-L6-v2"
    embedding_dimension: int = 384

    # Agent Configuration
    max_agent_iterations: int = 5
    agent_timeout: int = 30
    escalation_confidence_threshold: float = 0.6
    max_conversation_history: int = 10

    # Industry
    default_industry: str = "saas"
    supported_industries: List[str] = ["ecommerce", "saas", "telecom"]

    # WhatsApp (Twilio)
    twilio_account_sid: Optional[str] = None
    twilio_auth_token: Optional[str] = None
    twilio_whatsapp_number: Optional[str] = None

    # Stripe
    stripe_api_key: Optional[str] = None
    stripe_webhook_secret: Optional[str] = None

    # CRM
    crm_provider: str = "mock"
    crm_api_key: Optional[str] = None
    crm_api_url: Optional[str] = None

    # Shipping
    shipping_provider: str = "mock"
    fedex_api_key: Optional[str] = None
    ups_api_key: Optional[str] = None

    # Rate Limiting
    rate_limit_per_minute: int = 100
    rate_limit_per_hour: int = 1000

    # Ticket System
    ticket_prefix: str = "T-"
    ticket_notification_email: str = "support@example.com"

    # Feature Flags
    enable_whatsapp: bool = False
    enable_web_chat: bool = True
    enable_real_integrations: bool = False
    enable_vector_search: bool = True

    # Logging
    log_file_path: str = "logs/app.log"
    log_rotation: str = "10 MB"
    log_retention: str = "30 days"

    @property
    def redis_url(self) -> str:
        """Generate Redis URL."""
        if self.redis_password:
            return f"redis://:{self.redis_password}@{self.redis_host}:{self.redis_port}/{self.redis_db}"
        return f"redis://{self.redis_host}:{self.redis_port}/{self.redis_db}"


# Global settings instance
settings = Settings()
