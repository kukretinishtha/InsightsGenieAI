"""Stock price predictor agent implementation."""

from typing import Any, Dict, Optional
from datetime import datetime
import random
from app.models.agent import AgentTask, AgentResult, AgentConfig
from app.utils.logger import get_logger
from .base_agent import BaseAgent, Tool

logger = get_logger(__name__)


class PredictorAgent(BaseAgent):
    """Agent for predicting stock prices."""
    
    def __init__(self, config: AgentConfig):
        """Initialize predictor agent."""
        super().__init__(config)
        
        # Register tools
        self.register_tool(Tool(
            name="get_historical_data",
            description="Get historical price data"
        ))
        self.register_tool(Tool(
            name="generate_prediction",
            description="Generate price prediction using models"
        ))
        self.register_tool(Tool(
            name="calculate_confidence",
            description="Calculate prediction confidence score"
        ))
    
    async def process_task(self, task: AgentTask) -> AgentResult:
        """
        Predict stock price.
        
        Args:
            task: Prediction task
            
        Returns:
            Prediction result
        """
        logger.info(f"PredictorAgent processing task: {task.task_id}")
        
        try:
            symbol = task.input_data.get("symbol")
            days_ahead = task.input_data.get("days_ahead", 7)
            
            if not symbol:
                return AgentResult(
                    task_id=task.task_id,
                    agent_name=self.name,
                    status="failed",
                    result={},
                    execution_time_seconds=0,
                    error_message="Symbol not provided in input_data"
                )
            
            # Get historical data
            historical_data = await self._get_historical_data(symbol)
            
            # Generate prediction
            prediction = await self._generate_prediction(
                symbol,
                historical_data,
                days_ahead
            )
            
            result = {
                "symbol": symbol,
                "prediction": prediction,
                "historical_data_points": len(historical_data),
                "generated_at": datetime.utcnow().isoformat()
            }
            
            return AgentResult(
                task_id=task.task_id,
                agent_name=self.name,
                status="success",
                result=result,
                execution_time_seconds=0
            )
            
        except Exception as e:
            logger.error(f"Error in PredictorAgent: {str(e)}")
            return AgentResult(
                task_id=task.task_id,
                agent_name=self.name,
                status="failed",
                result={},
                execution_time_seconds=0,
                error_message=str(e)
            )
    
    async def _get_historical_data(self, symbol: str) -> list:
        """Get historical price data."""
        # Simulated historical data
        return [
            {"date": f"2024-01-{i:02d}", "price": 150.0 + random.uniform(-10, 10)}
            for i in range(1, 31)
        ]
    
    async def _generate_prediction(
        self,
        symbol: str,
        historical_data: list,
        days_ahead: int
    ) -> Dict[str, Any]:
        """Generate price prediction."""
        current_price = 150.0
        predicted_price = current_price * (1 + random.uniform(-0.05, 0.10))
        
        return {
            "symbol": symbol,
            "current_price": current_price,
            "predicted_price": round(predicted_price, 2),
            "days_ahead": days_ahead,
            "confidence": round(random.uniform(0.6, 0.95), 2),
            "recommendation": self._get_recommendation(current_price, predicted_price)
        }
    
    def _get_recommendation(self, current: float, predicted: float) -> str:
        """Get buy/sell/hold recommendation."""
        change = (predicted - current) / current
        if change > 0.05:
            return "BUY"
        elif change < -0.05:
            return "SELL"
        else:
            return "HOLD"
