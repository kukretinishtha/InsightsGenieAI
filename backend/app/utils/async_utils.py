"""Async utilities and helper functions."""

import asyncio
from typing import Any, Callable, List, TypeVar, Optional, Coroutine
from functools import wraps
import time
from app.utils.logger import get_logger
from app.utils.exceptions import TimeoutError as GenieTimeoutError, TaskExecutionError

logger = get_logger(__name__)

T = TypeVar("T")


async def gather_with_timeout(
    *coros: Coroutine[Any, Any, T],
    timeout: int = 30,
) -> List[T]:
    """
    Gather multiple coroutines with a timeout.
    
    Args:
        *coros: Coroutines to gather
        timeout: Timeout in seconds
        
    Returns:
        List of results
        
    Raises:
        GenieTimeoutError: If timeout is exceeded
    """
    try:
        results = await asyncio.wait_for(
            asyncio.gather(*coros, return_exceptions=True),
            timeout=timeout
        )
        return results
    except asyncio.TimeoutError as e:
        logger.error(f"Gather operation timed out after {timeout}s")
        raise GenieTimeoutError(f"Operation timed out after {timeout} seconds") from e


async def execute_with_retry(
    coro_func: Callable[..., Coroutine[Any, Any, T]],
    *args: Any,
    max_retries: int = 3,
    backoff_factor: float = 2.0,
    initial_delay: float = 1.0,
    **kwargs: Any
) -> T:
    """
    Execute async function with exponential backoff retry logic.
    
    Args:
        coro_func: Async function to execute
        max_retries: Maximum number of retries
        backoff_factor: Exponential backoff factor
        initial_delay: Initial delay in seconds
        *args: Positional arguments for coro_func
        **kwargs: Keyword arguments for coro_func
        
    Returns:
        Result from coro_func
        
    Raises:
        TaskExecutionError: If all retries fail
    """
    last_exception = None
    delay = initial_delay
    
    for attempt in range(max_retries + 1):
        try:
            logger.debug(f"Attempt {attempt + 1}/{max_retries + 1} to execute {coro_func.__name__}")
            return await coro_func(*args, **kwargs)
        except Exception as e:
            last_exception = e
            if attempt < max_retries:
                logger.warning(
                    f"Attempt {attempt + 1} failed for {coro_func.__name__}: {str(e)}. "
                    f"Retrying in {delay}s..."
                )
                await asyncio.sleep(delay)
                delay *= backoff_factor
            else:
                logger.error(f"All {max_retries + 1} attempts failed for {coro_func.__name__}")
    
    raise TaskExecutionError(
        message=f"Failed to execute {coro_func.__name__} after {max_retries + 1} attempts",
        task_name=coro_func.__name__,
        details={"last_error": str(last_exception)}
    ) from last_exception


async def run_in_thread_pool(
    func: Callable[..., T],
    *args: Any,
    **kwargs: Any
) -> T:
    """
    Run a blocking function in a thread pool to avoid blocking event loop.
    
    Args:
        func: Function to run
        *args: Positional arguments
        **kwargs: Keyword arguments
        
    Returns:
        Result from func
    """
    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(None, func, *args)


def async_timer(func: Callable) -> Callable:
    """
    Decorator to measure execution time of async functions.
    
    Args:
        func: Async function to decorate
        
    Returns:
        Decorated function
    """
    @wraps(func)
    async def async_wrapper(*args: Any, **kwargs: Any) -> Any:
        start_time = time.time()
        try:
            result = await func(*args, **kwargs)
            return result
        finally:
            elapsed_time = time.time() - start_time
            logger.debug(f"{func.__name__} executed in {elapsed_time:.2f}s")
    
    return async_wrapper


async def chunk_async_generator(
    items: List[T],
    chunk_size: int,
    async_processor: Callable[[T], Coroutine[Any, Any, Any]]
) -> None:
    """
    Process items in async batches to avoid overwhelming resources.
    
    Args:
        items: Items to process
        chunk_size: Size of each chunk
        async_processor: Async function to process each item
    """
    for i in range(0, len(items), chunk_size):
        chunk = items[i:i + chunk_size]
        await asyncio.gather(*[async_processor(item) for item in chunk], return_exceptions=True)


async def rate_limited_async_call(
    coro_func: Callable[..., Coroutine[Any, Any, T]],
    *args: Any,
    calls_per_second: float = 10.0,
    **kwargs: Any
) -> T:
    """
    Execute async function with rate limiting.
    
    Args:
        coro_func: Async function to execute
        calls_per_second: Maximum calls per second
        *args: Positional arguments
        **kwargs: Keyword arguments
        
    Returns:
        Result from coro_func
    """
    delay = 1.0 / calls_per_second
    await asyncio.sleep(delay)
    return await coro_func(*args, **kwargs)


class AsyncBatchProcessor:
    """Process items in batches asynchronously."""
    
    def __init__(
        self,
        batch_size: int = 10,
        max_concurrent: int = 5,
    ):
        """Initialize batch processor."""
        self.batch_size = batch_size
        self.max_concurrent = max_concurrent
        self.semaphore = asyncio.Semaphore(max_concurrent)
    
    async def process(
        self,
        items: List[T],
        processor: Callable[[T], Coroutine[Any, Any, Any]]
    ) -> List[Any]:
        """
        Process items in batches.
        
        Args:
            items: Items to process
            processor: Async function to process each item
            
        Returns:
            List of results
        """
        results = []
        
        for i in range(0, len(items), self.batch_size):
            batch = items[i:i + self.batch_size]
            batch_results = await asyncio.gather(
                *[self._process_with_semaphore(item, processor) for item in batch],
                return_exceptions=True
            )
            results.extend(batch_results)
        
        return results
    
    async def _process_with_semaphore(
        self,
        item: T,
        processor: Callable[[T], Coroutine[Any, Any, Any]]
    ) -> Any:
        """Process item with semaphore."""
        async with self.semaphore:
            return await processor(item)
