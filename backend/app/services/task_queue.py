"""Task queue service for async task execution."""

import asyncio
from typing import Any, Callable, Dict, List, Optional
from app.utils.logger import get_logger
from datetime import datetime
import uuid

logger = get_logger(__name__)


class TaskQueueService:
    """Async task queue service."""
    
    def __init__(self, max_workers: int = 10):
        """Initialize task queue."""
        self.max_workers = max_workers
        self._queue: asyncio.Queue = asyncio.Queue()
        self._tasks: Dict[str, Dict[str, Any]] = {}
        self._workers_running = False
    
    async def submit_task(
        self,
        func: Callable,
        *args,
        task_name: str = None,
        **kwargs
    ) -> str:
        """
        Submit a task to the queue.
        
        Args:
            func: Async function to execute
            task_name: Optional task name
            *args: Function arguments
            **kwargs: Function keyword arguments
            
        Returns:
            Task ID
        """
        task_id = str(uuid.uuid4())
        task_info = {
            "id": task_id,
            "name": task_name or func.__name__,
            "func": func,
            "args": args,
            "kwargs": kwargs,
            "status": "queued",
            "created_at": datetime.utcnow(),
            "result": None,
            "error": None
        }
        
        self._tasks[task_id] = task_info
        await self._queue.put(task_info)
        
        logger.info(f"Task {task_id} ({task_name}) submitted to queue")
        return task_id
    
    async def get_task_status(self, task_id: str) -> Optional[Dict[str, Any]]:
        """Get task status."""
        if task_id not in self._tasks:
            return None
        
        task = self._tasks[task_id]
        return {
            "id": task["id"],
            "name": task["name"],
            "status": task["status"],
            "created_at": task["created_at"],
            "result": task["result"],
            "error": task["error"]
        }
    
    async def start_workers(self) -> None:
        """Start worker tasks."""
        if self._workers_running:
            return
        
        self._workers_running = True
        for i in range(self.max_workers):
            asyncio.create_task(self._worker(i))
        
        logger.info(f"Started {self.max_workers} task queue workers")
    
    async def _worker(self, worker_id: int) -> None:
        """Worker task processor."""
        while self._workers_running:
            try:
                task_info = await asyncio.wait_for(
                    self._queue.get(),
                    timeout=1.0
                )
                
                task_id = task_info["id"]
                logger.info(f"Worker {worker_id} processing task {task_id}")
                
                self._tasks[task_id]["status"] = "running"
                
                try:
                    result = await task_info["func"](
                        *task_info["args"],
                        **task_info["kwargs"]
                    )
                    self._tasks[task_id]["result"] = result
                    self._tasks[task_id]["status"] = "completed"
                    logger.info(f"Task {task_id} completed successfully")
                except Exception as e:
                    self._tasks[task_id]["error"] = str(e)
                    self._tasks[task_id]["status"] = "failed"
                    logger.error(f"Task {task_id} failed: {str(e)}")
                
            except asyncio.TimeoutError:
                continue
            except Exception as e:
                logger.error(f"Worker {worker_id} error: {str(e)}")
