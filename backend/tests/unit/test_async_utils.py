"""Unit tests for async utilities."""

import pytest
import asyncio
from app.utils.async_utils import (
    gather_with_timeout,
    execute_with_retry,
    async_timer,
    AsyncBatchProcessor
)


@pytest.mark.asyncio
async def test_gather_with_timeout():
    """Test gather with timeout."""
    async def slow_task(duration):
        await asyncio.sleep(duration)
        return duration
    
    # Should complete
    results = await gather_with_timeout(
        slow_task(0.1),
        slow_task(0.2),
        timeout=5
    )
    
    assert len(results) == 2


@pytest.mark.asyncio
async def test_gather_with_timeout_exceeded():
    """Test gather timeout."""
    from app.utils.exceptions import TimeoutError as GenieTimeoutError
    
    async def slow_task():
        await asyncio.sleep(10)
        return "done"
    
    with pytest.raises(GenieTimeoutError):
        await gather_with_timeout(slow_task(), timeout=0.1)


@pytest.mark.asyncio
async def test_execute_with_retry_success():
    """Test retry execution with success."""
    call_count = 0
    
    async def flaky_function():
        nonlocal call_count
        call_count += 1
        if call_count < 2:
            raise ValueError("First call fails")
        return "success"
    
    result = await execute_with_retry(flaky_function, max_retries=2)
    
    assert result == "success"
    assert call_count == 2


@pytest.mark.asyncio
async def test_execute_with_retry_failure():
    """Test retry execution with failure."""
    from app.utils.exceptions import TaskExecutionError
    
    async def failing_function():
        raise ValueError("Always fails")
    
    with pytest.raises(TaskExecutionError):
        await execute_with_retry(failing_function, max_retries=2)


@pytest.mark.asyncio
async def test_async_batch_processor():
    """Test async batch processor."""
    results = []
    
    async def process_item(item):
        await asyncio.sleep(0.01)
        results.append(item)
    
    processor = AsyncBatchProcessor(batch_size=3, max_concurrent=2)
    items = list(range(10))
    
    await processor.process(items, process_item)
    
    assert len(results) == 10
