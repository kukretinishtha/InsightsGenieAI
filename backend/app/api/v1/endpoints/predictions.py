"""Stock prediction endpoints."""

from fastapi import APIRouter
from typing import Optional
from app.models.api import APIResponse
from app.utils.logger import get_logger
from datetime import datetime
import uuid
import random

logger = get_logger(__name__)

router = APIRouter()


@router.post("/predict/{symbol}", response_model=APIResponse[dict])
async def predict_stock_price(
    symbol: str,
    days_ahead: int = 7,
    model: str = "ensemble"
):
    """Predict stock price."""
    logger.info(f"Predicting price for {symbol} {days_ahead} days ahead")
    
    # Simulated prediction
    current_price = 150.0
    predicted_price = current_price * (1 + random.uniform(-0.05, 0.10))
    
    prediction = {
        "symbol": symbol,
        "current_price": current_price,
        "predicted_price": round(predicted_price, 2),
        "days_ahead": days_ahead,
        "confidence": round(random.uniform(0.6, 0.95), 2),
        "model_used": model,
        "factors": ["momentum", "volume", "technical indicators"]
    }
    
    return APIResponse(
        success=True,
        message=f"Price prediction for {symbol} generated",
        data=prediction,
        request_id=str(uuid.uuid4()),
        timestamp=datetime.utcnow().isoformat()
    )
