"""
Database initialization script.

Creates necessary indexes and sets up MongoDB collections.
"""
import sys
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from config import logger, settings
from src.core.database import connect_db, disconnect_db, db_manager


def main():
    """Initialize database."""
    logger.info("=" * 60)
    logger.info("AI Customer Support System - Database Initialization")
    logger.info("=" * 60)
    logger.info(f"MongoDB URI: {settings.mongodb_uri}")
    logger.info(f"Database: {settings.mongodb_db_name}")
    logger.info("")

    try:
        # Connect to database
        logger.info("Connecting to MongoDB...")
        connect_db()
        logger.info("✓ Connected successfully")
        logger.info("")

        # Create indexes (done automatically in connect_db)
        logger.info("Creating indexes...")
        logger.info("✓ Indexes created successfully")
        logger.info("")

        # Verify collections
        logger.info("Verifying collections...")
        db = db_manager.db
        collections = db.list_collection_names()

        logger.info(f"Available collections: {', '.join(collections) if collections else 'None (will be created on first insert)'}")
        logger.info("")

        # Health check
        logger.info("Running health check...")
        if db_manager.health_check():
            logger.info("✓ Database is healthy")
        else:
            logger.warning("⚠ Database health check failed")

        logger.info("")
        logger.info("=" * 60)
        logger.info("Database initialization completed successfully!")
        logger.info("=" * 60)
        logger.info("")
        logger.info("Next steps:")
        logger.info("1. Run 'python scripts/seed_data.py' to add sample data")
        logger.info("2. Start the API: 'uvicorn src.api.main:app --reload'")

    except Exception as e:
        logger.error(f"Error initializing database: {e}")
        sys.exit(1)

    finally:
        disconnect_db()


if __name__ == "__main__":
    main()
