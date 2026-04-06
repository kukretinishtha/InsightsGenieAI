"""Data models for InsightGenie AI."""

from .base import BaseModel
from .stock import StockPrediction, StockAnalysis, MarketData
from .agent import AgentTask, AgentResult, AgentConfig
from .api import APIResponse, ErrorResponse, PaginatedResponse

__all__ = [
    "BaseModel",
    "StockPrediction",
    "StockAnalysis",
    "MarketData",
    "AgentTask",
    "AgentResult",
    "AgentConfig",
    "APIResponse",
    "ErrorResponse",
    "PaginatedResponse",
]
