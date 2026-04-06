"""Analysis API routes."""

import logging
from datetime import datetime
from typing import List, Optional
from uuid import uuid4

from fastapi import APIRouter, HTTPException, BackgroundTasks
from pydantic import BaseModel

from src.models.request import AnalysisRequest, BatchAnalysisRequest
from src.models.response import APIResponse
from src.models.stock import AnalysisResult
from src.orchestrator import get_orchestrator

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api", tags=["analysis"])

# Pydantic models for requests/responses
class AnalysisStatusResponse(BaseModel):
    """Response for analysis status check."""
    request_id: str
    symbol: str
    status: str
    analysis_type: str
    started_at: datetime
    completed_at: Optional[datetime] = None
    error: Optional[str] = None
    result: Optional[AnalysisResult] = None


@router.post("/analyze", response_model=APIResponse)
async def analyze_stock(
    request: AnalysisRequest,
    background_tasks: BackgroundTasks
) -> APIResponse:
    """
    Submit a stock analysis request.
    
    Returns a request_id for polling status.
    
    Args:
        request: AnalysisRequest with symbol and parameters
        background_tasks: Background task executor
    
    Returns:
        APIResponse with request_id
    """
    
    try:
        request_id = str(uuid4())
        
        logger.info(f"Received analysis request for {request.symbol} (id={request_id})")
        
        # Get orchestrator
        orchestrator = await get_orchestrator()
        
        # Run analysis in background
        async def run_analysis():
            try:
                result = await orchestrator.analyze_stock(
                    request.symbol,
                    analysis_type=request.analysis_type
                )
                
                if result:
                    logger.info(f"Analysis completed for {request.symbol} (id={request_id})")
                else:
                    logger.warning(f"Analysis returned None for {request.symbol}")
            
            except Exception as e:
                logger.error(f"Background analysis failed: {e}", exc_info=True)
        
        # Start analysis in background
        background_tasks.add_task(run_analysis)
        
        return APIResponse(
            success=True,
            data={"request_id": request_id},
            message=f"Analysis request submitted for {request.symbol}"
        )
    
    except Exception as e:
        logger.error(f"Error submitting analysis request: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/analyze/{request_id}", response_model=APIResponse)
async def get_analysis_status(request_id: str) -> APIResponse:
    """
    Get status and results of an analysis request.
    
    Args:
        request_id: ID from the analysis request
    
    Returns:
        APIResponse with status and result if completed
    """
    
    try:
        orchestrator = await get_orchestrator()
        
        job = orchestrator.get_job_status(request_id)
        
        if not job:
            raise HTTPException(
                status_code=404,
                detail=f"Request {request_id} not found"
            )
        
        return APIResponse(
            success=True,
            data=job,
            message=f"Request {request_id} status: {job.get('status')}"
        )
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting analysis status: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/batch-analyze", response_model=APIResponse)
async def analyze_portfolio(
    request: BatchAnalysisRequest,
    background_tasks: BackgroundTasks
) -> APIResponse:
    """
    Submit batch analysis for multiple stocks.
    
    Args:
        request: BatchAnalysisRequest with list of symbols
        background_tasks: Background task executor
    
    Returns:
        APIResponse with request_id for polling
    """
    
    try:
        request_id = str(uuid4())
        
        logger.info(f"Received batch analysis for {len(request.symbols)} stocks (id={request_id})")
        
        if len(request.symbols) > 100:
            raise HTTPException(
                status_code=400,
                detail="Maximum 100 symbols per batch"
            )
        
        orchestrator = await get_orchestrator()
        
        async def run_batch_analysis():
            try:
                results = await orchestrator.analyze_portfolio(
                    request.symbols,
                    analysis_type=request.analysis_type
                )
                
                logger.info(f"Batch analysis completed (id={request_id})")
            
            except Exception as e:
                logger.error(f"Batch analysis failed: {e}", exc_info=True)
        
        # Start batch analysis in background
        background_tasks.add_task(run_batch_analysis)
        
        return APIResponse(
            success=True,
            data={
                "request_id": request_id,
                "symbol_count": len(request.symbols)
            },
            message=f"Batch analysis submitted for {len(request.symbols)} stocks"
        )
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error submitting batch analysis: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/jobs", response_model=APIResponse)
async def list_jobs() -> APIResponse:
    """
    List all analysis jobs.
    
    Returns:
        APIResponse with list of jobs
    """
    
    try:
        orchestrator = await get_orchestrator()
        
        jobs = orchestrator.get_all_jobs()
        
        return APIResponse(
            success=True,
            data={
                "total_jobs": len(jobs),
                "jobs": jobs
            },
            message=f"Found {len(jobs)} analysis jobs"
        )
    
    except Exception as e:
        logger.error(f"Error listing jobs: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/data/bronze/{symbol}", response_model=APIResponse)
async def get_bronze_data(symbol: str) -> APIResponse:
    """
    Get raw Bronze layer data for a symbol.
    
    Args:
        symbol: Stock symbol
    
    Returns:
        APIResponse with bronze layer data
    """
    
    try:
        from src.data.pipeline import get_pipeline
        
        pipeline = await get_pipeline()
        
        # Fetch bronze data
        bronze = await pipeline._fetch_bronze_data(symbol)
        
        if not bronze:
            raise HTTPException(
                status_code=404,
                detail=f"No data found for {symbol}"
            )
        
        return APIResponse(
            success=True,
            data=bronze.dict(),
            message=f"Bronze layer data for {symbol}"
        )
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching bronze data: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/data/silver/{symbol}", response_model=APIResponse)
async def get_silver_data(symbol: str) -> APIResponse:
    """
    Get cleaned Silver layer data for a symbol.
    
    Args:
        symbol: Stock symbol
    
    Returns:
        APIResponse with silver layer data
    """
    
    try:
        pipeline = await get_pipeline()
        
        # Check silver cache
        silver = await pipeline.silver_cache.get(f"silver:{symbol}")
        
        if not silver:
            # Generate silver data from bronze
            bronze = await pipeline._fetch_bronze_data(symbol)
            
            if not bronze:
                raise HTTPException(
                    status_code=404,
                    detail=f"No data found for {symbol}"
                )
            
            silver = await pipeline._transform_to_silver(symbol, bronze)
        
        return APIResponse(
            success=True,
            data=silver.dict(),
            message=f"Silver layer data for {symbol}"
        )
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching silver data: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/data/gold/{symbol}", response_model=APIResponse)
async def get_gold_data(symbol: str) -> APIResponse:
    """
    Get enriched Gold layer data for a symbol.
    
    Args:
        symbol: Stock symbol
    
    Returns:
        APIResponse with gold layer data
    """
    
    try:
        pipeline = await get_pipeline()
        
        gold = await pipeline.get_stock_analysis(symbol)
        
        if not gold:
            raise HTTPException(
                status_code=404,
                detail=f"No analysis available for {symbol}"
            )
        
        return APIResponse(
            success=True,
            data=gold.dict(),
            message=f"Gold layer data for {symbol}"
        )
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching gold data: {e}")
        raise HTTPException(status_code=500, detail=str(e))
