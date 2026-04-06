"""Request data models."""

from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field


class AnalysisRequest(BaseModel):
    """Request to analyze a stock."""

    symbol: str = Field(..., description="Stock symbol to analyze")
    analysis_type: str = Field(
        default="comprehensive",
        description="Type of analysis: quick, standard, comprehensive"
    )
    timeframe_days: int = Field(default=60, description="Analysis timeframe in days")
    include_technical: bool = Field(default=True, description="Include technical analysis")
    include_fundamental: bool = Field(default=True, description="Include fundamental analysis")
    include_sentiment: bool = Field(default=True, description="Include sentiment analysis")
    include_geopolitical: bool = Field(default=True, description="Include geopolitical analysis")
    
    class Config:
        json_schema_extra = {
            "example": {
                "symbol": "RELIANCE",
                "analysis_type": "comprehensive",
                "timeframe_days": 60,
                "include_technical": True,
                "include_sentiment": True,
                "include_geopolitical": True,
            }
        }


class ToolRequest(BaseModel):
    """Request to execute a specific tool."""

    tool_name: str = Field(..., description="Name of the tool to execute")
    parameters: Dict[str, Any] = Field(default={}, description="Tool parameters")
    timeout: int = Field(default=300, description="Execution timeout in seconds")
    
    class Config:
        json_schema_extra = {
            "example": {
                "tool_name": "fetch_nse_data",
                "parameters": {"symbol": "RELIANCE"},
                "timeout": 30,
            }
        }


class BatchAnalysisRequest(BaseModel):
    """Request to analyze multiple stocks in batch."""

    symbols: List[str] = Field(..., description="List of stock symbols")
    analysis_type: str = Field(default="standard")
    parallel_processing: bool = Field(default=True)
    
    class Config:
        json_schema_extra = {
            "example": {
                "symbols": ["RELIANCE", "TCS", "INFY"],
                "analysis_type": "standard",
                "parallel_processing": True,
            }
        }
