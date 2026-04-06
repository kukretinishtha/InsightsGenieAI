"""Data transformation pipelines for Bronze -> Silver -> Gold layers."""

import logging
from datetime import datetime, timedelta
from typing import Optional, List, Dict, Any
import statistics

from src.models.data_layers import (
    BronzeStockData,
    BronzeNewsData,
    SilverStockData,
    SilverNewsData,
    SilverGeoPoliticalData,
    GoldStockData,
    TechnicalIndicators,
    FundamentalMetrics,
)
from src.utils.async_helpers import AsyncCache

logger = logging.getLogger(__name__)


class BronzeToSilverTransformer:
    """Transform Bronze layer to Silver layer."""
    
    def __init__(self):
        self.cache = AsyncCache(ttl=3600)
        self.price_history: Dict[str, List[float]] = {}  # For calculating indicators
    
    async def transform_stock_data(
        self,
        bronze: BronzeStockData,
        historical_data: Optional[List[BronzeStockData]] = None
    ) -> SilverStockData:
        """Transform bronze stock data to silver layer."""
        
        # Calculate basic metrics
        price_change = bronze.close_price - bronze.previous_close
        price_change_percent = (price_change / bronze.previous_close * 100) if bronze.previous_close else 0
        
        # Calculate moving averages if historical data available
        sma_5, sma_20, ema_12, ema_26 = None, None, None, None
        volatility_5d, volatility_20d = None, None
        volume_change_percent = None
        sma_volume_5 = None
        
        if historical_data and len(historical_data) >= 20:
            closes = [d.close_price for d in historical_data[-20:]]
            volumes = [d.volume for d in historical_data[-5:]]
            
            # Simple Moving Averages
            if len(closes) >= 5:
                sma_5 = sum(closes[-5:]) / 5
            if len(closes) >= 20:
                sma_20 = sum(closes[-20:]) / 20
            
            # Exponential Moving Averages
            if len(closes) >= 12:
                ema_12 = self._calculate_ema(closes[-12:], 12)
            if len(closes) >= 26:
                ema_26 = self._calculate_ema(closes[-26:], 26)
            
            # Volatility
            if len(closes) >= 5:
                volatility_5d = (statistics.stdev(closes[-5:]) / sum(closes[-5:]) * 5) if sum(closes[-5:]) > 0 else 0
            if len(closes) >= 20:
                volatility_20d = (statistics.stdev(closes) / sum(closes) * 20) if sum(closes) > 0 else 0
            
            # Volume metrics
            if len(volumes) >= 5:
                sma_volume_5 = sum(volumes) // 5
                avg_vol = sum(volumes[:-1]) / 4
                if avg_vol > 0:
                    volume_change_percent = ((volumes[-1] - avg_vol) / avg_vol * 100)
        
        # Data quality assessment
        data_quality_score = self._assess_data_quality(bronze)
        missing_fields = self._identify_missing_fields(bronze)
        
        return SilverStockData(
            symbol=bronze.symbol,
            timestamp=bronze.timestamp,
            exchange=bronze.exchange,
            open_price=bronze.open_price,
            high_price=bronze.high_price,
            low_price=bronze.low_price,
            close_price=bronze.close_price,
            volume=bronze.volume,
            turnover=bronze.turnover,
            price_change=price_change,
            price_change_percent=price_change_percent,
            sma_5=sma_5,
            sma_20=sma_20,
            ema_12=ema_12,
            ema_26=ema_26,
            volatility_5d=volatility_5d,
            volatility_20d=volatility_20d,
            sma_volume_5=sma_volume_5,
            volume_change_percent=volume_change_percent,
            data_quality_score=data_quality_score,
            missing_fields=missing_fields
        )
    
    async def transform_news_data(self, bronze: BronzeNewsData) -> SilverNewsData:
        """Transform bronze news data to silver layer."""
        
        # Sentiment analysis (placeholder - would use actual NLP model)
        sentiment_score, sentiment_label = self._analyze_sentiment(
            bronze.headline + " " + bronze.summary
        )
        
        # Entity extraction (placeholder)
        mentioned_stocks, mentioned_countries, mentioned_companies = self._extract_entities(
            bronze.headline + " " + bronze.summary
        )
        
        # Topic classification
        topics = self._classify_topics(bronze.headline, bronze.summary)
        
        # India relevance scoring
        india_relevance_score = self._calculate_india_relevance(
            bronze.headline,
            mentioned_countries,
            mentioned_stocks
        )
        
        # Market impact assessment
        market_impact_potential = self._assess_market_impact(
            sentiment_score,
            india_relevance_score,
            topics
        )
        
        return SilverNewsData(
            article_id=bronze.article_id,
            timestamp=bronze.timestamp,
            source=bronze.source,
            headline=bronze.headline,
            summary=bronze.summary,
            sentiment_score=sentiment_score,
            sentiment_label=sentiment_label,
            mentioned_stocks=mentioned_stocks,
            mentioned_countries=mentioned_countries,
            mentioned_companies=mentioned_companies,
            topics=topics,
            india_relevance_score=india_relevance_score,
            market_impact_potential=market_impact_potential,
            processed_at=datetime.now()
        )
    
    # Helper methods
    
    @staticmethod
    def _calculate_ema(prices: List[float], period: int) -> float:
        """Calculate Exponential Moving Average."""
        if not prices:
            return 0.0
        
        multiplier = 2.0 / (period + 1)
        ema = prices[0]  # First EMA = SMA
        
        for price in prices[1:]:
            ema = price * multiplier + ema * (1 - multiplier)
        
        return ema
    
    @staticmethod
    def _assess_data_quality(bronze: BronzeStockData) -> float:
        """Assess data quality score (0-1)."""
        score = 1.0
        
        # Check for missing key fields
        if bronze.open_price <= 0:
            score -= 0.1
        if bronze.close_price <= 0:
            score -= 0.1
        if bronze.volume <= 0:
            score -= 0.1
        if bronze.turnover <= 0:
            score -= 0.1
        
        return max(0.0, min(1.0, score))
    
    @staticmethod
    def _identify_missing_fields(bronze: BronzeStockData) -> List[str]:
        """Identify missing fields in data."""
        missing = []
        
        if bronze.bid_price is None:
            missing.append("bid_price")
        if bronze.ask_price is None:
            missing.append("ask_price")
        if bronze.fifty_two_week_high is None:
            missing.append("fifty_two_week_high")
        
        return missing
    
    @staticmethod
    def _analyze_sentiment(text: str) -> tuple[float, str]:
        """Analyze sentiment of text."""
        # Placeholder - would use actual NLP library like TextBlob or transformers
        # For now, simple keyword-based approach
        
        positive_words = ["bullish", "strong", "gain", "positive", "growth", "profit"]
        negative_words = ["bearish", "weak", "loss", "negative", "decline", "risk"]
        
        text_lower = text.lower()
        
        positive_count = sum(1 for word in positive_words if word in text_lower)
        negative_count = sum(1 for word in negative_words if word in text_lower)
        
        if positive_count + negative_count == 0:
            return 0.0, "neutral"
        
        score = (positive_count - negative_count) / (positive_count + negative_count)
        
        if score > 0.2:
            label = "positive"
        elif score < -0.2:
            label = "negative"
        else:
            label = "neutral"
        
        return score, label
    
    @staticmethod
    def _extract_entities(text: str) -> tuple[List[str], List[str], List[str]]:
        """Extract stocks, countries, and companies from text."""
        # Placeholder - would use actual NER model
        
        stocks = []
        countries = []
        companies = []
        
        # Simple pattern matching
        text_upper = text.upper()
        
        # Common Indian stocks
        common_stocks = ["RELIANCE", "TCS", "INFY", "HDFC", "ICICI", "WIPRO", "HCL", "BAJAJ"]
        for stock in common_stocks:
            if stock in text_upper:
                stocks.append(stock)
        
        # Common countries
        common_countries = ["US", "CHINA", "JAPAN", "UK", "GERMANY", "INDIA"]
        for country in common_countries:
            if country in text_upper:
                countries.append(country)
        
        # Common companies
        common_companies = ["APPLE", "GOOGLE", "MICROSOFT", "TESLA", "META", "AMAZON"]
        for company in common_companies:
            if company in text_upper:
                companies.append(company)
        
        return stocks, countries, companies
    
    @staticmethod
    def _classify_topics(headline: str, summary: str) -> List[str]:
        """Classify news topics."""
        text = (headline + " " + summary).lower()
        topics = []
        
        topic_keywords = {
            "earnings": ["earnings", "results", "profit", "revenue"],
            "merger": ["merger", "acquisition", "takeover", "deal"],
            "regulation": ["regulation", "rbi", "sebi", "policy", "law"],
            "tech": ["technology", "ai", "digital", "software"],
            "finance": ["financial", "budget", "interest", "credit"],
            "global": ["global", "international", "trade", "export"],
        }
        
        for topic, keywords in topic_keywords.items():
            if any(keyword in text for keyword in keywords):
                topics.append(topic)
        
        return topics
    
    @staticmethod
    def _calculate_india_relevance(headline: str, countries: List[str], stocks: List[str]) -> float:
        """Calculate relevance to Indian market."""
        score = 0.0
        
        # Direct India mentions
        if "india" in headline.lower():
            score += 0.4
        
        # NSE/BSE mentions
        if any(x in headline.upper() for x in ["NSE", "BSE", "SENSEX", "NIFTY"]):
            score += 0.3
        
        # Relevant stocks mentioned
        if stocks:
            score += min(0.2, len(stocks) * 0.1)
        
        # Trade partner mentions
        trade_partners = ["US", "CHINA", "JAPAN", "UK", "EU", "GERMANY"]
        if any(c in countries for c in trade_partners):
            score += 0.1
        
        return min(1.0, score)
    
    @staticmethod
    def _assess_market_impact(sentiment_score: float, india_relevance: float, topics: List[str]) -> str:
        """Assess potential market impact."""
        
        # High impact topics
        high_impact_topics = ["earnings", "merger", "regulation"]
        
        impact_score = abs(sentiment_score) * india_relevance
        
        if any(topic in high_impact_topics for topic in topics):
            impact_score *= 1.5
        
        if impact_score > 0.6:
            return "high"
        elif impact_score > 0.3:
            return "medium"
        else:
            return "low"


class SilverToGoldTransformer:
    """Transform Silver layer to Gold layer."""
    
    def __init__(self):
        self.cache = AsyncCache(ttl=1800)  # 30-minute cache
    
    async def transform_stock_data(
        self,
        silver: SilverStockData,
        fundamental_metrics: Optional[FundamentalMetrics] = None,
        news_sentiment: float = 0.0,
        geo_risk: float = 0.0,
        geo_events: List[str] = None
    ) -> GoldStockData:
        """Transform silver stock data to gold layer."""
        
        # Calculate technical indicators
        technical = TechnicalIndicators(
            symbol=silver.symbol,
            date=silver.timestamp,
            sma_50=silver.sma_20,  # Simplified for demo
            sma_200=silver.sma_20,
            ema_12=silver.ema_12,
            ema_26=silver.ema_26,
            rsi_14=self._calculate_rsi(silver),
            bollinger_upper=silver.sma_20 * 1.02 if silver.sma_20 else None,
            bollinger_middle=silver.sma_20,
            bollinger_lower=silver.sma_20 * 0.98 if silver.sma_20 else None,
        )
        
        # Generate signals
        buy_signals, sell_signals, neutral_signals = self._generate_signals(silver, technical)
        
        # Predict direction
        predicted_direction, direction_confidence = self._predict_direction(
            silver,
            technical,
            news_sentiment,
            geo_risk
        )
        
        # Calculate overall strength score
        overall_strength = self._calculate_strength_score(
            silver,
            technical,
            buy_signals,
            sell_signals,
            news_sentiment,
            geo_risk
        )
        
        # Assess risk
        risk_level, volatility_score = self._assess_risk(silver, technical)
        
        # Price targets
        target_1m, target_3m, target_6m = self._calculate_price_targets(
            silver.close_price,
            direction_confidence,
            predicted_direction
        )
        
        return GoldStockData(
            symbol=silver.symbol,
            timestamp=silver.timestamp,
            exchange=silver.exchange,
            current_price=silver.close_price,
            price_change=silver.price_change,
            price_change_percent=silver.price_change_percent,
            technical_indicators=technical,
            fundamental_metrics=fundamental_metrics,
            news_sentiment_score=news_sentiment,
            sentiment_sources_count=1,
            geo_risk_score=geo_risk,
            affected_by_geo_events=geo_events or [],
            overall_strength_score=overall_strength,
            buy_signals=buy_signals,
            sell_signals=sell_signals,
            neutral_signals=neutral_signals,
            predicted_direction=predicted_direction,
            direction_confidence=direction_confidence,
            risk_level=risk_level,
            volatility_score=volatility_score,
            price_target_1m=target_1m,
            price_target_3m=target_3m,
            price_target_6m=target_6m,
            last_updated=datetime.now(),
            data_completeness=silver.data_quality_score
        )
    
    # Helper methods
    
    @staticmethod
    def _calculate_rsi(silver: SilverStockData, period: int = 14) -> Optional[float]:
        """Calculate Relative Strength Index."""
        # Simplified - would need price history
        # RSI = 100 - (100 / (1 + RS))
        # where RS = avg gain / avg loss
        return None  # Placeholder
    
    @staticmethod
    def _generate_signals(silver: SilverStockData, technical: TechnicalIndicators) -> tuple[List[str], List[str], List[str]]:
        """Generate buy/sell signals."""
        buy_signals = []
        sell_signals = []
        neutral_signals = []
        
        # Simple Moving Average crossover
        if silver.ema_12 and silver.ema_26:
            if silver.ema_12 > silver.ema_26:
                buy_signals.append("EMA_Golden_Cross")
            else:
                sell_signals.append("EMA_Death_Cross")
        
        # Price above moving average
        if silver.sma_20 and silver.close_price > silver.sma_20 * 1.02:
            buy_signals.append("Price_Above_SMA20")
        elif silver.sma_20 and silver.close_price < silver.sma_20 * 0.98:
            sell_signals.append("Price_Below_SMA20")
        
        # Volume analysis
        if silver.volume_change_percent and silver.volume_change_percent > 20:
            buy_signals.append("Volume_Surge")
        
        return buy_signals, sell_signals, neutral_signals
    
    @staticmethod
    def _predict_direction(
        silver: SilverStockData,
        technical: TechnicalIndicators,
        news_sentiment: float,
        geo_risk: float
    ) -> tuple[str, float]:
        """Predict stock direction."""
        
        score = 0.0
        
        # Technical analysis weight (60%)
        if silver.ema_12 and silver.ema_26:
            if silver.ema_12 > silver.ema_26:
                score += 0.3
            else:
                score -= 0.3
        
        # News sentiment weight (25%)
        score += news_sentiment * 0.25
        
        # Geopolitical risk weight (15%)
        score -= geo_risk * 0.15
        
        confidence = abs(score)
        
        if score > 0.1:
            direction = "up"
        elif score < -0.1:
            direction = "down"
        else:
            direction = "neutral"
        
        return direction, min(1.0, max(0.0, confidence))
    
    @staticmethod
    def _calculate_strength_score(
        silver: SilverStockData,
        technical: TechnicalIndicators,
        buy_signals: List[str],
        sell_signals: List[str],
        news_sentiment: float,
        geo_risk: float
    ) -> float:
        """Calculate overall strength score (0-100)."""
        
        score = 50.0  # Base score
        
        # Signal-based adjustments
        score += len(buy_signals) * 5
        score -= len(sell_signals) * 5
        
        # Sentiment adjustment
        score += news_sentiment * 15
        
        # Risk adjustment
        score -= geo_risk * 10
        
        # Volatility adjustment
        if silver.volatility_20d:
            score -= min(20, silver.volatility_20d * 20)
        
        return max(0.0, min(100.0, score))
    
    @staticmethod
    def _assess_risk(silver: SilverStockData, technical: TechnicalIndicators) -> tuple[str, float]:
        """Assess risk level."""
        
        volatility_score = 0.0
        
        if silver.volatility_20d:
            volatility_score = silver.volatility_20d * 100
        
        if volatility_score > 30:
            risk_level = "high"
        elif volatility_score > 15:
            risk_level = "medium"
        else:
            risk_level = "low"
        
        return risk_level, volatility_score
    
    @staticmethod
    def _calculate_price_targets(
        current_price: float,
        confidence: float,
        direction: str
    ) -> tuple[Optional[float], Optional[float], Optional[float]]:
        """Calculate price targets."""
        
        if direction == "up":
            multiplier_1m = 1.02 + (confidence * 0.05)  # 2-7% upside
            multiplier_3m = 1.05 + (confidence * 0.10)  # 5-15% upside
            multiplier_6m = 1.10 + (confidence * 0.15)  # 10-25% upside
        elif direction == "down":
            multiplier_1m = 0.98 - (confidence * 0.05)  # -2-7% downside
            multiplier_3m = 0.95 - (confidence * 0.10)  # -5-15% downside
            multiplier_6m = 0.90 - (confidence * 0.15)  # -10-25% downside
        else:
            multiplier_1m = 1.0
            multiplier_3m = 1.0
            multiplier_6m = 1.0
        
        return (
            current_price * multiplier_1m,
            current_price * multiplier_3m,
            current_price * multiplier_6m
        )
