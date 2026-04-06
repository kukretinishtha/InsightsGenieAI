"""Agent-related data models."""

from typing import Any, Dict, Optional, List
from pydantic import Field
from .base import BaseModel, TimestampedModel


class AgentConfig(BaseModel):
    """Configuration for an agent."""
    
    name: str = Field(..., description="Agent name")
    description: str = Field(..., description="Agent description")
    agent_type: str = Field(..., description="Type of agent (e.g., stock_analyzer, predictor)")
    tools: List[str] = Field(default_factory=list, description="Tools available to agent")
    max_iterations: int = Field(default=10, description="Maximum iterations per task")
    timeout_seconds: int = Field(default=300, description="Task timeout in seconds")
    parameters: Dict[str, Any] = Field(default_factory=dict, description="Agent-specific parameters")


class AgentTask(TimestampedModel):
    """Task for an agent to execute."""
    
    task_id: str = Field(..., description="Unique task identifier")
    agent_name: str = Field(..., description="Name of agent to execute task")
    task_type: str = Field(..., description="Type of task")
    input_data: Dict[str, Any] = Field(..., description="Task input data")
    status: str = Field(default="pending", description="Task status (pending, running, completed, failed)")
    priority: int = Field(default=5, ge=1, le=10, description="Task priority 1-10")
    tags: List[str] = Field(default_factory=list, description="Task tags for organization")


class AgentResult(TimestampedModel):
    """Result from agent task execution."""
    
    task_id: str = Field(..., description="Associated task ID")
    agent_name: str = Field(..., description="Agent that executed task")
    status: str = Field(..., description="Execution status (success/failure)")
    result: Dict[str, Any] = Field(..., description="Task result data")
    execution_time_seconds: float = Field(..., description="Time taken to execute")
    error_message: Optional[str] = Field(None, description="Error message if failed")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata")
