"""Genie API client with polling support."""

import aiohttp
import asyncio
from typing import Any, Dict, Optional, List
from app.config import get_settings
from app.utils.logger import get_logger
from app.utils.exceptions import ExternalAPIError
from datetime import datetime, timedelta
import uuid

logger = get_logger(__name__)


class GenieAPIClient:
    """Async client for Genie API with polling support."""
    
    def __init__(self):
        """Initialize Genie API client."""
        self.settings = get_settings()
        self.base_url = self.settings.GENIE_API_BASE_URL
        self.api_key = self.settings.GENIE_API_KEY
        self.timeout = self.settings.GENIE_API_TIMEOUT
        self._session: Optional[aiohttp.ClientSession] = None
    
    async def __aenter__(self):
        """Async context manager entry."""
        self._session = aiohttp.ClientSession()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        if self._session:
            await self._session.close()
    
    def _get_headers(self) -> Dict[str, str]:
        """Get HTTP headers for API requests."""
        return {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
            "X-Request-ID": str(uuid.uuid4())
        }
    
    async def _get_session(self) -> aiohttp.ClientSession:
        """Get or create aiohttp session."""
        if self._session is None:
            self._session = aiohttp.ClientSession()
        return self._session
    
    async def submit_prediction_task(
        self,
        symbol: str,
        analysis_data: Dict[str, Any]
    ) -> str:
        """
        Submit a prediction task to Genie API.
        
        Args:
            symbol: Stock symbol
            analysis_data: Stock analysis data
            
        Returns:
            Task ID for polling
            
        Raises:
            ExternalAPIError: If API call fails
        """
        session = await self._get_session()
        
        payload = {
            "symbol": symbol,
            "analysis_data": analysis_data,
            "timestamp": datetime.utcnow().isoformat()
        }
        
        try:
            async with session.post(
                f"{self.base_url}/predictions/submit",
                json=payload,
                headers=self._get_headers(),
                timeout=aiohttp.ClientTimeout(total=self.timeout)
            ) as response:
                if response.status == 202:
                    data = await response.json()
                    task_id = data.get("task_id")
                    logger.info(f"Prediction task submitted with ID: {task_id}")
                    return task_id
                else:
                    raise ExternalAPIError(
                        message=f"Failed to submit prediction task",
                        api_name="GenieAPI",
                        status_code=response.status
                    )
        except aiohttp.ClientError as e:
            logger.error(f"Genie API connection error: {str(e)}")
            raise ExternalAPIError(
                message=f"Connection error to Genie API: {str(e)}",
                api_name="GenieAPI"
            ) from e
    
    async def poll_prediction_result(
        self,
        task_id: str,
        max_attempts: int = 30,
        poll_interval: int = 5
    ) -> Dict[str, Any]:
        """
        Poll for prediction result with exponential backoff.
        
        Args:
            task_id: Task ID from submit_prediction_task
            max_attempts: Maximum polling attempts
            poll_interval: Initial polling interval in seconds
            
        Returns:
            Prediction result
            
        Raises:
            ExternalAPIError: If polling fails or times out
        """
        session = await self._get_session()
        attempt = 0
        current_interval = poll_interval
        
        while attempt < max_attempts:
            try:
                async with session.get(
                    f"{self.base_url}/predictions/{task_id}",
                    headers=self._get_headers(),
                    timeout=aiohttp.ClientTimeout(total=self.timeout)
                ) as response:
                    if response.status == 200:
                        data = await response.json()
                        
                        if data.get("status") == "completed":
                            logger.info(f"Prediction task {task_id} completed")
                            return data.get("result", {})
                        
                        elif data.get("status") == "failed":
                            raise ExternalAPIError(
                                message=f"Prediction task failed: {data.get('error')}",
                                api_name="GenieAPI"
                            )
                    
                    elif response.status == 202:
                        # Still processing
                        logger.debug(f"Task {task_id} still processing, retrying...")
                    else:
                        raise ExternalAPIError(
                            message=f"Unexpected response status: {response.status}",
                            api_name="GenieAPI",
                            status_code=response.status
                        )
                
                # Wait before next attempt
                await asyncio.sleep(current_interval)
                current_interval = min(current_interval * 1.5, 30)  # Cap at 30 seconds
                attempt += 1
                
            except aiohttp.ClientError as e:
                logger.error(f"Polling error on attempt {attempt + 1}: {str(e)}")
                if attempt >= max_attempts - 1:
                    raise ExternalAPIError(
                        message=f"Polling failed after {max_attempts} attempts",
                        api_name="GenieAPI"
                    ) from e
                attempt += 1
        
        raise ExternalAPIError(
            message=f"Prediction task {task_id} timed out after {max_attempts} polling attempts",
            api_name="GenieAPI"
        )
    
    async def submit_and_poll(
        self,
        symbol: str,
        analysis_data: Dict[str, Any],
        max_wait_time: int = 300
    ) -> Dict[str, Any]:
        """
        Submit task and poll for result in one call.
        
        Args:
            symbol: Stock symbol
            analysis_data: Analysis data
            max_wait_time: Maximum wait time in seconds
            
        Returns:
            Prediction result
        """
        task_id = await self.submit_prediction_task(symbol, analysis_data)
        return await self.poll_prediction_result(
            task_id,
            max_attempts=max_wait_time // 5
        )
