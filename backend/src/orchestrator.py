"""Analysis Orchestrator for coordinating multiple agents and data pipeline."""

import asyncio
import logging
from datetime import datetime
from typing import Optional, List, Dict, Any
from uuid import uuid4

from src.agents.stock_analyzer import StockAnalyzerAgent
from src.agents.geopolitical_analyst import GeopoliticalAnalystAgent
from src.agents.news_analyzer import NewsAnalyzerAgent
from src.data.pipeline import get_pipeline, close_pipeline
from src.models.stock import AnalysisResult
from src.utils.logger import get_logger
from src.utils.async_helpers import AsyncCache

logger = get_logger(__name__)


class AnalysisOrchestrator:
    """Orchestrate analysis across multiple agents and data layers."""
    
    def __init__(self):
        self.stock_analyzer = StockAnalyzerAgent()
        self.geo_analyst = GeopoliticalAnalystAgent()
        self.news_analyst = NewsAnalyzerAgent()
        
        self.pipeline = None
        self.cache = AsyncCache(ttl=1800)  # 30-minute cache
        
        # Track analysis requests
        self.analysis_jobs: Dict[str, Dict[str, Any]] = {}
        
        self.initialized = False
    
    async def initialize(self):
        """Initialize orchestrator and all components."""
        if not self.initialized:
            self.pipeline = await get_pipeline()
            self.initialized = True
            logger.info("AnalysisOrchestrator initialized")
    
    async def close(self):
        """Close orchestrator and all components."""
        if self.initialized:
            await close_pipeline()
            self.initialized = False
            logger.info("AnalysisOrchestrator closed")
    
    async def analyze_stock(
        self,
        symbol: str,
        analysis_type: str = "comprehensive"
    ) -> Optional[AnalysisResult]:
        """
        Analyze a stock comprehensively using all agents.
        
        Args:
            symbol: Stock symbol to analyze
            analysis_type: "quick", "standard", or "comprehensive"
        
        Returns:
            AnalysisResult with combined analysis
        """
        
        request_id = str(uuid4())
        
        try:
            logger.info(f"Starting {analysis_type} analysis for {symbol} (request_id={request_id})")
            
            # Check cache
            cache_key = f"analysis:{symbol}:{analysis_type}"
            cached = await self.cache.get(cache_key)
            if cached:
                logger.info(f"Returning cached analysis for {symbol}")
                return cached
            
            # Track job
            self.analysis_jobs[request_id] = {
                "symbol": symbol,
                "analysis_type": analysis_type,
                "status": "in_progress",
                "started_at": datetime.now()
            }
            
            # Run all analyses in parallel
            stock_task = self.stock_analyzer.analyze(symbol=symbol)
            geo_task = self.geo_analyst.analyze(symbol=symbol)
            news_task = self.news_analyzer.analyze(symbol=symbol)
            
            # Execute in parallel
            stock_result, geo_result, news_result = await asyncio.gather(
                stock_task,
                geo_task,
                news_task,
                return_exceptions=True
            )
            
            # Handle any exceptions
            if isinstance(stock_result, Exception):
                logger.error(f"Stock analysis failed: {stock_result}")
                stock_result = {"status": "error", "error": str(stock_result)}
            
            if isinstance(geo_result, Exception):
                logger.error(f"Geopolitical analysis failed: {geo_result}")
                geo_result = {"status": "error", "error": str(geo_result)}
            
            if isinstance(news_result, Exception):
                logger.error(f"News analysis failed: {news_result}")
                news_result = {"status": "error", "error": str(news_result)}
            
            # Get data layer analysis
            gold_data = None
            if self.pipeline:
                gold_data = await self.pipeline.get_stock_analysis(
                    symbol,
                    include_news=True,
                    include_geo=True
                )
            
            # Synthesize all results
            result = self._synthesize_analysis(
                symbol,
                stock_result,
                geo_result,
                news_result,
                gold_data,
                analysis_type
            )
            
            # Cache result
            await self.cache.set(cache_key, result)
            
            # Update job status
            self.analysis_jobs[request_id]["status"] = "completed"
            self.analysis_jobs[request_id]["completed_at"] = datetime.now()
            
            logger.info(f"Analysis completed for {symbol} (request_id={request_id})")
            
            return result
        
        except Exception as e:
            logger.error(f"Error analyzing {symbol}: {e}", exc_info=True)
            
            # Update job status
            if request_id in self.analysis_jobs:
                self.analysis_jobs[request_id]["status"] = "failed"
                self.analysis_jobs[request_id]["error"] = str(e)
            
            return None
    
    async def analyze_portfolio(
        self,
        symbols: List[str],
        analysis_type: str = "standard"
    ) -> Dict[str, Optional[AnalysisResult]]:
        """
        Analyze multiple stocks in parallel.
        
        Args:
            symbols: List of stock symbols
            analysis_type: "quick", "standard", or "comprehensive"
        
        Returns:
            Dictionary mapping symbols to AnalysisResult
        """
        
        logger.info(f"Starting portfolio analysis for {len(symbols)} stocks")
        
        tasks = [
            self.analyze_stock(symbol, analysis_type)
            for symbol in symbols
        ]
        
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        analysis_results = {}
        for symbol, result in zip(symbols, results):
            if isinstance(result, Exception):
                logger.error(f"Analysis failed for {symbol}: {result}")
                analysis_results[symbol] = None
            else:
                analysis_results[symbol] = result
        
        logger.info(f"Portfolio analysis completed for {len(symbols)} stocks")
        
        return analysis_results
    
    async def stream_analysis(
        self,
        symbol: str,
        interval_seconds: int = 300,
        max_updates: Optional[int] = None
    ):
        """
        Stream continuous analysis updates for a stock.
        
        Args:
            symbol: Stock symbol to analyze
            interval_seconds: Interval between updates
            max_updates: Maximum number of updates (None = infinite)
        
        Yields:
            AnalysisResult objects
        """
        
        update_count = 0
        
        while max_updates is None or update_count < max_updates:
            try:
                result = await self.analyze_stock(symbol, "quick")
                
                if result:
                    yield {
                        "timestamp": datetime.now(),
                        "update_number": update_count,
                        "data": result
                    }
                
                update_count += 1
                
                # Wait for next update
                await asyncio.sleep(interval_seconds)
            
            except Exception as e:
                logger.error(f"Error in stream analysis: {e}")
                await asyncio.sleep(interval_seconds)
    
    def get_job_status(self, request_id: str) -> Optional[Dict[str, Any]]:
        """Get status of an analysis job."""
        return self.analysis_jobs.get(request_id)
    
    def get_all_jobs(self) -> Dict[str, Dict[str, Any]]:
        """Get all analysis jobs."""
        return self.analysis_jobs.copy()
    
    def _synthesize_analysis(
        self,
        symbol: str,
        stock_result: Dict[str, Any],
        geo_result: Dict[str, Any],
        news_result: Dict[str, Any],
        gold_data: Optional[Any],
        analysis_type: str
    ) -> AnalysisResult:
        """Synthesize results from all agents into comprehensive analysis."""
        
        # Extract key metrics from each agent
        stock_summary = stock_result.get("summary", {}) if stock_result else {}
        geo_summary = geo_result.get("summary", {}) if geo_result else {}
        news_summary = news_result.get("summary", {}) if news_result else {}
        
        # Extract gold layer data
        gold_summary = {}
        if gold_data:
            gold_summary = {
                "current_price": gold_data.current_price,
                "price_change_percent": gold_data.price_change_percent,
                "strength_score": gold_data.overall_strength_score,
                "risk_level": gold_data.risk_level,
                "buy_signals": gold_data.buy_signals,
                "sell_signals": gold_data.sell_signals,
                "predicted_direction": gold_data.predicted_direction,
                "direction_confidence": gold_data.direction_confidence,
                "price_targets": {
                    "1m": gold_data.price_target_1m,
                    "3m": gold_data.price_target_3m,
                    "6m": gold_data.price_target_6m
                }
            }
        
        # Determine overall recommendation
        recommendation = self._generate_recommendation(
            stock_summary,
            geo_summary,
            news_summary,
            gold_summary
        )
        
        # Calculate confidence
        confidence = self._calculate_confidence(
            stock_result,
            geo_result,
            news_result
        )
        
        return AnalysisResult(
            symbol=symbol,
            timestamp=datetime.now(),
            analysis_type=analysis_type,
            recommendation=recommendation,
            confidence_score=confidence,
            price_target=gold_summary.get("price_targets", {}).get("3m"),
            risk_level=gold_summary.get("risk_level", "UNKNOWN"),
            technical_analysis=stock_summary,
            geopolitical_analysis=geo_summary,
            news_sentiment=news_summary,
            data_layer_analysis=gold_summary,
            overall_summary={
                "bullish_signals": len(stock_summary.get("buy_signals", [])),
                "bearish_signals": len(stock_summary.get("sell_signals", [])),
                "geopolitical_risk": geo_summary.get("overall_risk_assessment", "UNKNOWN"),
                "news_sentiment": news_summary.get("overall_sentiment", "UNKNOWN"),
                "market_outlook": self._determine_outlook(
                    stock_summary,
                    geo_summary,
                    news_summary
                )
            }
        )
    
    @staticmethod
    def _generate_recommendation(
        stock: Dict[str, Any],
        geo: Dict[str, Any],
        news: Dict[str, Any],
        gold: Dict[str, Any]
    ) -> str:
        """Generate investment recommendation."""
        
        score = 50  # Base neutral score
        
        # Stock analysis (40% weight)
        if gold.get("predicted_direction") == "up":
            score += 15
        elif gold.get("predicted_direction") == "down":
            score -= 15
        
        score += len(gold.get("buy_signals", [])) * 3
        score -= len(gold.get("sell_signals", [])) * 3
        
        # News sentiment (30% weight)
        news_sentiment = news.get("overall_sentiment", "neutral")
        if news_sentiment == "bullish":
            score += 10
        elif news_sentiment == "bearish":
            score -= 10
        
        # Geopolitical risk (30% weight)
        geo_risk = geo.get("overall_risk_assessment", "UNKNOWN")
        if geo_risk == "CRITICAL":
            score -= 15
        elif geo_risk == "HIGH":
            score -= 10
        elif geo_risk == "LOW":
            score += 5
        
        # Generate recommendation
        if score >= 65:
            return "STRONG BUY"
        elif score >= 55:
            return "BUY"
        elif score >= 45:
            return "HOLD"
        elif score >= 35:
            return "SELL"
        else:
            return "STRONG SELL"
    
    @staticmethod
    def _calculate_confidence(
        stock_result: Dict[str, Any],
        geo_result: Dict[str, Any],
        news_result: Dict[str, Any]
    ) -> float:
        """Calculate overall confidence score (0-1)."""
        
        # Base confidence from data availability
        confidence = 0.5
        
        # Increase confidence if all agents succeeded
        if stock_result.get("status") == "success":
            confidence += 0.15
        if geo_result.get("status") == "success":
            confidence += 0.15
        if news_result.get("status") in ["success", "no_data"]:
            confidence += 0.15
        
        return min(1.0, confidence)
    
    @staticmethod
    def _determine_outlook(
        stock: Dict[str, Any],
        geo: Dict[str, Any],
        news: Dict[str, Any]
    ) -> str:
        """Determine overall market outlook."""
        
        bullish_score = 0
        bearish_score = 0
        
        # Stock technical
        if stock.get("trend") == "bullish":
            bullish_score += 2
        elif stock.get("trend") == "bearish":
            bearish_score += 2
        
        # News sentiment
        if news.get("overall_sentiment") == "bullish":
            bullish_score += 1
        elif news.get("overall_sentiment") == "bearish":
            bearish_score += 1
        
        # Geopolitical
        geo_risk = geo.get("overall_risk_assessment", "MEDIUM")
        if geo_risk in ["LOW", "MEDIUM"]:
            bullish_score += 1
        else:
            bearish_score += 1
        
        if bullish_score > bearish_score:
            return "BULLISH"
        elif bearish_score > bullish_score:
            return "BEARISH"
        else:
            return "NEUTRAL"


# Global orchestrator instance
_orchestrator_instance: Optional[AnalysisOrchestrator] = None


async def get_orchestrator() -> AnalysisOrchestrator:
    """Get or create the orchestrator instance."""
    global _orchestrator_instance
    
    if _orchestrator_instance is None:
        _orchestrator_instance = AnalysisOrchestrator()
        await _orchestrator_instance.initialize()
    
    return _orchestrator_instance


async def close_orchestrator():
    """Close the orchestrator instance."""
    global _orchestrator_instance
    
    if _orchestrator_instance:
        await _orchestrator_instance.close()
        _orchestrator_instance = None
