"""API v1 endpoints."""

from fastapi import APIRouter
from .endpoints import health, stocks, agents, predictions

router = APIRouter(prefix="/api/v1")

router.include_router(health.router, prefix="/health", tags=["Health"])
router.include_router(stocks.router, prefix="/stocks", tags=["Stocks"])
router.include_router(agents.router, prefix="/agents", tags=["Agents"])
router.include_router(predictions.router, prefix="/predictions", tags=["Predictions"])

__all__ = ["router"]
