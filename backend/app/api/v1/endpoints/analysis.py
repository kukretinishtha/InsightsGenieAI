"""
Analysis endpoints for AI-powered stock insights and recommendations.
"""

import logging
from fastapi import APIRouter, HTTPException, status

from app.services.databricks_service import get_databricks_service
from app.services.analysis_service import get_analysis_service

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/analysis", tags=["analysis"])


@router.get("/trends", summary="Get trend analysis")
async def get_trends():
    """Analyze stock trends from Gold layer data."""
    try:
        db_service = get_databricks_service()
        analysis_service = get_analysis_service(db_service)
        result = await analysis_service.get_trend_analysis()
        return result
    except Exception as e:
        logger.error(f"Error getting trends: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.get("/signals", summary="Get buy/sell signals")
async def get_signals():
    """Generate buy/sell/hold signals based on Gold layer insights."""
    try:
        db_service = get_databricks_service()
        analysis_service = get_analysis_service(db_service)
        result = await analysis_service.get_buy_sell_signals()
        return result
    except Exception as e:
        logger.error(f"Error getting signals: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.get("/risk", summary="Get risk assessment")
async def get_risk():
    """Assess risk levels based on volatility and market conditions."""
    try:
        db_service = get_databricks_service()
        analysis_service = get_analysis_service(db_service)
        result = await analysis_service.get_risk_assessment()
        return result
    except Exception as e:
        logger.error(f"Error getting risk assessment: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.get("/portfolio", summary="Get portfolio recommendations")
async def get_portfolio():
    """Generate portfolio recommendations based on Gold layer data."""
    try:
        db_service = get_databricks_service()
        analysis_service = get_analysis_service(db_service)
        result = await analysis_service.get_portfolio_recommendations()
        return result
    except Exception as e:
        logger.error(f"Error getting portfolio recommendations: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.get("/complete", summary="Run complete analysis")
async def get_complete():
    """Run complete analysis pipeline (trends + signals + risk + portfolio)."""
    try:
        db_service = get_databricks_service()
        analysis_service = get_analysis_service(db_service)
        result = await analysis_service.get_complete_analysis()
        return result
    except Exception as e:
        logger.error(f"Error running complete analysis: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )
