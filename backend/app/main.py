"""InsightGenie AI FastAPI application."""

from fastapi import FastAPI
from fastapi.responses import JSONResponse
import logging
from app.config import get_settings
from app.utils.logger import setup_logging
from app.middleware import setup_cors, setup_error_handlers, RequestLoggingMiddleware
from app.api.v1 import router as api_v1_router

# Setup logging
setup_logging()
logger = logging.getLogger(__name__)

# Initialize FastAPI application
settings = get_settings()
app = FastAPI(
    title=settings.APP_NAME,
    description="AI-powered stock market prediction system",
    version=settings.APP_VERSION,
    docs_url="/docs",
    openapi_url="/openapi.json"
)

# Add middleware
setup_cors(app)
setup_error_handlers(app)
app.add_middleware(RequestLoggingMiddleware)

# Include routers
app.include_router(api_v1_router)


@app.on_event("startup")
async def startup_event():
    """Handle application startup."""
    logger.info(f"Starting {settings.APP_NAME} v{settings.APP_VERSION}")
    logger.info(f"Environment: {settings.ENVIRONMENT}")
    logger.info(f"Debug mode: {settings.DEBUG}")


@app.on_event("shutdown")
async def shutdown_event():
    """Handle application shutdown."""
    logger.info(f"Shutting down {settings.APP_NAME}")


@app.get("/", response_model=dict)
async def root():
    """Root endpoint."""
    return {
        "name": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "status": "operational"
    }


@app.get("/health")
async def health():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "service": settings.APP_NAME
    }


if __name__ == "__main__":
    import uvicorn
    
    uvicorn.run(
        "app.main:app",
        host=settings.HOST,
        port=settings.PORT,
        workers=settings.WORKERS,
        reload=settings.DEBUG,
        log_level=settings.LOG_LEVEL.lower()
    )
