"""Base agent class for InsightGenie AI."""

import asyncio
import logging
from abc import ABC, abstractmethod
from datetime import datetime
from typing import Any, Dict, List, Optional
from uuid import uuid4


logger = logging.getLogger(__name__)


class Tool:
    """Represents a tool that an agent can execute."""

    def __init__(
        self,
        name: str,
        description: str,
        func: callable,
        timeout: int = 300,
    ):
        """
        Initialize a tool.

        Args:
            name: Tool name
            description: Tool description
            func: Async function to execute
            timeout: Execution timeout in seconds
        """
        self.name = name
        self.description = description
        self.func = func
        self.timeout = timeout

    async def execute(self, **kwargs) -> Any:
        """
        Execute the tool with timeout protection.

        Args:
            **kwargs: Tool parameters

        Returns:
            Tool execution result

        Raises:
            asyncio.TimeoutError: If tool execution exceeds timeout
        """
        try:
            result = await asyncio.wait_for(
                self.func(**kwargs),
                timeout=self.timeout
            )
            return result
        except asyncio.TimeoutError:
            logger.error(f"Tool {self.name} timed out after {self.timeout}s")
            raise
        except Exception as e:
            logger.error(f"Tool {self.name} execution failed: {str(e)}")
            raise


class BaseAgent(ABC):
    """Abstract base class for all agents."""

    def __init__(self, agent_id: Optional[str] = None):
        """
        Initialize the agent.

        Args:
            agent_id: Optional agent identifier
        """
        self.agent_id = agent_id or f"agent_{str(uuid4())[:8]}"
        self.logger = logging.getLogger(f"Agent:{self.agent_id}")
        self.tools: Dict[str, Tool] = {}
        self.execution_history: List[Dict[str, Any]] = []
        self.start_time = datetime.utcnow()

    def register_tool(
        self,
        name: str,
        description: str,
        func: callable,
        timeout: int = 300,
    ) -> None:
        """
        Register a tool that the agent can use.

        Args:
            name: Tool name
            description: Tool description
            func: Async function to execute
            timeout: Execution timeout
        """
        tool = Tool(name, description, func, timeout)
        self.tools[name] = tool
        self.logger.info(f"Tool registered: {name}")

    async def execute_tool(self, tool_name: str, **kwargs) -> Any:
        """
        Execute a specific tool.

        Args:
            tool_name: Name of the tool to execute
            **kwargs: Tool parameters

        Returns:
            Tool result

        Raises:
            ValueError: If tool not found
        """
        if tool_name not in self.tools:
            raise ValueError(f"Tool {tool_name} not found")

        tool = self.tools[tool_name]
        self.logger.info(f"Executing tool: {tool_name}")

        try:
            start_time = datetime.utcnow()
            result = await tool.execute(**kwargs)
            elapsed = (datetime.utcnow() - start_time).total_seconds()

            # Record execution
            self.execution_history.append({
                "tool": tool_name,
                "timestamp": start_time,
                "duration_seconds": elapsed,
                "status": "success",
            })

            self.logger.info(f"Tool {tool_name} completed in {elapsed:.2f}s")
            return result

        except Exception as e:
            self.logger.error(f"Tool {tool_name} failed: {str(e)}")
            self.execution_history.append({
                "tool": tool_name,
                "timestamp": datetime.utcnow(),
                "status": "error",
                "error": str(e),
            })
            raise

    async def execute_tools_parallel(
        self,
        tool_names: List[str],
        **kwargs
    ) -> Dict[str, Any]:
        """
        Execute multiple tools in parallel.

        Args:
            tool_names: List of tool names to execute
            **kwargs: Parameters for all tools

        Returns:
            Dictionary mapping tool names to results

        Raises:
            ValueError: If any tool not found
        """
        # Validate all tools exist
        for tool_name in tool_names:
            if tool_name not in self.tools:
                raise ValueError(f"Tool {tool_name} not found")

        self.logger.info(f"Executing {len(tool_names)} tools in parallel")

        # Create tasks for all tools
        tasks = [
            self.execute_tool(tool_name, **kwargs)
            for tool_name in tool_names
        ]

        # Execute in parallel
        try:
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            # Build result dictionary
            result_dict = {}
            for tool_name, result in zip(tool_names, results):
                if isinstance(result, Exception):
                    self.logger.error(f"Tool {tool_name} raised exception: {result}")
                    result_dict[tool_name] = {"error": str(result)}
                else:
                    result_dict[tool_name] = result

            return result_dict

        except Exception as e:
            self.logger.error(f"Parallel execution failed: {str(e)}")
            raise

    @abstractmethod
    async def analyze(self, **kwargs) -> Dict[str, Any]:
        """
        Perform analysis using the agent's tools.

        Args:
            **kwargs: Analysis parameters

        Returns:
            Analysis result
        """
        pass

    async def get_execution_summary(self) -> Dict[str, Any]:
        """
        Get a summary of execution history.

        Returns:
            Execution summary
        """
        total_duration = (datetime.utcnow() - self.start_time).total_seconds()
        successful = sum(1 for h in self.execution_history if h.get("status") == "success")
        failed = sum(1 for h in self.execution_history if h.get("status") == "error")

        return {
            "agent_id": self.agent_id,
            "total_duration_seconds": total_duration,
            "tools_executed": len(self.execution_history),
            "successful": successful,
            "failed": failed,
            "execution_history": self.execution_history,
        }
