"""Core package exports."""
from .database import (
    db_manager,
    get_db,
    get_collection,
    connect_db,
    disconnect_db,
    DatabaseManager
)
from .vector_store import (
    vector_store,
    search_knowledge_base,
    add_knowledge_entry,
    VectorStore
)
from .exceptions import *
from .constants import *

__all__ = [
    # Database
    "db_manager",
    "get_db",
    "get_collection",
    "connect_db",
    "disconnect_db",
    "DatabaseManager",
    # Vector Store
    "vector_store",
    "search_knowledge_base",
    "add_knowledge_entry",
    "VectorStore",
]
