"""Unit tests for agents."""

import pytest
from app.agents import StockAnalyzerAgent, PredictorAgent
from app.models.agent import AgentTask, AgentConfig
import uuid


@pytest.mark.asyncio
async def test_stock_analyzer_agent_initialization():
    """Test stock analyzer agent initialization."""
    config = AgentConfig(
        name="test_analyzer",
        description="Test Analyzer",
        agent_type="stock_analyzer"
    )
    agent = StockAnalyzerAgent(config)
    
    assert agent.name == "test_analyzer"
    assert agent.agent_type == "stock_analyzer"
    assert len(agent._tools) == 4


@pytest.mark.asyncio
async def test_stock_analyzer_process_task(stock_analyzer_agent):
    """Test stock analyzer task processing."""
    task = AgentTask(
        task_id=str(uuid.uuid4()),
        agent_name="stock_analyzer",
        task_type="analyze",
        input_data={"symbol": "AAPL"}
    )
    
    result = await stock_analyzer_agent.process_task(task)
    
    assert result.status == "success"
    assert result.task_id == task.task_id
    assert "symbol" in result.result


@pytest.mark.asyncio
async def test_predictor_agent_initialization():
    """Test predictor agent initialization."""
    config = AgentConfig(
        name="test_predictor",
        description="Test Predictor",
        agent_type="predictor"
    )
    agent = PredictorAgent(config)
    
    assert agent.name == "test_predictor"
    assert agent.agent_type == "predictor"
    assert len(agent._tools) == 3


@pytest.mark.asyncio
async def test_predictor_process_task(predictor_agent):
    """Test predictor task processing."""
    task = AgentTask(
        task_id=str(uuid.uuid4()),
        agent_name="price_predictor",
        task_type="predict",
        input_data={"symbol": "AAPL", "days_ahead": 7}
    )
    
    result = await predictor_agent.process_task(task)
    
    assert result.status == "success"
    assert "prediction" in result.result


@pytest.mark.asyncio
async def test_agent_missing_symbol_input(stock_analyzer_agent):
    """Test agent handling of missing input."""
    task = AgentTask(
        task_id=str(uuid.uuid4()),
        agent_name="stock_analyzer",
        task_type="analyze",
        input_data={}  # Missing symbol
    )
    
    result = await stock_analyzer_agent.process_task(task)
    
    assert result.status == "failed"
    assert "Symbol not provided" in result.error_message


@pytest.mark.asyncio
async def test_agent_execution_history(stock_analyzer_agent):
    """Test agent execution history tracking."""
    task = AgentTask(
        task_id=str(uuid.uuid4()),
        agent_name="stock_analyzer",
        task_type="analyze",
        input_data={"symbol": "AAPL"}
    )
    
    await stock_analyzer_agent.execute_task(task)
    
    history = stock_analyzer_agent.get_execution_history()
    assert len(history) == 1
    assert history[0]["task_id"] == task.task_id
