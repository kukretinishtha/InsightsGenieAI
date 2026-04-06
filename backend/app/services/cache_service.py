"""Cache service for storing analysis results."""

from typing import Any, Optional
import json
from app.utils.logger import get_logger

logger = get_logger(__name__)


class CacheService:
    """Simple in-memory cache service."""
    
    def __init__(self, max_size: int = 1000, ttl_seconds: int = 3600):
        """Initialize cache service."""
        self.max_size = max_size
        self.ttl_seconds = ttl_seconds
        self._cache: dict = {}
    
    async def get(self, key: str) -> Optional[Any]:
        """Get value from cache."""
        if key in self._cache:
            value, timestamp = self._cache[key]
            logger.debug(f"Cache hit for key: {key}")
            return value
        
        logger.debug(f"Cache miss for key: {key}")
        return None
    
    async def set(self, key: str, value: Any) -> None:
        """Set value in cache."""
        if len(self._cache) >= self.max_size:
            # Remove oldest entry
            oldest_key = next(iter(self._cache))
            del self._cache[oldest_key]
        
        from datetime import datetime, timedelta
        self._cache[key] = (value, datetime.utcnow() + timedelta(seconds=self.ttl_seconds))
        logger.debug(f"Cache set for key: {key}")
    
    async def delete(self, key: str) -> None:
        """Delete value from cache."""
        if key in self._cache:
            del self._cache[key]
            logger.debug(f"Cache deleted for key: {key}")
    
    async def clear(self) -> None:
        """Clear all cache."""
        self._cache.clear()
        logger.info("Cache cleared")
    
    async def get_or_set(
        self,
        key: str,
        fetch_func,
        *args,
        **kwargs
    ) -> Any:
        """Get from cache or fetch and set."""
        cached = await self.get(key)
        if cached is not None:
            return cached
        
        value = await fetch_func(*args, **kwargs)
        await self.set(key, value)
        return value
