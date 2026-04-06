"""Async utility functions for InsightGenie AI."""

import asyncio
import logging
from typing import Any, Callable, Coroutine, List, Optional

logger = logging.getLogger(__name__)


async def execute_with_timeout(
    coro: Coroutine[Any, Any, Any],
    timeout: int = 300,
    fallback: Optional[Any] = None,
) -> Any:
    """
    Execute a coroutine with timeout protection.

    Args:
        coro: Coroutine to execute
        timeout: Timeout in seconds
        fallback: Fallback value if timeout occurs

    Returns:
        Coroutine result or fallback value
    """
    try:
        result = await asyncio.wait_for(coro, timeout=timeout)
        return result
    except asyncio.TimeoutError:
        logger.warning(f"Operation timed out after {timeout}s")
        if fallback is not None:
            return fallback
        raise


async def execute_with_retry(
    coro_func: Callable[[], Coroutine[Any, Any, Any]],
    max_retries: int = 3,
    initial_delay: float = 1.0,
    max_delay: float = 60.0,
    backoff_multiplier: float = 2.0,
) -> Any:
    """
    Execute a coroutine with exponential backoff retry logic.

    Args:
        coro_func: Function that returns a coroutine to execute
        max_retries: Maximum number of retries
        initial_delay: Initial delay between retries in seconds
        max_delay: Maximum delay between retries in seconds
        backoff_multiplier: Multiplier for exponential backoff

    Returns:
        Coroutine result

    Raises:
        Exception: If all retries fail
    """
    delay = initial_delay
    last_exception = None

    for attempt in range(max_retries):
        try:
            result = await coro_func()
            if attempt > 0:
                logger.info(f"Operation succeeded on attempt {attempt + 1}")
            return result

        except Exception as e:
            last_exception = e
            if attempt < max_retries - 1:
                logger.warning(
                    f"Attempt {attempt + 1} failed, retrying in {delay:.1f}s: {str(e)}"
                )
                await asyncio.sleep(delay)
                delay = min(delay * backoff_multiplier, max_delay)
            else:
                logger.error(f"All {max_retries} attempts failed: {str(e)}")

    if last_exception:
        raise last_exception


async def gather_with_timeout(
    *coros: Coroutine[Any, Any, Any],
    timeout: int = 300,
    return_exceptions: bool = False,
) -> List[Any]:
    """
    Execute multiple coroutines in parallel with timeout.

    Args:
        *coros: Coroutines to execute
        timeout: Timeout in seconds
        return_exceptions: Whether to return exceptions as results

    Returns:
        List of results
    """
    try:
        results = await asyncio.wait_for(
            asyncio.gather(*coros, return_exceptions=return_exceptions),
            timeout=timeout
        )
        return results
    except asyncio.TimeoutError:
        logger.error(f"Parallel execution timed out after {timeout}s")
        raise


async def batch_process(
    items: List[Any],
    processor: Callable[[Any], Coroutine[Any, Any, Any]],
    batch_size: int = 10,
    max_concurrent: int = 5,
) -> List[Any]:
    """
    Process items in batches with concurrency control.

    Args:
        items: Items to process
        processor: Async function to process each item
        batch_size: Number of items to process in each batch
        max_concurrent: Maximum concurrent operations per batch

    Returns:
        List of processed results
    """
    results = []
    
    for i in range(0, len(items), batch_size):
        batch = items[i:i + batch_size]
        
        # Limit concurrency within batch
        semaphore = asyncio.Semaphore(max_concurrent)
        
        async def process_with_semaphore(item):
            async with semaphore:
                return await processor(item)
        
        batch_results = await asyncio.gather(
            *[process_with_semaphore(item) for item in batch],
            return_exceptions=True
        )
        
        results.extend(batch_results)
    
    return results


class RateLimiter:
    """Async rate limiter using token bucket algorithm."""

    def __init__(self, rate: int, period: float = 1.0):
        """
        Initialize rate limiter.

        Args:
            rate: Number of allowed operations per period
            period: Time period in seconds
        """
        self.rate = rate
        self.period = period
        self.tokens = rate
        self.updated_at = asyncio.get_event_loop().time()
        self.lock = asyncio.Lock()

    async def acquire(self) -> None:
        """
        Acquire a token, waiting if necessary.
        """
        async with self.lock:
            now = asyncio.get_event_loop().time()
            elapsed = now - self.updated_at

            # Refill tokens based on elapsed time
            self.tokens = min(
                self.rate,
                self.tokens + elapsed * (self.rate / self.period)
            )
            self.updated_at = now

            # Wait if no tokens available
            if self.tokens < 1:
                wait_time = (1 - self.tokens) * (self.period / self.rate)
                await asyncio.sleep(wait_time)
                self.tokens = 0
            else:
                self.tokens -= 1


class AsyncCache:
    """Simple async-compatible cache."""

    def __init__(self, ttl: int = 3600):
        """
        Initialize cache.

        Args:
            ttl: Time-to-live in seconds
        """
        self.ttl = ttl
        self.cache: dict[str, tuple[Any, float]] = {}
        self.lock = asyncio.Lock()

    async def get(self, key: str) -> Optional[Any]:
        """Get value from cache."""
        async with self.lock:
            if key not in self.cache:
                return None
            
            value, timestamp = self.cache[key]
            elapsed = asyncio.get_event_loop().time() - timestamp
            
            if elapsed > self.ttl:
                del self.cache[key]
                return None
            
            return value

    async def set(self, key: str, value: Any) -> None:
        """Set value in cache."""
        async with self.lock:
            self.cache[key] = (value, asyncio.get_event_loop().time())

    async def delete(self, key: str) -> None:
        """Delete value from cache."""
        async with self.lock:
            if key in self.cache:
                del self.cache[key]

    async def clear(self) -> None:
        """Clear all cache."""
        async with self.lock:
            self.cache.clear()
