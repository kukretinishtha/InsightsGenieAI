"""Base Pydantic models."""

from datetime import datetime
from typing import Any, Optional
from pydantic import BaseModel as PydanticBaseModel, Field


class BaseModel(PydanticBaseModel):
    """Base model with common configurations."""
    
    class Config:
        """Pydantic configuration."""
        json_schema_extra = {
            "example": {}
        }
        populate_by_name = True
        arbitrary_types_allowed = True


class TimestampedModel(BaseModel):
    """Model with timestamp fields."""
    
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
