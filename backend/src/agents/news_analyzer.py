"""News Analyzer Agent for sentiment analysis and news impact assessment."""

import asyncio
import logging
from typing import Dict, Any, List
from datetime import datetime, timedelta

from src.agents.base import BaseAgent
from src.utils.logger import get_logger
from src.prompts.system_prompts import NEWS_SENTIMENT_ANALYST_PROMPT
from src.data.clients import NewsDataClient
from src.data.transformers import BronzeToSilverTransformer

logger = get_logger(__name__)


class NewsAnalyzerAgent(BaseAgent):
    """Agent for analyzing news sentiment and impact on stocks."""
    
    def __init__(self):
        super().__init__()
        self.news_client = NewsDataClient()
        self.transformer = BronzeToSilverTransformer()
        self._register_tools()
    
    def _register_tools(self):
        """Register news analysis tools."""
        
        self.register_tool(
            "fetch_stock_news",
            "Fetch recent news about a specific stock",
            self.fetch_stock_news,
            timeout=30
        )
        
        self.register_tool(
            "analyze_sentiment",
            "Analyze sentiment of news articles",
            self.analyze_sentiment,
            timeout=30
        )
        
        self.register_tool(
            "extract_entities",
            "Extract entities from news articles",
            self.extract_entities,
            timeout=30
        )
        
        self.register_tool(
            "identify_trends",
            "Identify trending topics in market news",
            self.identify_trends,
            timeout=30
        )
        
        self.register_tool(
            "assess_news_impact",
            "Assess market impact of news",
            self.assess_news_impact,
            timeout=30
        )
    
    async def analyze(self, symbol: str = None, **kwargs) -> Dict[str, Any]:
        """
        Analyze news sentiment and impact.
        
        Args:
            symbol: Stock symbol to analyze news for
            **kwargs: Additional parameters
        
        Returns:
            Dictionary with news analysis results
        """
        
        logger.info(f"Starting news analysis for {symbol or 'market'}")
        
        # Execute all tools in parallel
        results = await self.execute_tools_parallel(
            [
                "fetch_stock_news",
                "analyze_sentiment",
                "extract_entities",
                "identify_trends",
                "assess_news_impact"
            ],
            symbol=symbol
        )
        
        # Synthesize results
        synthesis = self._synthesize_analysis(results, symbol)
        
        logger.info(f"News analysis completed for {symbol or 'market'}")
        
        return synthesis
    
    # Tool implementations
    
    async def fetch_stock_news(self, symbol: str = None, days: int = 7, **kwargs) -> Dict[str, Any]:
        """Fetch recent news about a stock."""
        
        try:
            if not symbol:
                # Fetch market news
                news_list = await self.news_client.get_market_news(days=days)
                source = "market"
            else:
                # Fetch stock-specific news
                news_list = await self.news_client.get_stock_news(symbol, days=days)
                source = symbol
            
            if not news_list:
                return {
                    "status": "no_data",
                    "articles_found": 0,
                    "source": source
                }
            
            # Transform to silver layer
            silver_articles = []
            for bronze_news in news_list:
                silver = await self.transformer.transform_news_data(bronze_news)
                silver_articles.append({
                    "headline": silver.headline,
                    "source": silver.source,
                    "timestamp": silver.timestamp.isoformat(),
                    "sentiment": silver.sentiment_score,
                    "sentiment_label": silver.sentiment_label,
                    "topics": silver.topics,
                    "impact_potential": silver.market_impact_potential
                })
            
            # Sort by recency
            silver_articles.sort(
                key=lambda x: x["timestamp"],
                reverse=True
            )
            
            return {
                "status": "success",
                "source": source,
                "articles_found": len(silver_articles),
                "date_range_days": days,
                "articles": silver_articles[:20],  # Top 20 most recent
                "latest_timestamp": silver_articles[0]["timestamp"] if silver_articles else None
            }
        
        except Exception as e:
            logger.error(f"Error fetching news for {symbol}: {e}")
            return {
                "status": "error",
                "error": str(e),
                "articles": []
            }
    
    async def analyze_sentiment(self, symbol: str = None, **kwargs) -> Dict[str, Any]:
        """Analyze sentiment of news articles."""
        
        try:
            # Fetch news first
            news_result = await self.fetch_stock_news(symbol, days=7)
            
            if news_result.get("status") != "success":
                return {
                    "status": "no_data",
                    "average_sentiment": 0.0
                }
            
            articles = news_result.get("articles", [])
            
            if not articles:
                return {
                    "status": "no_data",
                    "average_sentiment": 0.0,
                    "articles_analyzed": 0
                }
            
            # Calculate sentiment statistics
            sentiments = [a["sentiment"] for a in articles]
            
            positive = sum(1 for s in sentiments if s > 0.2)
            negative = sum(1 for s in sentiments if s < -0.2)
            neutral = sum(1 for s in sentiments if -0.2 <= s <= 0.2)
            
            average_sentiment = sum(sentiments) / len(sentiments) if sentiments else 0
            
            # Sentiment distribution
            positive_pct = (positive / len(articles) * 100) if articles else 0
            negative_pct = (negative / len(articles) * 100) if articles else 0
            neutral_pct = (neutral / len(articles) * 100) if articles else 0
            
            # Sentiment trend (compare recent vs older)
            if len(articles) >= 2:
                recent_sentiment = sum(s for s in sentiments[:len(sentiments)//2]) / (len(sentiments)//2)
                older_sentiment = sum(s for s in sentiments[len(sentiments)//2:]) / (len(sentiments)//2)
                trend = "improving" if recent_sentiment > older_sentiment else "declining"
            else:
                trend = "insufficient_data"
            
            return {
                "status": "success",
                "articles_analyzed": len(articles),
                "average_sentiment": average_sentiment,
                "sentiment_distribution": {
                    "positive": positive_pct,
                    "negative": negative_pct,
                    "neutral": neutral_pct
                },
                "sentiment_counts": {
                    "positive": positive,
                    "negative": negative,
                    "neutral": neutral
                },
                "sentiment_trend": trend,
                "overall_sentiment": "bullish" if average_sentiment > 0.2 else (
                    "bearish" if average_sentiment < -0.2 else "neutral"
                )
            }
        
        except Exception as e:
            logger.error(f"Error analyzing sentiment for {symbol}: {e}")
            return {
                "status": "error",
                "error": str(e),
                "average_sentiment": 0.0
            }
    
    async def extract_entities(self, symbol: str = None, **kwargs) -> Dict[str, Any]:
        """Extract entities from news articles."""
        
        try:
            news_result = await self.fetch_stock_news(symbol, days=7)
            
            if news_result.get("status") != "success":
                return {
                    "status": "no_data",
                    "entities": {}
                }
            
            articles = news_result.get("articles", [])
            
            # Aggregate entities
            all_stocks = set()
            all_countries = set()
            all_topics = set()
            
            for article in articles:
                if "mentions_stocks" in article:
                    all_stocks.update(article.get("mentions_stocks", []))
                all_topics.update(article.get("topics", []))
            
            # Extract from headlines
            for article in articles:
                headline = article.get("headline", "").upper()
                
                # Common stocks
                stocks = ["RELIANCE", "TCS", "INFY", "HDFC", "ICICI", "WIPRO"]
                for stock in stocks:
                    if stock in headline:
                        all_stocks.add(stock)
                
                # Common countries
                countries = ["US", "CHINA", "JAPAN", "UK", "GERMANY", "FRANCE"]
                for country in countries:
                    if country in headline:
                        all_countries.add(country)
            
            return {
                "status": "success",
                "total_articles": len(articles),
                "entities": {
                    "stocks": list(all_stocks),
                    "countries": list(all_countries),
                    "topics": list(all_topics)
                },
                "most_mentioned_stock": max(
                    ((s, len([a for a in articles if s in a.get("headline", "")])) for s in all_stocks),
                    default=(None, 0)
                )[0] if all_stocks else None,
                "topics_distribution": {
                    topic: len([a for a in articles if topic in a.get("topics", [])])
                    for topic in all_topics
                }
            }
        
        except Exception as e:
            logger.error(f"Error extracting entities for {symbol}: {e}")
            return {
                "status": "error",
                "error": str(e),
                "entities": {}
            }
    
    async def identify_trends(self, symbol: str = None, **kwargs) -> Dict[str, Any]:
        """Identify trending topics in news."""
        
        try:
            # Fetch market news for trend analysis
            news_result = await self.fetch_stock_news(None, days=7)
            
            if news_result.get("status") != "success":
                return {
                    "status": "no_data",
                    "trends": []
                }
            
            articles = news_result.get("articles", [])
            
            # Aggregate topics
            topic_counts = {}
            for article in articles:
                for topic in article.get("topics", []):
                    topic_counts[topic] = topic_counts.get(topic, 0) + 1
            
            # Find trending topics
            trending = sorted(
                topic_counts.items(),
                key=lambda x: x[1],
                reverse=True
            )[:10]
            
            # Keywords in headlines
            keywords = {}
            for article in articles:
                headline = article.get("headline", "").lower().split()
                for word in headline:
                    if len(word) > 4:  # Ignore short words
                        keywords[word] = keywords.get(word, 0) + 1
            
            trending_keywords = sorted(
                keywords.items(),
                key=lambda x: x[1],
                reverse=True
            )[:15]
            
            return {
                "status": "success",
                "total_articles_analyzed": len(articles),
                "trending_topics": [
                    {"topic": t[0], "mentions": t[1]} for t in trending
                ],
                "trending_keywords": [
                    {"keyword": k[0], "mentions": k[1]} for k in trending_keywords
                ],
                "trend_strength": "strong" if trending[0][1] > 5 else (
                    "moderate" if trending[0][1] > 2 else "weak"
                ),
                "market_sentiment_indicators": {
                    "earnings": len([a for a in articles if "earnings" in a.get("headline", "").lower()]),
                    "merger": len([a for a in articles if "merger" in a.get("headline", "").lower()]),
                    "regulation": len([a for a in articles if "regulation" in a.get("headline", "").lower()]),
                    "growth": len([a for a in articles if "growth" in a.get("headline", "").lower()])
                }
            }
        
        except Exception as e:
            logger.error(f"Error identifying trends: {e}")
            return {
                "status": "error",
                "error": str(e),
                "trends": []
            }
    
    async def assess_news_impact(self, symbol: str = None, **kwargs) -> Dict[str, Any]:
        """Assess market impact of news."""
        
        try:
            # Get sentiment analysis
            sentiment_result = await self.analyze_sentiment(symbol)
            entities_result = await self.extract_entities(symbol)
            
            sentiment_score = sentiment_result.get("average_sentiment", 0)
            entities = entities_result.get("entities", {})
            
            # Calculate impact score
            impact_factors = {
                "sentiment_impact": abs(sentiment_score),  # 0-1
                "entity_relevance": (len(entities.get("stocks", [])) + 
                                    len(entities.get("countries", []))) / 10,  # Normalize
                "trend_strength": 0.3  # Placeholder
            }
            
            # Weighted impact
            total_impact = (
                impact_factors["sentiment_impact"] * 0.5 +
                impact_factors["entity_relevance"] * 0.3 +
                impact_factors["trend_strength"] * 0.2
            )
            
            # Impact level
            if total_impact > 0.6:
                impact_level = "CRITICAL"
            elif total_impact > 0.4:
                impact_level = "HIGH"
            elif total_impact > 0.2:
                impact_level = "MEDIUM"
            else:
                impact_level = "LOW"
            
            # Expected market reaction
            if sentiment_score > 0.3:
                market_reaction = "positive"
            elif sentiment_score < -0.3:
                market_reaction = "negative"
            else:
                market_reaction = "neutral"
            
            return {
                "status": "success",
                "overall_impact_score": total_impact,
                "impact_level": impact_level,
                "impact_factors": impact_factors,
                "expected_market_reaction": market_reaction,
                "affected_stocks": entities.get("stocks", []),
                "affected_sectors": ["IT", "Pharma", "Auto"] if entities.get("countries") else [],
                "confidence_level": 0.75,
                "recommendation": (
                    "BULLISH" if market_reaction == "positive" else (
                        "BEARISH" if market_reaction == "negative" else "NEUTRAL"
                    )
                )
            }
        
        except Exception as e:
            logger.error(f"Error assessing news impact: {e}")
            return {
                "status": "error",
                "error": str(e),
                "overall_impact_score": 0.0
            }
    
    def _synthesize_analysis(self, results: Dict[str, Any], symbol: str = None) -> Dict[str, Any]:
        """Synthesize individual tool results into comprehensive analysis."""
        
        return {
            "analysis_type": "news_sentiment",
            "symbol": symbol,
            "timestamp": datetime.now().isoformat(),
            "system_prompt": NEWS_SENTIMENT_ANALYST_PROMPT,
            "tools_executed": list(results.keys()),
            "summary": {
                "overall_sentiment": results.get("analyze_sentiment", {}).get(
                    "overall_sentiment", "UNKNOWN"
                ),
                "articles_analyzed": results.get("fetch_stock_news", {}).get(
                    "articles_found", 0
                ),
                "trending_topics": [
                    t["topic"] for t in results.get("identify_trends", {}).get(
                        "trending_topics", []
                    )[:3]
                ],
                "news_impact": results.get("assess_news_impact", {}).get(
                    "impact_level", "UNKNOWN"
                ),
                "market_reaction": results.get("assess_news_impact", {}).get(
                    "expected_market_reaction", "unknown"
                ),
                "recommendation": results.get("assess_news_impact", {}).get(
                    "recommendation", "NEUTRAL"
                )
            },
            "detailed_results": results,
            "execution_summary": {
                "tools_executed": len(results),
                "successful": sum(1 for r in results.values() if r.get("status") in ["success", "no_data"]),
                "failed": sum(1 for r in results.values() if r.get("status") == "error")
            }
        }
