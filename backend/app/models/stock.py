"""Stock market data models."""

from datetime import datetime
from typing import Optional, List
from decimal import Decimal
from pydantic import Field
from .base import BaseModel, TimestampedModel


class MarketData(BaseModel):
    """Market data for a stock."""
    
    symbol: str = Field(..., description="Stock symbol (e.g., AAPL)")
    price: float = Field(..., description="Current stock price")
    previous_close: float = Field(..., description="Previous day closing price")
    open_price: float = Field(..., description="Opening price")
    high: float = Field(..., description="Day high")
    low: float = Field(..., description="Day low")
    volume: int = Field(..., description="Trading volume")
    market_cap: Optional[float] = Field(None, description="Market capitalization")
    pe_ratio: Optional[float] = Field(None, description="Price-to-earnings ratio")
    dividend_yield: Optional[float] = Field(None, description="Dividend yield percentage")
    timestamp: datetime = Field(default_factory=datetime.utcnow)


class StockPrediction(TimestampedModel):
    """Stock price prediction model."""
    
    symbol: str = Field(..., description="Stock symbol")
    predicted_price: float = Field(..., description="Predicted stock price")
    confidence_score: float = Field(..., ge=0, le=1, description="Confidence score 0-1")
    prediction_horizon_days: int = Field(..., gt=0, description="Number of days ahead")
    prediction_date: datetime = Field(...)
    factors: List[str] = Field(default_factory=list, description="Key factors influencing prediction")
    model_version: str = Field(..., description="Version of prediction model used")
    recommendation: str = Field(..., description="Buy/Sell/Hold recommendation")


class StockAnalysis(TimestampedModel):
    """Detailed stock analysis model."""
    
    symbol: str = Field(..., description="Stock symbol")
    market_data: MarketData = Field(..., description="Current market data")
    prediction: StockPrediction = Field(..., description="Price prediction")
    technical_signals: dict = Field(default_factory=dict, description="Technical analysis signals")
    fundamental_scores: dict = Field(default_factory=dict, description="Fundamental analysis scores")
    sentiment_score: float = Field(default=0.5, ge=0, le=1, description="Sentiment analysis score")
    analysis_report: Optional[str] = Field(None, description="Detailed analysis report")
