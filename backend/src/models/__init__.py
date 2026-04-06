"""Data models for InsightGenie AI."""

from .stock import StockData, StockPrediction, AnalysisResult
from .request import AnalysisRequest, ToolRequest
from .response import APIResponse, ErrorResponse

__all__ = [
    "StockData",
    "StockPrediction",
    "AnalysisResult",
    "AnalysisRequest",
    "ToolRequest",
    "APIResponse",
    "ErrorResponse",
]
