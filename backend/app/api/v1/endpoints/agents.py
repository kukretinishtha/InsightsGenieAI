"""Agent-related endpoints."""

from fastapi import APIRouter, HTTPException
from typing import List
from app.models.agent import AgentTask, AgentResult, AgentConfig
from app.models.api import APIResponse
from app.agents import StockAnalyzerAgent, PredictorAgent
from app.utils.logger import get_logger
from datetime import datetime
import uuid

logger = get_logger(__name__)

router = APIRouter()

# Store agent instances
agents = {}


@router.get("/", response_model=APIResponse[dict])
async def list_agents():
    """List available agents."""
    logger.info("Listing available agents")
    
    available_agents = {
        "stock_analyzer": {
            "name": "Stock Analyzer",
            "type": "stock_analyzer",
            "description": "Analyzes stock market data"
        },
        "price_predictor": {
            "name": "Price Predictor",
            "type": "predictor",
            "description": "Predicts stock prices"
        }
    }
    
    return APIResponse(
        success=True,
        message="Available agents listed",
        data=available_agents,
        request_id=str(uuid.uuid4()),
        timestamp=datetime.utcnow().isoformat()
    )


@router.post("/task", response_model=APIResponse[AgentResult])
async def submit_agent_task(task: AgentTask):
    """Submit a task to an agent."""
    logger.info(f"Task submitted: {task.task_id} to agent {task.agent_name}")
    
    # Initialize agent if not exists
    if task.agent_name == "stock_analyzer":
        config = AgentConfig(
            name="stock_analyzer",
            description="Stock Analyzer",
            agent_type="stock_analyzer"
        )
        agent = StockAnalyzerAgent(config)
    elif task.agent_name == "price_predictor":
        config = AgentConfig(
            name="price_predictor",
            description="Price Predictor",
            agent_type="predictor"
        )
        agent = PredictorAgent(config)
    else:
        raise HTTPException(status_code=404, detail="Agent not found")
    
    # Execute task
    result = await agent.execute_task(task)
    
    return APIResponse(
        success=result.status == "success",
        message=f"Task {task.task_id} executed",
        data=result,
        request_id=str(uuid.uuid4()),
        timestamp=datetime.utcnow().isoformat()
    )
