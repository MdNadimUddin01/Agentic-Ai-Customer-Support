"""FastAPI application main entry point."""
from contextlib import asynccontextmanager
from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from config import settings, logger
from src.core.database import connect_db, disconnect_db, db_manager
from src.api.routes import auth, chat, webhook, admin


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Application lifespan manager.
    Handles startup and shutdown events.
    """
    # Startup
    logger.info("Starting AI Customer Support System...")
    logger.info(f"Environment: {settings.environment}")
    logger.info(f"API Host: {settings.api_host}:{settings.api_port}")

    # Connect to database
    try:
        connect_db()
        logger.info("Database connected successfully")
    except Exception as e:
        logger.error(f"Failed to connect to database: {e}")
        raise

    logger.info("Application started successfully")

    yield

    # Shutdown
    logger.info("Shutting down application...")
    try:
        disconnect_db()
        logger.info("Database disconnected")
    except Exception as e:
        logger.error(f"Error during shutdown: {e}")


# Create FastAPI application
app = FastAPI(
    title=settings.app_name,
    description="AI-powered customer support system with LangChain agents",
    version="0.1.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth.router, prefix="/api/auth", tags=["Authentication"])
app.include_router(chat.router, prefix="/api", tags=["Chat"])
app.include_router(webhook.router, prefix="/api/webhook", tags=["Webhooks"])
app.include_router(
    admin.router,
    prefix="/api/admin",
    tags=["Admin"],
    dependencies=[Depends(admin.require_admin)]
)


@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "message": "AI Customer Support System API",
        "version": "0.1.0",
        "status": "online",
        "docs": "/docs"
    }


@app.get("/api/health")
async def health_check():
    """
    Health check endpoint.

    Returns:
        Health status
    """
    # Check database health
    db_healthy = db_manager.health_check()

    if not db_healthy:
        return JSONResponse(
            status_code=503,
            content={
                "status": "unhealthy",
                "database": "disconnected"
            }
        )

    return {
        "status": "healthy",
        "database": "connected",
        "environment": settings.environment
    }


@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    """Global exception handler."""
    logger.error(f"Unhandled exception: {exc}")
    return JSONResponse(
        status_code=500,
        content={
            "error": "Internal server error",
            "message": str(exc) if settings.debug else "An error occurred"
        }
    )


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "src.api.main:app",
        host=settings.api_host,
        port=settings.api_port,
        reload=settings.debug,
        log_level=settings.log_level.lower()
    )
