"""
Data validation module.
"""

from typing import Any, Dict

from pydantic import BaseModel, Field, validator


class AnalysisRequest(BaseModel):
    """Stock analysis request model."""

    symbol: str = Field(..., min_length=1, max_length=10)
    analysis_type: str = Field(
        default="comprehensive",
        regex="^(quick|comprehensive|deep)$",
    )
    include_historical: bool = Field(default=False)
    include_portfolio: bool = Field(default=False)

    @validator("symbol")
    def validate_symbol(cls, v: str) -> str:
        """Validate stock symbol."""
        return v.upper().strip()


class BatchAnalysisRequest(BaseModel):
    """Batch analysis request model."""

    symbols: list = Field(..., min_items=1, max_items=100)
    analysis_type: str = Field(default="quick")

    @validator("symbols")
    def validate_symbols(cls, v: list) -> list:
        """Validate symbols."""
        return [s.upper().strip() for s in v]


class PortfolioRequest(BaseModel):
    """Portfolio analysis request model."""

    stocks: Dict[str, float] = Field(...)  # symbol: weight
    analysis_type: str = Field(default="comprehensive")

    @validator("stocks")
    def validate_portfolio(cls, v: Dict[str, float]) -> Dict[str, float]:
        """Validate portfolio."""
        total_weight = sum(v.values())
        if not (0.99 <= total_weight <= 1.01):
            raise ValueError("Weights must sum to approximately 1.0")
        return {k.upper(): wt for k, wt in v.items()}


class DataLayerRequest(BaseModel):
    """Data layer query request model."""

    symbol: str = Field(..., min_length=1, max_length=10)
    layer: str = Field(..., regex="^(bronze|silver|gold)$")

    @validator("symbol")
    def validate_symbol(cls, v: str) -> str:
        """Validate symbol."""
        return v.upper().strip()


class RequestValidator:
    """Request validation utility."""

    @staticmethod
    def validate_analysis_request(data: Dict[str, Any]) -> AnalysisRequest:
        """Validate analysis request."""
        return AnalysisRequest(**data)

    @staticmethod
    def validate_batch_request(data: Dict[str, Any]) -> BatchAnalysisRequest:
        """Validate batch request."""
        return BatchAnalysisRequest(**data)

    @staticmethod
    def validate_portfolio_request(
        data: Dict[str, Any],
    ) -> PortfolioRequest:
        """Validate portfolio request."""
        return PortfolioRequest(**data)

    @staticmethod
    def validate_data_layer_request(
        data: Dict[str, Any],
    ) -> DataLayerRequest:
        """Validate data layer request."""
        return DataLayerRequest(**data)
