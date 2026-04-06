"""Base agent abstract class."""

from abc import ABC, abstractmethod
from typing import Any, Dict, Optional, List
import asyncio
import uuid
from datetime import datetime
from app.models.agent import AgentTask, AgentResult, AgentConfig
from app.utils.logger import get_logger
from app.utils.exceptions import TaskExecutionError

logger = get_logger(__name__)


class Tool:
    """Tool descriptor for agents."""
    
    def __init__(
        self,
        name: str,
        description: str,
        async_func: Optional[Any] = None,
    ):
        """Initialize tool."""
        self.name = name
        self.description = description
        self.async_func = async_func
    
    async def execute(self, **kwargs: Any) -> Any:
        """Execute tool asynchronously."""
        if self.async_func is None:
            raise NotImplementedError(f"Tool {self.name} not implemented")
        return await self.async_func(**kwargs)


class BaseAgent(ABC):
    """Abstract base class for all agents."""
    
    def __init__(self, config: AgentConfig):
        """
        Initialize agent.
        
        Args:
            config: Agent configuration
        """
        self.config = config
        self.name = config.name
        self.agent_type = config.agent_type
        self.max_iterations = config.max_iterations
        self.timeout_seconds = config.timeout_seconds
        self.parameters = config.parameters
        self._tools: Dict[str, Tool] = {}
        self._execution_history: List[Dict[str, Any]] = []
        
        logger.info(f"Initialized agent: {self.name} (type: {self.agent_type})")
    
    @abstractmethod
    async def process_task(
        self,
        task: AgentTask
    ) -> AgentResult:
        """
        Process a task. Must be implemented by subclasses.
        
        Args:
            task: Task to process
            
        Returns:
            Agent result with execution output
        """
        pass
    
    def register_tool(self, tool: Tool) -> None:
        """
        Register a tool for this agent.
        
        Args:
            tool: Tool to register
        """
        self._tools[tool.name] = tool
        logger.debug(f"Registered tool '{tool.name}' for agent '{self.name}'")
    
    async def use_tool(
        self,
        tool_name: str,
        **kwargs: Any
    ) -> Any:
        """
        Use a registered tool.
        
        Args:
            tool_name: Name of tool to use
            **kwargs: Tool arguments
            
        Returns:
            Tool execution result
            
        Raises:
            TaskExecutionError: If tool not found
        """
        if tool_name not in self._tools:
            raise TaskExecutionError(
                message=f"Tool '{tool_name}' not found",
                task_name=self.name
            )
        
        tool = self._tools[tool_name]
        logger.debug(f"Executing tool '{tool_name}' for agent '{self.name}'")
        
        try:
            result = await tool.execute(**kwargs)
            return result
        except Exception as e:
            logger.error(f"Tool '{tool_name}' execution failed: {str(e)}")
            raise TaskExecutionError(
                message=f"Tool execution failed: {str(e)}",
                task_name=tool_name,
                details={"agent": self.name}
            ) from e
    
    async def execute_task(
        self,
        task: AgentTask
    ) -> AgentResult:
        """
        Execute a task with timeout and error handling.
        
        Args:
            task: Task to execute
            
        Returns:
            Agent result
        """
        start_time = datetime.utcnow()
        
        try:
            # Execute task with timeout
            result = await asyncio.wait_for(
                self.process_task(task),
                timeout=self.timeout_seconds
            )
            
            execution_time = (datetime.utcnow() - start_time).total_seconds()
            
            self._execution_history.append({
                "task_id": task.task_id,
                "status": "success",
                "execution_time": execution_time,
                "timestamp": datetime.utcnow()
            })
            
            return result
            
        except asyncio.TimeoutError:
            logger.error(f"Task {task.task_id} timed out after {self.timeout_seconds}s")
            execution_time = (datetime.utcnow() - start_time).total_seconds()
            
            return AgentResult(
                task_id=task.task_id,
                agent_name=self.name,
                status="failed",
                result={},
                execution_time_seconds=execution_time,
                error_message=f"Task timed out after {self.timeout_seconds} seconds"
            )
        
        except Exception as e:
            logger.error(f"Task {task.task_id} failed: {str(e)}", exc_info=True)
            execution_time = (datetime.utcnow() - start_time).total_seconds()
            
            return AgentResult(
                task_id=task.task_id,
                agent_name=self.name,
                status="failed",
                result={},
                execution_time_seconds=execution_time,
                error_message=str(e)
            )
    
    def get_execution_history(self) -> List[Dict[str, Any]]:
        """Get agent execution history."""
        return self._execution_history.copy()
    
    def clear_execution_history(self) -> None:
        """Clear execution history."""
        self._execution_history.clear()
    
    async def health_check(self) -> Dict[str, Any]:
        """
        Check agent health.
        
        Returns:
            Health status dictionary
        """
        return {
            "agent_name": self.name,
            "agent_type": self.agent_type,
            "status": "healthy",
            "tools_count": len(self._tools),
            "executions": len(self._execution_history),
            "timestamp": datetime.utcnow()
        }
