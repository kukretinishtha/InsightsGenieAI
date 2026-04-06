"""Health check endpoints."""

from fastapi import APIRouter, Depends
from app.models.api import APIResponse
from datetime import datetime
from app.utils.logger import get_logger

logger = get_logger(__name__)

router = APIRouter()


@router.get("/check", response_model=APIResponse)
async def health_check():
    """Check application health status."""
    logger.info("Health check requested")
    
    return APIResponse(
        success=True,
        message="Application is healthy",
        data={
            "status": "healthy",
            "timestamp": datetime.utcnow().isoformat()
        }
    )


@router.get("/status", response_model=APIResponse)
async def status():
    """Get detailed application status."""
    logger.info("Status check requested")
    
    return APIResponse(
        success=True,
        message="Status retrieved successfully",
        data={
            "status": "operational",
            "version": "1.0.0",
            "timestamp": datetime.utcnow().isoformat()
        }
    )
