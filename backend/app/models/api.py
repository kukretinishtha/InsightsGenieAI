"""API response models."""

from typing import Any, Optional, Generic, TypeVar, List
from pydantic import Field
from .base import BaseModel

T = TypeVar("T")


class APIResponse(BaseModel, Generic[T]):
    """Standard API response wrapper."""
    
    success: bool = Field(..., description="Whether request was successful")
    message: str = Field(..., description="Response message")
    data: Optional[T] = Field(None, description="Response data")
    request_id: Optional[str] = Field(None, description="Request ID for tracking")
    timestamp: Optional[str] = Field(None, description="Response timestamp")


class ErrorResponse(BaseModel):
    """Error response model."""
    
    error: str = Field(..., description="Error code")
    message: str = Field(..., description="Error message")
    details: Optional[dict] = Field(None, description="Error details")
    request_id: Optional[str] = Field(None, description="Request ID for tracking")


class PaginatedResponse(BaseModel, Generic[T]):
    """Paginated response wrapper."""
    
    items: List[T] = Field(..., description="List of items")
    total: int = Field(..., description="Total number of items")
    page: int = Field(..., ge=1, description="Current page number")
    page_size: int = Field(..., gt=0, description="Items per page")
    pages: int = Field(..., description="Total number of pages")
    
    @property
    def has_next(self) -> bool:
        """Check if there's a next page."""
        return self.page < self.pages
    
    @property
    def has_previous(self) -> bool:
        """Check if there's a previous page."""
        return self.page > 1
