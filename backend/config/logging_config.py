"""
Logging configuration using Loguru.
"""
import sys
from pathlib import Path
from loguru import logger
from config.settings import settings


def setup_logging():
    """Configure login logger with file and console handlers."""

    # Remove default handler
    logger.remove()

    # Console handler with colors
    logger.add(
        sys.stdout,
        format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>",
        level=settings.log_level,
        colorize=True
    )

    # Create logs directory if it doesn't exist
    log_dir = Path(settings.log_file_path).parent
    log_dir.mkdir(parents=True, exist_ok=True)

    # File handler with rotation
    logger.add(
        settings.log_file_path,
        rotation=settings.log_rotation,
        retention=settings.log_retention,
        compression="zip",
        format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} - {message}",
        level=settings.log_level,
        enqueue=True  # Async logging
    )

    # Error-specific file
    logger.add(
        log_dir / "errors.log",
        rotation=settings.log_rotation,
        retention=settings.log_retention,
        compression="zip",
        format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} - {message}",
        level="ERROR",
        enqueue=True
    )

    logger.info(f"Logging initialized - Level: {settings.log_level}")
    logger.info(f"Log file: {settings.log_file_path}")
    logger.info(f"Environment: {settings.environment}")


# Initialize logging when module is imported
setup_logging()
