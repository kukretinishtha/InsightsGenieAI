"""Response data models."""

from typing import Optional, Any, Dict
from pydantic import BaseModel, Field
from datetime import datetime


class APIResponse(BaseModel):
    """Standard API response."""

    success: bool = Field(..., description="Whether request was successful")
    data: Optional[Any] = Field(None, description="Response data")
    message: Optional[str] = Field(None, description="Response message")
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    request_id: Optional[str] = Field(None, description="Request identifier")
    
    class Config:
        json_schema_extra = {
            "example": {
                "success": True,
                "data": {"symbol": "RELIANCE", "price": 2850.50},
                "message": "Analysis completed successfully",
                "timestamp": "2024-01-15T10:30:00Z",
                "request_id": "req_abc123",
            }
        }


class ErrorResponse(BaseModel):
    """Error response model."""

    success: bool = Field(default=False)
    error: str = Field(..., description="Error message")
    error_code: str = Field(..., description="Error code")
    details: Optional[Dict[str, Any]] = Field(None, description="Error details")
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    request_id: Optional[str] = Field(None, description="Request identifier")
    
    class Config:
        json_schema_extra = {
            "example": {
                "success": False,
                "error": "Invalid stock symbol",
                "error_code": "INVALID_SYMBOL",
                "details": {"symbol": "INVALID"},
                "timestamp": "2024-01-15T10:30:00Z",
                "request_id": "req_abc123",
            }
        }


class HealthResponse(BaseModel):
    """Health check response."""

    status: str = Field(..., description="Health status")
    version: str = Field(..., description="API version")
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    services: Optional[Dict[str, str]] = Field(None, description="Service health status")
    
    class Config:
        json_schema_extra = {
            "example": {
                "status": "healthy",
                "version": "1.0.0",
                "timestamp": "2024-01-15T10:30:00Z",
                "services": {
                    "database": "healthy",
                    "redis": "healthy",
                    "genie_api": "healthy",
                },
            }
        }
