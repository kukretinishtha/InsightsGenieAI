"""Genie API client with polling mechanism."""

import asyncio
import logging
from typing import Any, Dict, Optional
from datetime import datetime
import aiohttp
from uuid import uuid4

logger = logging.getLogger(__name__)


class GenieApiClient:
    """Async Genie API client with intelligent polling."""

    def __init__(
        self,
        api_url: str,
        api_key: str,
        model: str = "claude-3-5-sonnet",
        timeout: int = 300,
        max_retries: int = 3,
    ):
        """
        Initialize Genie API client.

        Args:
            api_url: Genie API base URL
            api_key: API authentication key
            model: Model to use
            timeout: Request timeout in seconds
            max_retries: Maximum retry attempts
        """
        self.api_url = api_url
        self.api_key = api_key
        self.model = model
        self.timeout = timeout
        self.max_retries = max_retries
        self.session: Optional[aiohttp.ClientSession] = None
        self.request_cache: Dict[str, Any] = {}

    async def initialize(self) -> None:
        """Initialize HTTP session."""
        if self.session is None:
            self.session = aiohttp.ClientSession()
        logger.info("Genie API client initialized")

    async def close(self) -> None:
        """Close HTTP session."""
        if self.session:
            await self.session.close()
        logger.info("Genie API client closed")

    async def submit_task(
        self,
        prompt: str,
        task_type: str = "analysis",
        priority: str = "normal",
    ) -> str:
        """
        Submit a task to Genie API.

        Args:
            prompt: Prompt/instruction for Genie
            task_type: Type of task
            priority: Task priority (low, normal, high)

        Returns:
            Task ID for polling

        Raises:
            Exception: If submission fails
        """
        await self.initialize()

        task_id = str(uuid4())
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }

        payload = {
            "task_id": task_id,
            "model": self.model,
            "prompt": prompt,
            "task_type": task_type,
            "priority": priority,
        }

        try:
            async with self.session.post(
                f"{self.api_url}/submit",
                json=payload,
                headers=headers,
                timeout=aiohttp.ClientTimeout(total=30),
            ) as response:
                if response.status != 202:
                    raise Exception(f"Task submission failed: {response.status}")

                result = await response.json()
                logger.info(f"Task submitted with ID: {task_id}")
                return task_id

        except asyncio.TimeoutError:
            logger.error(f"Task submission timeout for {task_id}")
            raise
        except Exception as e:
            logger.error(f"Task submission error: {str(e)}")
            raise

    async def poll_task(
        self,
        task_id: str,
        initial_delay: int = 100,
        max_delay: int = 5000,
        max_attempts: int = 100,
    ) -> Dict[str, Any]:
        """
        Poll for task completion with exponential backoff.

        Args:
            task_id: Task ID to poll
            initial_delay: Initial polling delay in milliseconds
            max_delay: Maximum polling delay in milliseconds
            max_attempts: Maximum polling attempts

        Returns:
            Task result when completed

        Raises:
            Exception: If polling fails or times out
        """
        await self.initialize()

        delay = initial_delay
        attempt = 0
        headers = {"Authorization": f"Bearer {self.api_key}"}

        while attempt < max_attempts:
            try:
                async with self.session.get(
                    f"{self.api_url}/status/{task_id}",
                    headers=headers,
                    timeout=aiohttp.ClientTimeout(total=10),
                ) as response:
                    if response.status == 200:
                        result = await response.json()

                        if result.get("status") == "completed":
                            logger.info(f"Task {task_id} completed")
                            return result.get("result")

                        elif result.get("status") == "failed":
                            error = result.get("error", "Unknown error")
                            logger.error(f"Task {task_id} failed: {error}")
                            raise Exception(f"Task failed: {error}")

                        # Still processing
                        logger.debug(f"Task {task_id} in progress (attempt {attempt + 1})")

                    elif response.status == 404:
                        logger.error(f"Task {task_id} not found")
                        raise Exception(f"Task {task_id} not found")

                    else:
                        logger.warning(f"Unexpected status {response.status}")

            except asyncio.TimeoutError:
                logger.warning(f"Poll request timeout for {task_id}")
            except Exception as e:
                logger.error(f"Poll error for {task_id}: {str(e)}")

            # Wait before next poll (exponential backoff)
            await asyncio.sleep(min(delay, max_delay) / 1000.0)
            delay = int(delay * 1.5)
            attempt += 1

        raise Exception(f"Task {task_id} polling timed out after {max_attempts} attempts")

    async def execute(
        self,
        prompt: str,
        task_type: str = "analysis",
        priority: str = "normal",
    ) -> Dict[str, Any]:
        """
        Execute a task (submit and poll for completion).

        Args:
            prompt: Prompt for execution
            task_type: Type of task
            priority: Task priority

        Returns:
            Task result

        Raises:
            Exception: If execution fails
        """
        # Check cache
        cache_key = f"{hash(prompt)}:{task_type}"
        if cache_key in self.request_cache:
            logger.info(f"Cache hit for prompt hash: {cache_key}")
            return self.request_cache[cache_key]

        # Submit task
        task_id = await self.submit_task(prompt, task_type, priority)

        # Poll for completion
        result = await self.poll_task(task_id)

        # Cache result
        self.request_cache[cache_key] = result

        return result


class PollingManager:
    """Manager for polling configurations and strategies."""

    # Polling profiles with different strategies
    POLLING_PROFILES = {
        "fast": {
            "initial_delay": 100,
            "max_delay": 2000,
            "max_attempts": 50,
            "timeout": 60000,
        },
        "normal": {
            "initial_delay": 500,
            "max_delay": 5000,
            "max_attempts": 100,
            "timeout": 300000,
        },
        "slow": {
            "initial_delay": 1000,
            "max_delay": 10000,
            "max_attempts": 50,
            "timeout": 600000,
        },
    }

    @staticmethod
    def get_profile(profile_name: str) -> Dict[str, int]:
        """
        Get polling profile.

        Args:
            profile_name: Profile name (fast, normal, slow)

        Returns:
            Polling configuration
        """
        return PollingManager.POLLING_PROFILES.get(
            profile_name,
            PollingManager.POLLING_PROFILES["normal"]
        )


class RequestQueue:
    """Async-safe request queue with priority support."""

    def __init__(self):
        """Initialize request queue."""
        self.high_priority: asyncio.Queue = asyncio.Queue()
        self.normal_priority: asyncio.Queue = asyncio.Queue()
        self.low_priority: asyncio.Queue = asyncio.Queue()

    async def enqueue(
        self,
        task_id: str,
        request: Dict[str, Any],
        priority: str = "normal",
    ) -> None:
        """
        Enqueue a request.

        Args:
            task_id: Task identifier
            request: Request data
            priority: Priority level (low, normal, high)
        """
        queue_map = {
            "high": self.high_priority,
            "normal": self.normal_priority,
            "low": self.low_priority,
        }

        queue = queue_map.get(priority, self.normal_priority)
        await queue.put({"task_id": task_id, **request})

    async def dequeue(self) -> Optional[Dict[str, Any]]:
        """
        Dequeue a request (high priority first).

        Returns:
            Next request or None if all queues empty
        """
        # Try high priority first
        if not self.high_priority.empty():
            return self.high_priority.get_nowait()

        # Then normal
        if not self.normal_priority.empty():
            return self.normal_priority.get_nowait()

        # Then low
        if not self.low_priority.empty():
            return self.low_priority.get_nowait()

        return None
