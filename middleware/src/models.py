"""
Response and error models module.
"""

from typing import Any, Dict, Optional

from pydantic import BaseModel


class APIResponse(BaseModel):
    """Standard API response model."""

    success: bool
    message: str
    data: Optional[Any] = None
    error: Optional[str] = None
    request_id: Optional[str] = None

    class Config:
        """Pydantic config."""

        json_schema_extra = {
            "example": {
                "success": True,
                "message": "Request processed successfully",
                "data": {"symbol": "RELIANCE", "price": 2750.0},
                "request_id": "550e8400-e29b-41d4-a716-446655440000",
            }
        }


class ErrorResponse(BaseModel):
    """Error response model."""

    success: bool = False
    message: str
    error: str
    details: Optional[Dict[str, Any]] = None

    class Config:
        """Pydantic config."""

        json_schema_extra = {
            "example": {
                "success": False,
                "message": "Request failed",
                "error": "Invalid symbol",
                "details": {"symbol": "INVALID"},
            }
        }


class JobStatus(BaseModel):
    """Job status model."""

    request_id: str
    status: str  # pending, processing, completed, failed
    progress: float  # 0-100
    result: Optional[Any] = None
    error: Optional[str] = None
    created_at: str
    updated_at: str

    class Config:
        """Pydantic config."""

        json_schema_extra = {
            "example": {
                "request_id": "550e8400-e29b-41d4-a716-446655440000",
                "status": "completed",
                "progress": 100.0,
                "result": {"symbol": "RELIANCE", "recommendation": "BUY"},
                "created_at": "2026-04-06T10:00:00Z",
                "updated_at": "2026-04-06T10:02:15Z",
            }
        }


class HealthCheck(BaseModel):
    """Health check response model."""

    status: str
    version: str
    timestamp: str
    services: Dict[str, str]  # service_name: status

    class Config:
        """Pydantic config."""

        json_schema_extra = {
            "example": {
                "status": "healthy",
                "version": "1.0.0",
                "timestamp": "2026-04-06T10:00:00Z",
                "services": {
                    "backend": "healthy",
                    "cache": "healthy",
                    "database": "healthy",
                },
            }
        }
