"""Data pipeline orchestrator for managing Bronze -> Silver -> Gold transformations."""

import asyncio
import logging
from datetime import datetime
from typing import Optional, List, Dict, Any

from src.data.clients import DataClientManager, NSEDataClient, BSEDataClient, NewsDataClient
from src.data.transformers import BronzeToSilverTransformer, SilverToGoldTransformer
from src.models.data_layers import (
    BronzeStockData,
    SilverStockData,
    GoldStockData,
)
from src.utils.async_helpers import AsyncCache, execute_with_retry

logger = logging.getLogger(__name__)


class DataPipeline:
    """Main data pipeline orchestrator."""
    
    def __init__(self):
        self.clients = DataClientManager()
        self.bronze_to_silver = BronzeToSilverTransformer()
        self.silver_to_gold = SilverToGoldTransformer()
        
        # Storage for different layers
        self.bronze_cache = AsyncCache(ttl=300)  # 5 minutes
        self.silver_cache = AsyncCache(ttl=600)  # 10 minutes
        self.gold_cache = AsyncCache(ttl=1800)  # 30 minutes
        
        # Historical data for technical indicators
        self.price_history: Dict[str, List[BronzeStockData]] = {}
        
        self.initialized = False
    
    async def initialize(self):
        """Initialize all data clients."""
        if not self.initialized:
            await self.clients.initialize()
            self.initialized = True
            logger.info("Data pipeline initialized")
    
    async def close(self):
        """Close all data clients."""
        await self.clients.close()
        self.initialized = False
        logger.info("Data pipeline closed")
    
    async def get_stock_analysis(
        self,
        symbol: str,
        include_news: bool = True,
        include_geo: bool = True,
        from_both_exchanges: bool = False
    ) -> Optional[GoldStockData]:
        """Get complete stock analysis through all data layers."""
        
        try:
            # Check gold cache first
            cache_key = f"gold:{symbol}"
            cached = await self.gold_cache.get(cache_key)
            if cached:
                return cached
            
            # Phase 1: Bronze layer - Fetch raw data
            logger.info(f"Fetching raw data for {symbol}")
            bronze_data = await self._fetch_bronze_data(symbol, from_both_exchanges)
            
            if not bronze_data:
                logger.warning(f"No data available for {symbol}")
                return None
            
            # Store in bronze cache
            await self.bronze_cache.set(f"bronze:{symbol}", bronze_data)
            
            # Phase 2: Silver layer - Clean and process
            logger.info(f"Transforming {symbol} to silver layer")
            silver_data = await self._transform_to_silver(symbol, bronze_data)
            
            # Store in silver cache
            await self.silver_cache.set(f"silver:{symbol}", silver_data)
            
            # Phase 3: Fetch supplementary data (news, geo)
            news_sentiment = 0.0
            geo_risk = 0.0
            geo_events = []
            
            if include_news:
                logger.info(f"Fetching news for {symbol}")
                news_sentiment = await self._fetch_news_sentiment(symbol)
            
            if include_geo:
                logger.info(f"Fetching geopolitical data")
                geo_risk, geo_events = await self._fetch_geo_data()
            
            # Phase 4: Gold layer - Aggregate and synthesize
            logger.info(f"Transforming {symbol} to gold layer")
            gold_data = await self._transform_to_gold(
                silver_data,
                news_sentiment,
                geo_risk,
                geo_events
            )
            
            # Cache gold result
            await self.gold_cache.set(cache_key, gold_data)
            
            logger.info(f"Successfully analyzed {symbol}")
            return gold_data
        
        except Exception as e:
            logger.error(f"Error analyzing {symbol}: {e}", exc_info=True)
            return None
    
    async def get_batch_analysis(
        self,
        symbols: List[str],
        include_news: bool = True,
        include_geo: bool = True
    ) -> Dict[str, Optional[GoldStockData]]:
        """Analyze multiple stocks in parallel."""
        
        tasks = [
            self.get_stock_analysis(
                symbol,
                include_news=include_news,
                include_geo=include_geo
            )
            for symbol in symbols
        ]
        
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        return {
            symbol: result
            for symbol, result in zip(symbols, results)
            if isinstance(result, GoldStockData) or result is None
        }
    
    async def update_real_time(self, symbol: str) -> Optional[GoldStockData]:
        """Update stock data with latest real-time information."""
        return await self.get_stock_analysis(symbol)
    
    async def stream_updates(
        self,
        symbols: List[str],
        interval_seconds: int = 60,
        max_updates: Optional[int] = None
    ):
        """Stream continuous updates for symbols."""
        
        update_count = 0
        
        while max_updates is None or update_count < max_updates:
            try:
                logger.info(f"Fetching real-time updates for {len(symbols)} symbols")
                
                results = await self.get_batch_analysis(symbols, include_geo=False)
                
                yield {
                    "timestamp": datetime.now(),
                    "data": results,
                    "update_number": update_count
                }
                
                update_count += 1
                
                # Wait for next update
                await asyncio.sleep(interval_seconds)
            
            except Exception as e:
                logger.error(f"Error in stream update: {e}")
                await asyncio.sleep(interval_seconds)
    
    # Private helper methods
    
    async def _fetch_bronze_data(
        self,
        symbol: str,
        from_both_exchanges: bool = False
    ) -> Optional[BronzeStockData]:
        """Fetch raw data from NSE/BSE."""
        
        try:
            # Try NSE first
            nse_data = await execute_with_retry(
                self.clients.nse.get_quote,
                args=(symbol,),
                max_retries=2
            )
            
            if nse_data:
                return nse_data
            
            # Fallback to BSE
            bse_data = await execute_with_retry(
                self.clients.bse.get_quote,
                args=(symbol,),
                max_retries=2
            )
            
            if bse_data:
                return bse_data
            
            logger.warning(f"Could not fetch data from NSE or BSE for {symbol}")
            return None
        
        except Exception as e:
            logger.error(f"Error fetching bronze data for {symbol}: {e}")
            return None
    
    async def _transform_to_silver(
        self,
        symbol: str,
        bronze: BronzeStockData
    ) -> SilverStockData:
        """Transform bronze to silver layer."""
        
        # Get historical data if available
        historical = self.price_history.get(symbol, [])
        
        silver = await self.bronze_to_silver.transform_stock_data(bronze, historical)
        
        # Update price history
        if symbol not in self.price_history:
            self.price_history[symbol] = []
        
        self.price_history[symbol].append(bronze)
        
        # Keep only last 100 days
        if len(self.price_history[symbol]) > 100:
            self.price_history[symbol] = self.price_history[symbol][-100:]
        
        return silver
    
    async def _transform_to_gold(
        self,
        silver: SilverStockData,
        news_sentiment: float = 0.0,
        geo_risk: float = 0.0,
        geo_events: List[str] = None
    ) -> GoldStockData:
        """Transform silver to gold layer."""
        
        return await self.silver_to_gold.transform_stock_data(
            silver,
            news_sentiment=news_sentiment,
            geo_risk=geo_risk,
            geo_events=geo_events or []
        )
    
    async def _fetch_news_sentiment(self, symbol: str) -> float:
        """Fetch news and calculate sentiment."""
        
        try:
            news_list = await execute_with_retry(
                self.clients.news.get_stock_news,
                args=(symbol,),
                max_retries=2
            )
            
            if not news_list:
                return 0.0
            
            # Calculate average sentiment
            sentiments = []
            for news in news_list:
                silver_news = await self.bronze_to_silver.transform_news_data(news)
                sentiments.append(silver_news.sentiment_score)
            
            if sentiments:
                return sum(sentiments) / len(sentiments)
            
            return 0.0
        
        except Exception as e:
            logger.error(f"Error fetching news sentiment for {symbol}: {e}")
            return 0.0
    
    async def _fetch_geo_data(self) -> tuple[float, List[str]]:
        """Fetch geopolitical data and assess impact."""
        
        try:
            events = await execute_with_retry(
                self.clients.geo.get_recent_events,
                max_retries=1
            )
            
            if not events:
                return 0.0, []
            
            # Calculate overall risk and extract event IDs
            risk_score = 0.0
            event_ids = []
            
            for event in events:
                # Simple risk calculation based on severity
                severity_map = {"low": 0.1, "medium": 0.3, "high": 0.6, "critical": 1.0}
                risk_score += severity_map.get(event.severity, 0.2)
                event_ids.append(event.event_id)
            
            # Average risk
            if events:
                risk_score = risk_score / len(events)
            
            return min(1.0, risk_score), event_ids
        
        except Exception as e:
            logger.error(f"Error fetching geopolitical data: {e}")
            return 0.0, []


# Global instance
_pipeline_instance: Optional[DataPipeline] = None


async def get_pipeline() -> DataPipeline:
    """Get or create the data pipeline instance."""
    global _pipeline_instance
    
    if _pipeline_instance is None:
        _pipeline_instance = DataPipeline()
        await _pipeline_instance.initialize()
    
    return _pipeline_instance


async def close_pipeline():
    """Close the data pipeline instance."""
    global _pipeline_instance
    
    if _pipeline_instance:
        await _pipeline_instance.close()
        _pipeline_instance = None
