"""Data source clients for NSE, BSE, and News APIs."""

import asyncio
import aiohttp
import logging
from datetime import datetime, timedelta
from typing import Optional, List, Dict, Any
from src.models.data_layers import (
    BronzeStockData,
    BronzeNewsData,
    BronzeGeoPoliticalData,
)
from src.utils.async_helpers import execute_with_retry, execute_with_timeout, AsyncCache
from src.config.settings import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()


class NSEDataClient:
    """National Stock Exchange of India data client."""
    
    def __init__(self):
        self.base_url = settings.nse_api_url or "https://www.nseindia.com/api"
        self.cache = AsyncCache(ttl=300)  # 5-minute cache
        self.session: Optional[aiohttp.ClientSession] = None
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        }
    
    async def initialize(self):
        """Initialize HTTP session."""
        self.session = aiohttp.ClientSession()
    
    async def close(self):
        """Close HTTP session."""
        if self.session:
            await self.session.close()
    
    async def get_quote(self, symbol: str) -> Optional[BronzeStockData]:
        """Fetch real-time quote for a symbol."""
        try:
            # Check cache first
            cache_key = f"nse_quote:{symbol}"
            cached = await self.cache.get(cache_key)
            if cached:
                return cached
            
            # Fetch from API
            url = f"{self.base_url}/quote-equity"
            params = {"symbol": symbol}
            
            result = await execute_with_timeout(
                self._fetch_quote(url, params),
                timeout=10
            )
            
            if result:
                # Cache result
                await self.cache.set(cache_key, result)
            
            return result
        
        except Exception as e:
            logger.error(f"Error fetching NSE quote for {symbol}: {e}")
            return None
    
    async def _fetch_quote(self, url: str, params: Dict) -> Optional[BronzeStockData]:
        """Internal method to fetch quote from API."""
        async with self.session.get(url, params=params, headers=self.headers) as resp:
            if resp.status != 200:
                return None
            
            data = await resp.json()
            
            # Parse response and create BronzeStockData
            # (This is a simplified example - actual parsing depends on API response format)
            quote = data.get("priceInfo", {})
            
            return BronzeStockData(
                symbol=params["symbol"],
                timestamp=datetime.now(),
                exchange="NSE",
                open_price=float(quote.get("open", 0)),
                high_price=float(quote.get("high", 0)),
                low_price=float(quote.get("low", 0)),
                close_price=float(quote.get("close", 0)),
                last_traded_price=float(quote.get("lastPrice", 0)),
                volume=int(quote.get("totalTradedQuantity", 0)),
                turnover=float(quote.get("totalTradedValue", 0)),
                previous_close=float(quote.get("previousClose", 0)),
                source="nse_api",
                raw_data=data
            )
    
    async def get_quotes_batch(self, symbols: List[str]) -> Dict[str, BronzeStockData]:
        """Fetch quotes for multiple symbols in parallel."""
        tasks = [self.get_quote(symbol) for symbol in symbols]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        return {
            symbol: result
            for symbol, result in zip(symbols, results)
            if isinstance(result, BronzeStockData)
        }
    
    async def get_market_status(self) -> Dict[str, Any]:
        """Get current market status."""
        try:
            url = f"{self.base_url}/marketStatus"
            
            async with self.session.get(url, headers=self.headers) as resp:
                if resp.status == 200:
                    return await resp.json()
                return {}
        
        except Exception as e:
            logger.error(f"Error fetching market status: {e}")
            return {}
    
    async def get_index_data(self, index: str) -> Optional[BronzeStockData]:
        """Fetch index data (Sensex, Nifty, etc.)."""
        # Implementation similar to get_quote but for indices
        pass


class BSEDataClient:
    """Bombay Stock Exchange data client."""
    
    def __init__(self):
        self.base_url = settings.bse_api_url or "https://api.bseindia.com/api"
        self.cache = AsyncCache(ttl=300)
        self.session: Optional[aiohttp.ClientSession] = None
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        }
    
    async def initialize(self):
        """Initialize HTTP session."""
        self.session = aiohttp.ClientSession()
    
    async def close(self):
        """Close HTTP session."""
        if self.session:
            await self.session.close()
    
    async def get_quote(self, symbol: str) -> Optional[BronzeStockData]:
        """Fetch real-time quote for a symbol."""
        try:
            cache_key = f"bse_quote:{symbol}"
            cached = await self.cache.get(cache_key)
            if cached:
                return cached
            
            url = f"{self.base_url}/ScripQuoteDetail"
            params = {"scripcode": symbol}  # BSE uses scripcode
            
            result = await execute_with_timeout(
                self._fetch_quote(url, params),
                timeout=10
            )
            
            if result:
                await self.cache.set(cache_key, result)
            
            return result
        
        except Exception as e:
            logger.error(f"Error fetching BSE quote for {symbol}: {e}")
            return None
    
    async def _fetch_quote(self, url: str, params: Dict) -> Optional[BronzeStockData]:
        """Internal method to fetch quote from API."""
        async with self.session.get(url, params=params, headers=self.headers) as resp:
            if resp.status != 200:
                return None
            
            data = await resp.json()
            
            return BronzeStockData(
                symbol=params["scripcode"],
                timestamp=datetime.now(),
                exchange="BSE",
                open_price=float(data.get("open", 0)),
                high_price=float(data.get("high", 0)),
                low_price=float(data.get("low", 0)),
                close_price=float(data.get("close", 0)),
                last_traded_price=float(data.get("lastPrice", 0)),
                volume=int(data.get("volume", 0)),
                turnover=float(data.get("turnover", 0)),
                previous_close=float(data.get("previousClose", 0)),
                source="bse_api",
                raw_data=data
            )
    
    async def get_quotes_batch(self, symbols: List[str]) -> Dict[str, BronzeStockData]:
        """Fetch quotes for multiple symbols in parallel."""
        tasks = [self.get_quote(symbol) for symbol in symbols]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        return {
            symbol: result
            for symbol, result in zip(symbols, results)
            if isinstance(result, BronzeStockData)
        }


class NewsDataClient:
    """Real-time news data client."""
    
    def __init__(self):
        self.news_api_key = settings.news_api_key
        self.base_url = "https://newsapi.org/v2"
        self.cache = AsyncCache(ttl=600)  # 10-minute cache
        self.session: Optional[aiohttp.ClientSession] = None
    
    async def initialize(self):
        """Initialize HTTP session."""
        self.session = aiohttp.ClientSession()
    
    async def close(self):
        """Close HTTP session."""
        if self.session:
            await self.session.close()
    
    async def get_news(
        self,
        query: str,
        language: str = "en",
        sort_by: str = "publishedAt",
        page_size: int = 20
    ) -> List[BronzeNewsData]:
        """Fetch news articles matching query."""
        try:
            cache_key = f"news:{query}:{language}"
            cached = await self.cache.get(cache_key)
            if cached:
                return cached
            
            url = f"{self.base_url}/everything"
            params = {
                "q": query,
                "language": language,
                "sortBy": sort_by,
                "pageSize": page_size,
                "apiKey": self.news_api_key
            }
            
            result = await execute_with_timeout(
                self._fetch_news(url, params),
                timeout=10
            )
            
            if result:
                await self.cache.set(cache_key, result)
            
            return result
        
        except Exception as e:
            logger.error(f"Error fetching news for {query}: {e}")
            return []
    
    async def _fetch_news(self, url: str, params: Dict) -> List[BronzeNewsData]:
        """Internal method to fetch news from API."""
        async with self.session.get(url, params=params) as resp:
            if resp.status != 200:
                return []
            
            data = await resp.json()
            articles = data.get("articles", [])
            
            news_list = []
            for article in articles:
                news = BronzeNewsData(
                    article_id=article.get("url", ""),  # Use URL as ID
                    timestamp=datetime.fromisoformat(
                        article.get("publishedAt", "").replace("Z", "+00:00")
                    ),
                    source=article.get("source", {}).get("name", "Unknown"),
                    headline=article.get("title", ""),
                    summary=article.get("description", ""),
                    full_text=article.get("content", ""),
                    url=article.get("url", ""),
                    author=article.get("author", ""),
                    category="general",
                    raw_data=article
                )
                news_list.append(news)
            
            return news_list
    
    async def get_stock_news(self, symbol: str, days: int = 7) -> List[BronzeNewsData]:
        """Fetch news related to a specific stock."""
        query = f"{symbol} Indian stock market"
        from_date = (datetime.now() - timedelta(days=days)).isoformat()
        
        try:
            cache_key = f"stock_news:{symbol}:{days}d"
            cached = await self.cache.get(cache_key)
            if cached:
                return cached
            
            url = f"{self.base_url}/everything"
            params = {
                "q": query,
                "from": from_date,
                "language": "en",
                "sortBy": "publishedAt",
                "pageSize": 50,
                "apiKey": self.news_api_key
            }
            
            result = await execute_with_timeout(
                self._fetch_news(url, params),
                timeout=15
            )
            
            if result:
                await self.cache.set(cache_key, result)
            
            return result
        
        except Exception as e:
            logger.error(f"Error fetching stock news for {symbol}: {e}")
            return []
    
    async def get_market_news(self, days: int = 1) -> List[BronzeNewsData]:
        """Fetch news related to Indian stock market."""
        query = "Indian stock market NSE BSE Sensex Nifty"
        from_date = (datetime.now() - timedelta(days=days)).isoformat()
        
        try:
            cache_key = f"market_news:{days}d"
            cached = await self.cache.get(cache_key)
            if cached:
                return cached
            
            url = f"{self.base_url}/everything"
            params = {
                "q": query,
                "from": from_date,
                "language": "en",
                "sortBy": "publishedAt",
                "pageSize": 100,
                "apiKey": self.news_api_key
            }
            
            result = await execute_with_timeout(
                self._fetch_news(url, params),
                timeout=15
            )
            
            if result:
                await self.cache.set(cache_key, result)
            
            return result
        
        except Exception as e:
            logger.error(f"Error fetching market news: {e}")
            return []


class GeoPoliticalDataClient:
    """Geopolitical events data client."""
    
    def __init__(self):
        self.cache = AsyncCache(ttl=3600)  # 1-hour cache
        self.session: Optional[aiohttp.ClientSession] = None
    
    async def initialize(self):
        """Initialize HTTP session."""
        self.session = aiohttp.ClientSession()
    
    async def close(self):
        """Close HTTP session."""
        if self.session:
            await self.session.close()
    
    async def get_recent_events(
        self,
        countries: Optional[List[str]] = None,
        severity_min: str = "low"
    ) -> List[BronzeGeoPoliticalData]:
        """Fetch recent geopolitical events."""
        # This would integrate with a geopolitical database like GDELT
        # For now, returning empty list as placeholder
        try:
            cache_key = f"geo_events:{':'.join(countries or [])}"
            cached = await self.cache.get(cache_key)
            if cached:
                return cached
            
            # Placeholder implementation
            events = []
            
            await self.cache.set(cache_key, events)
            return events
        
        except Exception as e:
            logger.error(f"Error fetching geopolitical events: {e}")
            return []
    
    async def get_events_for_countries(
        self,
        countries: List[str],
        days: int = 7
    ) -> List[BronzeGeoPoliticalData]:
        """Fetch events affecting specific countries."""
        # This would filter events for countries with trade relationships to India
        pass
    
    async def get_trade_agreements(self) -> Dict[str, Any]:
        """Fetch current trade agreements and policies affecting India."""
        pass


class DataClientManager:
    """Manager for all data clients."""
    
    def __init__(self):
        self.nse = NSEDataClient()
        self.bse = BSEDataClient()
        self.news = NewsDataClient()
        self.geo = GeoPoliticalDataClient()
    
    async def initialize(self):
        """Initialize all clients."""
        await asyncio.gather(
            self.nse.initialize(),
            self.bse.initialize(),
            self.news.initialize(),
            self.geo.initialize()
        )
        logger.info("All data clients initialized")
    
    async def close(self):
        """Close all clients."""
        await asyncio.gather(
            self.nse.close(),
            self.bse.close(),
            self.news.close(),
            self.geo.close()
        )
        logger.info("All data clients closed")
