"""Stock market data models."""

from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field


class StockData(BaseModel):
    """Stock market data model."""

    symbol: str = Field(..., description="Stock symbol (e.g., RELIANCE, TCS)")
    price: float = Field(..., description="Current stock price")
    high: float = Field(..., description="Daily high price")
    low: float = Field(..., description="Daily low price")
    open: float = Field(..., description="Opening price")
    close: float = Field(..., description="Closing price")
    volume: int = Field(..., description="Trading volume")
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    
    # Technical indicators
    rsi: Optional[float] = Field(None, description="Relative Strength Index")
    macd: Optional[float] = Field(None, description="MACD value")
    bollinger_upper: Optional[float] = Field(None, description="Bollinger Bands upper")
    bollinger_lower: Optional[float] = Field(None, description="Bollinger Bands lower")
    sma_20: Optional[float] = Field(None, description="20-day Simple Moving Average")
    sma_50: Optional[float] = Field(None, description="50-day Simple Moving Average")
    
    class Config:
        json_schema_extra = {
            "example": {
                "symbol": "RELIANCE",
                "price": 2850.50,
                "high": 2890.00,
                "low": 2820.00,
                "open": 2835.00,
                "close": 2850.50,
                "volume": 5000000,
                "rsi": 65.5,
                "macd": 2.35,
            }
        }


class StockPrediction(BaseModel):
    """Stock price prediction model."""

    symbol: str = Field(..., description="Stock symbol")
    predicted_price: float = Field(..., description="Predicted price target")
    confidence_score: float = Field(..., ge=0, le=1, description="Prediction confidence (0-1)")
    timeframe_days: int = Field(..., description="Prediction timeframe in days")
    bull_probability: float = Field(..., ge=0, le=1, description="Bullish probability")
    bear_probability: float = Field(..., ge=0, le=1, description="Bearish probability")
    neutral_probability: float = Field(..., ge=0, le=1, description="Neutral probability")
    
    # Supporting factors
    technical_score: Optional[float] = Field(None, description="Technical analysis score")
    sentiment_score: Optional[float] = Field(None, description="Sentiment analysis score")
    geopolitical_score: Optional[float] = Field(None, description="Geopolitical risk score")
    
    # Risk assessment
    risk_level: str = Field(..., description="Risk level: LOW, MEDIUM, HIGH")
    risk_factors: List[str] = Field(default=[], description="Identified risk factors")
    
    # Metadata
    analysis_timestamp: datetime = Field(default_factory=datetime.utcnow)
    model_version: str = Field(..., description="Model version used")
    
    class Config:
        json_schema_extra = {
            "example": {
                "symbol": "RELIANCE",
                "predicted_price": 2950.00,
                "confidence_score": 0.82,
                "timeframe_days": 60,
                "bull_probability": 0.73,
                "bear_probability": 0.22,
                "neutral_probability": 0.05,
                "technical_score": 0.75,
                "sentiment_score": 0.68,
                "geopolitical_score": 0.45,
                "risk_level": "MEDIUM",
                "risk_factors": ["Market Volatility", "Geopolitical Risk"],
                "model_version": "v1.0.0",
            }
        }


class AnalysisResult(BaseModel):
    """Complete analysis result combining all agent outputs."""

    request_id: str = Field(..., description="Unique request identifier")
    symbol: str = Field(..., description="Stock symbol analyzed")
    
    # Agent outputs
    stock_analysis: Optional[dict] = Field(None, description="Stock analyst agent output")
    geopolitical_analysis: Optional[dict] = Field(None, description="Geopolitical analyst output")
    news_analysis: Optional[dict] = Field(None, description="News analyst output")
    
    # Final prediction
    prediction: StockPrediction = Field(..., description="Final prediction")
    
    # Summary
    executive_summary: str = Field(..., description="Executive summary of analysis")
    key_insights: List[str] = Field(default=[], description="Key insights from analysis")
    
    # Metadata
    total_execution_time_ms: float = Field(..., description="Total execution time in milliseconds")
    analysis_timestamp: datetime = Field(default_factory=datetime.utcnow)
    
    class Config:
        json_schema_extra = {
            "example": {
                "request_id": "req_abc123",
                "symbol": "RELIANCE",
                "prediction": {
                    "symbol": "RELIANCE",
                    "predicted_price": 2950.00,
                    "confidence_score": 0.82,
                    "timeframe_days": 60,
                    "bull_probability": 0.73,
                    "bear_probability": 0.22,
                    "neutral_probability": 0.05,
                    "risk_level": "MEDIUM",
                },
                "executive_summary": "RELIANCE shows bullish momentum...",
                "total_execution_time_ms": 5230.50,
            }
        }
