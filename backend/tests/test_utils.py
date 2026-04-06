"""Unit tests for async utilities."""

import pytest
import asyncio
from src.utils.async_helpers import (
    execute_with_timeout,
    execute_with_retry,
    gather_with_timeout,
    RateLimiter,
    AsyncCache,
)


@pytest.mark.asyncio
async def test_execute_with_timeout_success():
    """Test successful execution with timeout."""
    
    async def fast_operation():
        await asyncio.sleep(0.1)
        return "success"
    
    result = await execute_with_timeout(
        fast_operation(),
        timeout=1
    )
    
    assert result == "success"


@pytest.mark.asyncio
async def test_execute_with_timeout_exceeded():
    """Test timeout exceeded."""
    
    async def slow_operation():
        await asyncio.sleep(2)
        return "should not reach"
    
    with pytest.raises(asyncio.TimeoutError):
        await execute_with_timeout(
            slow_operation(),
            timeout=1
        )


@pytest.mark.asyncio
async def test_execute_with_retry_success_first_attempt():
    """Test retry succeeds on first attempt."""
    
    async def operation():
        return "success"
    
    result = await execute_with_retry(operation)
    assert result == "success"


@pytest.mark.asyncio
async def test_execute_with_retry_eventual_success():
    """Test retry succeeds after failures."""
    
    call_count = 0
    
    async def flaky_operation():
        nonlocal call_count
        call_count += 1
        
        if call_count < 3:
            raise ValueError("Not ready yet")
        
        return "success"
    
    result = await execute_with_retry(
        flaky_operation,
        max_retries=5
    )
    
    assert result == "success"
    assert call_count == 3


@pytest.mark.asyncio
async def test_execute_with_retry_all_fail():
    """Test retry fails after max attempts."""
    
    async def always_fails():
        raise ValueError("Always fails")
    
    with pytest.raises(ValueError):
        await execute_with_retry(
            always_fails,
            max_retries=3
        )


@pytest.mark.asyncio
async def test_gather_with_timeout_success():
    """Test successful parallel execution with timeout."""
    
    async def task(n):
        await asyncio.sleep(0.1)
        return n * 2
    
    results = await gather_with_timeout(
        task(1),
        task(2),
        task(3),
        timeout=5
    )
    
    assert results == [2, 4, 6]


@pytest.mark.asyncio
async def test_gather_with_timeout_exceeded():
    """Test timeout in parallel execution."""
    
    async def slow_task():
        await asyncio.sleep(5)
    
    with pytest.raises(asyncio.TimeoutError):
        await gather_with_timeout(
            slow_task(),
            slow_task(),
            timeout=1
        )


@pytest.mark.asyncio
async def test_rate_limiter():
    """Test rate limiter."""
    
    limiter = RateLimiter(rate=5, period=1.0)
    
    start = asyncio.get_event_loop().time()
    
    for _ in range(5):
        await limiter.acquire()
    
    elapsed = asyncio.get_event_loop().time() - start
    
    # Should complete quickly (within period)
    assert elapsed < 1.5


@pytest.mark.asyncio
async def test_async_cache_set_get():
    """Test async cache."""
    
    cache = AsyncCache(ttl=3600)
    
    await cache.set("key1", "value1")
    
    result = await cache.get("key1")
    assert result == "value1"


@pytest.mark.asyncio
async def test_async_cache_expiry():
    """Test cache expiry."""
    
    cache = AsyncCache(ttl=1)
    
    await cache.set("key1", "value1")
    
    # Wait for expiry
    await asyncio.sleep(1.5)
    
    result = await cache.get("key1")
    assert result is None


@pytest.mark.asyncio
async def test_async_cache_delete():
    """Test cache deletion."""
    
    cache = AsyncCache()
    
    await cache.set("key1", "value1")
    await cache.delete("key1")
    
    result = await cache.get("key1")
    assert result is None


@pytest.mark.asyncio
async def test_async_cache_clear():
    """Test cache clearing."""
    
    cache = AsyncCache()
    
    await cache.set("key1", "value1")
    await cache.set("key2", "value2")
    await cache.clear()
    
    assert await cache.get("key1") is None
    assert await cache.get("key2") is None
