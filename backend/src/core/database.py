"""MongoDB database connection and management."""
from typing import Optional
from pymongo import MongoClient, ASCENDING, DESCENDING
from pymongo.database import Database
from pymongo.collection import Collection
from pymongo.errors import ConnectionFailure, OperationFailure
from config import settings, logger
from src.core.exceptions import DatabaseException
from src.core.constants import (
    COLLECTION_CONVERSATIONS,
    COLLECTION_CUSTOMERS,
    COLLECTION_TICKETS,
    COLLECTION_KNOWLEDGE_BASE,
    COLLECTION_ORDERS,
    COLLECTION_SUBSCRIPTIONS,
)


class DatabaseManager:
    """Manages MongoDB connections and operations."""

    def __init__(self):
        """Initialize database manager."""
        self._client: Optional[MongoClient] = None
        self._db: Optional[Database] = None

    def connect(self) -> None:
        """Establish connection to MongoDB."""
        try:
            logger.info(f"Connecting to MongoDB: {settings.mongodb_uri}")

            self._client = MongoClient(
                settings.mongodb_uri,
                maxPoolSize=settings.mongodb_max_pool_size,
                minPoolSize=settings.mongodb_min_pool_size,
                serverSelectionTimeoutMS=5000,
            )

            # Test connection
            self._client.admin.command('ping')

            self._db = self._client[settings.mongodb_db_name]
            logger.info(f"Connected to database: {settings.mongodb_db_name}")

            # Create indexes
            self._create_indexes()

        except ConnectionFailure as e:
            logger.error(f"Failed to connect to MongoDB: {e}")
            raise DatabaseException(f"Database connection failed: {e}")
        except Exception as e:
            logger.error(f"Unexpected error connecting to MongoDB: {e}")
            raise DatabaseException(f"Database error: {e}")

    def disconnect(self) -> None:
        """Close MongoDB connection."""
        if self._client:
            self._client.close()
            logger.info("Disconnected from MongoDB")

    def _create_indexes(self) -> None:
        """Create database indexes for optimal performance."""
        try:
            logger.info("Creating database indexes...")

            # Conversations indexes
            conversations = self.get_collection(COLLECTION_CONVERSATIONS)
            conversations.create_index([("conversation_id", ASCENDING)], unique=True)
            conversations.create_index([("customer_id", ASCENDING)])
            conversations.create_index([("status", ASCENDING)])
            conversations.create_index([("created_at", DESCENDING)])
            conversations.create_index([("channel", ASCENDING)])

            # Customers indexes
            customers = self.get_collection(COLLECTION_CUSTOMERS)
            customers.create_index([("customer_id", ASCENDING)], unique=True)
            self._ensure_unique_customer_contact_indexes(customers)

            # Tickets indexes
            tickets = self.get_collection(COLLECTION_TICKETS)
            tickets.create_index([("ticket_id", ASCENDING)], unique=True)
            tickets.create_index([("customer_id", ASCENDING)])
            tickets.create_index([("conversation_id", ASCENDING)])
            tickets.create_index([("status", ASCENDING)])
            tickets.create_index([("priority", ASCENDING)])
            tickets.create_index([("created_at", DESCENDING)])
            tickets.create_index([("metadata.confidence_score", DESCENDING)])
            tickets.create_index([("metadata.source_intent", ASCENDING)])
            tickets.create_index([("metadata.escalation_reason", ASCENDING)])

            # Knowledge base indexes
            knowledge_base = self.get_collection(COLLECTION_KNOWLEDGE_BASE)
            knowledge_base.create_index([("metadata.category", ASCENDING)])
            knowledge_base.create_index([("metadata.industry", ASCENDING)])

            # Vector search index (requires MongoDB Atlas or manual setup)
            # This is a placeholder - actual vector search index created via Atlas UI or mongosh
            try:
                # For local development, we'll create a text index
                knowledge_base.create_index([("content", "text")])
            except OperationFailure:
                logger.warning("Vector search index creation skipped (requires MongoDB Atlas)")

            # Orders indexes
            orders = self.get_collection(COLLECTION_ORDERS)
            orders.create_index([("order_id", ASCENDING)], unique=True)
            orders.create_index([("customer_id", ASCENDING)])
            orders.create_index([("status", ASCENDING)])
            orders.create_index([("tracking_number", ASCENDING)])

            # Subscriptions indexes
            subscriptions = self.get_collection(COLLECTION_SUBSCRIPTIONS)
            subscriptions.create_index([("customer_id", ASCENDING)], unique=True)
            subscriptions.create_index([("status", ASCENDING)])
            subscriptions.create_index([("plan", ASCENDING)])

            logger.info("Database indexes created successfully")

        except Exception as e:
            logger.error(f"Error creating indexes: {e}")
            raise DatabaseException(f"Index creation failed: {e}")

    def _ensure_unique_customer_contact_indexes(self, customers: Collection) -> None:
        """Ensure customer email/phone indexes are unique, migrating old indexes if needed."""
        existing_indexes = list(customers.list_indexes())

        def find_index_by_key_pattern(key_pattern: dict) -> Optional[dict]:
            for idx in existing_indexes:
                if dict(idx.get("key", {})) == key_pattern:
                    return idx
            return None

        def ensure_unique_index(key_pattern: dict, index_name: str, *, sparse: bool = False) -> None:
            existing = find_index_by_key_pattern(key_pattern)

            # If a valid unique index already exists for this key pattern, keep it as-is.
            if existing and existing.get("unique", False):
                existing_sparse = bool(existing.get("sparse", False))
                if not sparse or existing_sparse:
                    return

            # If index exists but is not unique, drop and recreate as unique.
            if existing:
                old_name = existing.get("name")
                if old_name:
                    logger.info(f"Dropping customer index '{old_name}' to recreate with required options")
                    customers.drop_index(old_name)

            # Handle name collisions from prior runs with different key/options.
            for idx in existing_indexes:
                if idx.get("name") == index_name and dict(idx.get("key", {})) != key_pattern:
                    customers.drop_index(index_name)
                    break

            customers.create_index(
                list(key_pattern.items()),
                name=index_name,
                unique=True,
                sparse=sparse
            )

        ensure_unique_index({"email": ASCENDING}, "customer_email_unique_idx")
        ensure_unique_index({"phone": ASCENDING}, "customer_phone_unique_idx", sparse=True)

    @property
    def db(self) -> Database:
        """Get database instance."""
        if self._db is None:
            raise DatabaseException("Database not connected. Call connect() first.")
        return self._db

    def get_collection(self, collection_name: str) -> Collection:
        """
        Get a collection by name.

        Args:
            collection_name: Name of the collection

        Returns:
            Collection instance
        """
        return self.db[collection_name]

    def health_check(self) -> bool:
        """
        Check database health.

        Returns:
            True if database is healthy, False otherwise
        """
        try:
            if not self._client:
                return False
            self._client.admin.command('ping')
            return True
        except Exception as e:
            logger.error(f"Health check failed: {e}")
            return False


# Global database manager instance
db_manager = DatabaseManager()


# Convenience functions
def get_db() -> Database:
    """Get database instance."""
    return db_manager.db


def get_collection(collection_name: str) -> Collection:
    """Get a collection by name."""
    return db_manager.get_collection(collection_name)


def connect_db() -> None:
    """Connect to database."""
    db_manager.connect()


def disconnect_db() -> None:
    """Disconnect from database."""
    db_manager.disconnect()
