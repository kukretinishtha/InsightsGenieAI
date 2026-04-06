"""
Caching module for middleware.
"""

import json
import logging
from typing import Any, Optional

import redis

from .config import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()


class CacheManager:
    """Manages caching with Redis."""

    def __init__(self, redis_url: str = None):
        """Initialize cache manager."""
        self.redis_url = redis_url or settings.redis_url
        self.redis_client: Optional[redis.Redis] = None
        self.enabled = settings.cache_enabled

    def connect(self) -> None:
        """Connect to Redis."""
        if not self.enabled:
            logger.info("Cache disabled")
            return

        try:
            self.redis_client = redis.from_url(self.redis_url)
            self.redis_client.ping()
            logger.info("Connected to Redis cache")
        except Exception as e:
            logger.error(f"Failed to connect to Redis: {e}")
            self.enabled = False

    def disconnect(self) -> None:
        """Disconnect from Redis."""
        if self.redis_client:
            self.redis_client.close()
            logger.info("Disconnected from Redis cache")

    def get(self, key: str) -> Optional[Any]:
        """Get value from cache."""
        if not self.enabled or not self.redis_client:
            return None

        try:
            value = self.redis_client.get(key)
            if value:
                return json.loads(value)
            return None
        except Exception as e:
            logger.error(f"Cache get error: {e}")
            return None

    def set(
        self,
        key: str,
        value: Any,
        ttl: int = None,
    ) -> bool:
        """Set value in cache."""
        if not self.enabled or not self.redis_client:
            return False

        try:
            ttl = ttl or settings.cache_ttl
            self.redis_client.setex(
                key,
                ttl,
                json.dumps(value),
            )
            return True
        except Exception as e:
            logger.error(f"Cache set error: {e}")
            return False

    def delete(self, key: str) -> bool:
        """Delete value from cache."""
        if not self.enabled or not self.redis_client:
            return False

        try:
            self.redis_client.delete(key)
            return True
        except Exception as e:
            logger.error(f"Cache delete error: {e}")
            return False

    def clear_pattern(self, pattern: str) -> int:
        """Clear all keys matching pattern."""
        if not self.enabled or not self.redis_client:
            return 0

        try:
            cursor = 0
            deleted = 0
            while True:
                cursor, keys = self.redis_client.scan(
                    cursor, match=pattern
                )
                for key in keys:
                    self.redis_client.delete(key)
                    deleted += 1
                if cursor == 0:
                    break
            return deleted
        except Exception as e:
            logger.error(f"Cache clear pattern error: {e}")
            return 0

    def exists(self, key: str) -> bool:
        """Check if key exists in cache."""
        if not self.enabled or not self.redis_client:
            return False

        try:
            return bool(self.redis_client.exists(key))
        except Exception as e:
            logger.error(f"Cache exists error: {e}")
            return False

    def get_ttl(self, key: str) -> int:
        """Get TTL of key in seconds."""
        if not self.enabled or not self.redis_client:
            return -1

        try:
            return self.redis_client.ttl(key)
        except Exception as e:
            logger.error(f"Cache TTL error: {e}")
            return -1


# Global cache manager instance
_cache_manager: Optional[CacheManager] = None


def get_cache_manager() -> CacheManager:
    """Get cache manager instance."""
    global _cache_manager
    if _cache_manager is None:
        _cache_manager = CacheManager()
        _cache_manager.connect()
    return _cache_manager
