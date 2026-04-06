"""Development utility functions."""

import asyncio
from app.agents import StockAnalyzerAgent, PredictorAgent
from app.models.agent import AgentConfig, AgentTask
from app.services import CacheService, TaskQueueService
import uuid


async def test_stock_analyzer():
    """Test stock analyzer agent."""
    print("\n=== Testing Stock Analyzer Agent ===")
    
    config = AgentConfig(
        name="test_analyzer",
        description="Test Stock Analyzer",
        agent_type="stock_analyzer"
    )
    agent = StockAnalyzerAgent(config)
    
    task = AgentTask(
        task_id=str(uuid.uuid4()),
        agent_name="test_analyzer",
        task_type="analyze",
        input_data={"symbol": "AAPL"}
    )
    
    result = await agent.execute_task(task)
    print(f"Status: {result.status}")
    print(f"Result: {result.result}")
    print(f"Execution time: {result.execution_time_seconds}s")


async def test_price_predictor():
    """Test price predictor agent."""
    print("\n=== Testing Price Predictor Agent ===")
    
    config = AgentConfig(
        name="test_predictor",
        description="Test Predictor",
        agent_type="predictor"
    )
    agent = PredictorAgent(config)
    
    task = AgentTask(
        task_id=str(uuid.uuid4()),
        agent_name="test_predictor",
        task_type="predict",
        input_data={"symbol": "AAPL", "days_ahead": 7}
    )
    
    result = await agent.execute_task(task)
    print(f"Status: {result.status}")
    print(f"Result: {result.result}")
    print(f"Execution time: {result.execution_time_seconds}s")


async def test_cache_service():
    """Test cache service."""
    print("\n=== Testing Cache Service ===")
    
    cache = CacheService(max_size=100, ttl_seconds=3600)
    
    # Test set and get
    await cache.set("AAPL", {"price": 150.00})
    value = await cache.get("AAPL")
    print(f"Cached value: {value}")
    
    # Test delete
    await cache.delete("AAPL")
    value = await cache.get("AAPL")
    print(f"After delete: {value}")


async def run_all_tests():
    """Run all development tests."""
    print("\nInsightGenie AI - Development Tests")
    print("=" * 50)
    
    try:
        await test_stock_analyzer()
        await test_price_predictor()
        await test_cache_service()
        
        print("\n" + "=" * 50)
        print("All tests completed successfully!")
    except Exception as e:
        print(f"\nError during testing: {str(e)}")
        raise


if __name__ == "__main__":
    asyncio.run(run_all_tests())
