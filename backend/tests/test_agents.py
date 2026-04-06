"""Unit tests for BaseAgent and tools."""

import pytest
import asyncio
from src.agents.base import BaseAgent, Tool


@pytest.fixture
async def sample_agent():
    """Create a sample agent for testing."""
    
    class TestAgent(BaseAgent):
        async def analyze(self, **kwargs):
            return {"result": "test"}
    
    agent = TestAgent()
    
    # Register test tools
    async def dummy_tool_1(**kwargs):
        await asyncio.sleep(0.1)
        return {"tool1": "result1"}
    
    async def dummy_tool_2(**kwargs):
        await asyncio.sleep(0.1)
        return {"tool2": "result2"}
    
    agent.register_tool("tool1", "Test tool 1", dummy_tool_1)
    agent.register_tool("tool2", "Test tool 2", dummy_tool_2)
    
    return agent


@pytest.mark.asyncio
async def test_tool_registration(sample_agent):
    """Test tool registration."""
    assert "tool1" in sample_agent.tools
    assert "tool2" in sample_agent.tools
    assert len(sample_agent.tools) == 2


@pytest.mark.asyncio
async def test_single_tool_execution(sample_agent):
    """Test executing a single tool."""
    result = await sample_agent.execute_tool("tool1")
    assert result == {"tool1": "result1"}


@pytest.mark.asyncio
async def test_parallel_tool_execution(sample_agent):
    """Test executing tools in parallel."""
    results = await sample_agent.execute_tools_parallel(
        ["tool1", "tool2"]
    )
    
    assert "tool1" in results
    assert "tool2" in results
    assert results["tool1"] == {"tool1": "result1"}
    assert results["tool2"] == {"tool2": "result2"}


@pytest.mark.asyncio
async def test_execution_history(sample_agent):
    """Test execution history tracking."""
    await sample_agent.execute_tool("tool1")
    await sample_agent.execute_tool("tool2")
    
    history = await sample_agent.get_execution_summary()
    
    assert history["tools_executed"] == 2
    assert history["successful"] == 2
    assert history["failed"] == 0


@pytest.mark.asyncio
async def test_tool_not_found_error(sample_agent):
    """Test error when tool not found."""
    with pytest.raises(ValueError):
        await sample_agent.execute_tool("nonexistent_tool")


@pytest.mark.asyncio
async def test_tool_timeout():
    """Test tool execution timeout."""
    
    class TimeoutAgent(BaseAgent):
        async def analyze(self, **kwargs):
            return {}
    
    agent = TimeoutAgent()
    
    async def slow_tool():
        await asyncio.sleep(5)
        return {"result": "timeout"}
    
    agent.register_tool(
        "slow_tool",
        "Slow tool",
        slow_tool,
        timeout=1  # 1 second timeout
    )
    
    with pytest.raises(asyncio.TimeoutError):
        await agent.execute_tool("slow_tool")
