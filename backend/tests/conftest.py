"""Pytest configuration and fixtures."""

import pytest
import asyncio
from app.config import get_settings
from app.agents import StockAnalyzerAgent, PredictorAgent
from app.models.agent import AgentConfig


@pytest.fixture
def event_loop():
    """Create event loop for async tests."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture
def settings():
    """Get application settings."""
    return get_settings()


@pytest.fixture
def stock_analyzer_agent():
    """Create stock analyzer agent instance."""
    config = AgentConfig(
        name="test_stock_analyzer",
        description="Test Stock Analyzer",
        agent_type="stock_analyzer"
    )
    return StockAnalyzerAgent(config)


@pytest.fixture
def predictor_agent():
    """Create predictor agent instance."""
    config = AgentConfig(
        name="test_predictor",
        description="Test Predictor",
        agent_type="predictor"
    )
    return PredictorAgent(config)
