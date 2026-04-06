"""Data layer models for Bronze, Silver, and Gold layers."""

from datetime import datetime
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field


# ============================================================================
# BRONZE LAYER - Raw Data (minimal transformation)
# ============================================================================

class BronzeStockData(BaseModel):
    """Raw stock data from NSE/BSE."""
    
    symbol: str
    timestamp: datetime
    exchange: str  # NSE or BSE
    
    # Price data
    open_price: float
    high_price: float
    low_price: float
    close_price: float
    last_traded_price: float
    
    # Volume data
    volume: int
    turnover: float  # In lakhs or crores
    
    # Additional raw data
    previous_close: float
    bid_price: Optional[float] = None
    ask_price: Optional[float] = None
    bid_quantity: Optional[int] = None
    ask_quantity: Optional[int] = None
    
    # Raw indicators (if available from source)
    fifty_two_week_high: Optional[float] = None
    fifty_two_week_low: Optional[float] = None
    
    # Metadata
    market_status: str  # "open", "closed", "pre-market"
    source: str  # "nse_api", "bse_api", "data_provider"
    raw_data: Optional[Dict[str, Any]] = None  # Store raw JSON response
    
    class Config:
        json_schema_extra = {
            "example": {
                "symbol": "RELIANCE",
                "timestamp": "2026-04-06T15:30:00Z",
                "exchange": "NSE",
                "open_price": 2850.50,
                "high_price": 2890.00,
                "low_price": 2840.00,
                "close_price": 2875.25,
                "last_traded_price": 2875.25,
                "volume": 5000000,
                "turnover": 1500000.00,
                "previous_close": 2850.00
            }
        }


class BronzeNewsData(BaseModel):
    """Raw news data from news sources."""
    
    article_id: str
    timestamp: datetime
    source: str  # "reuters", "bloomberg", "economictimes", etc.
    
    # Content
    headline: str
    summary: str
    full_text: Optional[str] = None
    
    # Metadata
    url: str
    author: Optional[str] = None
    category: Optional[str] = None
    
    # Raw data
    raw_data: Optional[Dict[str, Any]] = None


class BronzeGeoPoliticalData(BaseModel):
    """Raw geopolitical event data."""
    
    event_id: str
    timestamp: datetime
    
    # Event details
    country: str
    region: Optional[str] = None
    event_type: str  # "trade_agreement", "political_change", "conflict", "policy_change"
    severity: str  # "low", "medium", "high", "critical"
    
    # Description
    description: str
    affected_countries: List[str]
    
    # Raw data
    raw_data: Optional[Dict[str, Any]] = None


# ============================================================================
# SILVER LAYER - Cleaned & Processed Data
# ============================================================================

class SilverStockData(BaseModel):
    """Cleaned and enriched stock data."""
    
    symbol: str
    timestamp: datetime
    exchange: str
    
    # Cleaned price data
    open_price: float
    high_price: float
    low_price: float
    close_price: float
    
    # Volume data
    volume: int
    turnover: float
    
    # Calculated fields
    price_change: float  # Close - Previous Close
    price_change_percent: float
    
    # Technical calculations (simple)
    sma_5: Optional[float] = None  # 5-day simple moving average
    sma_20: Optional[float] = None  # 20-day simple moving average
    ema_12: Optional[float] = None  # 12-day exponential moving average
    ema_26: Optional[float] = None  # 26-day exponential moving average
    
    # Volatility
    volatility_5d: Optional[float] = None
    volatility_20d: Optional[float] = None
    
    # Volume indicators
    sma_volume_5: Optional[int] = None
    volume_change_percent: Optional[float] = None
    
    # Data quality
    data_quality_score: float = Field(ge=0.0, le=1.0)  # 0-1 score
    missing_fields: List[str] = []
    
    class Config:
        json_schema_extra = {
            "example": {
                "symbol": "RELIANCE",
                "timestamp": "2026-04-06T15:30:00Z",
                "exchange": "NSE",
                "open_price": 2850.50,
                "high_price": 2890.00,
                "low_price": 2840.00,
                "close_price": 2875.25,
                "volume": 5000000,
                "turnover": 1500000.00,
                "price_change": 25.25,
                "price_change_percent": 0.94,
                "sma_20": 2860.00,
                "data_quality_score": 0.95
            }
        }


class SilverNewsData(BaseModel):
    """Processed news data with sentiment and entities."""
    
    article_id: str
    timestamp: datetime
    source: str
    
    # Content (cleaned)
    headline: str
    summary: str
    
    # NLP Processing
    sentiment_score: float = Field(ge=-1.0, le=1.0)  # -1 (negative) to 1 (positive)
    sentiment_label: str  # "positive", "negative", "neutral"
    
    # Entity extraction
    mentioned_stocks: List[str] = []  # Extracted stock symbols
    mentioned_countries: List[str] = []
    mentioned_companies: List[str] = []
    
    # Topics/Categories
    topics: List[str] = []  # e.g., ["earnings", "merger", "regulation"]
    
    # Relevance to Indian market
    india_relevance_score: float = Field(ge=0.0, le=1.0)
    market_impact_potential: str  # "high", "medium", "low"
    
    # Processing metadata
    language: str = "en"
    processed_at: datetime


class SilverGeoPoliticalData(BaseModel):
    """Processed geopolitical data with impact assessment."""
    
    event_id: str
    timestamp: datetime
    
    # Event details
    country: str
    region: Optional[str] = None
    event_type: str
    severity: str
    
    # Impact assessment
    trade_impact_score: float = Field(ge=0.0, le=1.0)
    market_impact_score: float = Field(ge=0.0, le=1.0)
    
    # Related information
    affected_sectors: List[str]  # e.g., ["IT", "Pharma", "Auto"]
    affected_stocks: List[str]  # NSE symbols likely affected
    
    # Trend information
    is_ongoing: bool
    expected_duration_days: Optional[int] = None
    resolution_confidence: float = Field(ge=0.0, le=1.0)


# ============================================================================
# GOLD LAYER - Aggregated & Feature-Engineered Data
# ============================================================================

class TechnicalIndicators(BaseModel):
    """Comprehensive technical analysis indicators."""
    
    symbol: str
    date: datetime
    
    # Trend indicators
    sma_50: Optional[float] = None
    sma_200: Optional[float] = None
    ema_12: Optional[float] = None
    ema_26: Optional[float] = None
    
    # Momentum indicators
    rsi_14: Optional[float] = Field(None, ge=0, le=100)  # Relative Strength Index
    macd_line: Optional[float] = None
    macd_signal: Optional[float] = None
    macd_histogram: Optional[float] = None
    
    # Volatility indicators
    bollinger_upper: Optional[float] = None
    bollinger_middle: Optional[float] = None
    bollinger_lower: Optional[float] = None
    atr_14: Optional[float] = None  # Average True Range
    
    # Volume indicators
    obv: Optional[float] = None  # On-Balance Volume
    cmf: Optional[float] = None  # Chaikin Money Flow
    
    # Support and Resistance
    support_level_1: Optional[float] = None
    support_level_2: Optional[float] = None
    resistance_level_1: Optional[float] = None
    resistance_level_2: Optional[float] = None
    
    # Pattern recognition
    is_golden_cross: bool = False
    is_death_cross: bool = False
    pattern: Optional[str] = None  # e.g., "Head and Shoulders", "Double Top"


class FundamentalMetrics(BaseModel):
    """Fundamental analysis metrics."""
    
    symbol: str
    as_of_date: datetime
    
    # Valuation metrics
    pe_ratio: Optional[float] = None
    pb_ratio: Optional[float] = None  # Price-to-Book
    dividend_yield: Optional[float] = None
    
    # Growth metrics
    eps_growth: Optional[float] = None
    revenue_growth: Optional[float] = None
    
    # Financial health
    debt_to_equity: Optional[float] = None
    current_ratio: Optional[float] = None
    
    # Profitability
    roe: Optional[float] = None  # Return on Equity
    roa: Optional[float] = None  # Return on Assets
    profit_margin: Optional[float] = None


class GoldStockData(BaseModel):
    """Gold layer: Complete stock analysis with all features."""
    
    symbol: str
    timestamp: datetime
    exchange: str
    
    # Price information
    current_price: float
    price_change: float
    price_change_percent: float
    
    # Technical analysis
    technical_indicators: TechnicalIndicators
    
    # Fundamental analysis
    fundamental_metrics: Optional[FundamentalMetrics] = None
    
    # Sentiment indicators
    news_sentiment_score: float = Field(ge=-1.0, le=1.0)
    sentiment_sources_count: int
    
    # Geopolitical impact
    geo_risk_score: float = Field(ge=0.0, le=1.0)
    affected_by_geo_events: List[str] = []  # Event IDs
    
    # Composite signals
    overall_strength_score: float = Field(ge=0.0, le=100.0)  # 0-100 score
    
    # Buy/Sell signals
    buy_signals: List[str] = []  # e.g., ["RSI_Oversold", "Golden_Cross"]
    sell_signals: List[str] = []  # e.g., ["RSI_Overbought", "Death_Cross"]
    neutral_signals: List[str] = []
    
    # Prediction data
    predicted_direction: str  # "up", "down", "neutral"
    direction_confidence: float = Field(ge=0.0, le=1.0)
    
    # News impact
    recent_news_headlines: List[str] = []
    news_topics: List[str] = []
    
    # Risk assessment
    risk_level: str  # "low", "medium", "high"
    volatility_score: float = Field(ge=0.0, le=100.0)
    
    # Targets
    price_target_1m: Optional[float] = None  # 1-month target
    price_target_3m: Optional[float] = None  # 3-month target
    price_target_6m: Optional[float] = None  # 6-month target
    
    # Aggregation metadata
    last_updated: datetime
    data_completeness: float = Field(ge=0.0, le=1.0)  # Percentage of available data


class GoldPortfolioAnalysis(BaseModel):
    """Gold layer: Portfolio-level analysis."""
    
    portfolio_date: datetime
    stocks: List[str]  # List of symbols
    
    # Portfolio metrics
    total_stocks_analyzed: int
    bullish_count: int
    bearish_count: int
    neutral_count: int
    
    # Sector breakdown
    sector_allocation: Dict[str, float]  # Sector -> percentage
    sector_sentiment: Dict[str, float]  # Sector -> sentiment score
    
    # Overall portfolio health
    portfolio_health_score: float = Field(ge=0.0, le=100.0)
    portfolio_risk: str  # "low", "medium", "high"
    
    # Correlation analysis
    correlation_matrix: Optional[Dict[str, Dict[str, float]]] = None
    
    # Recommendations
    top_buys: List[str]  # Top 5 stocks to buy
    top_sells: List[str]  # Top 5 stocks to sell
    sector_recommendations: Dict[str, str]  # Sector -> recommendation
    
    # Market sentiment
    market_sentiment: str  # "bullish", "bearish", "neutral"
    sentiment_strength: float = Field(ge=0.0, le=1.0)
    
    # News impact
    impactful_news_count: int
    geopolitical_risks: List[str]
