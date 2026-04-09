"""
Pipeline management endpoints for data orchestration.
"""

import logging
from fastapi import APIRouter, HTTPException, status, Query

from app.services.databricks_service import get_databricks_service
from app.services.data_ingestion_service import get_data_ingestion_service

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/pipelines", tags=["pipelines"])


@router.get("/status", summary="Get pipeline status")
async def get_pipeline_status():
    """Get current pipeline and Databricks status."""
    try:
        db_service = get_databricks_service()
        status = await db_service.get_status()
        return {
            "status": "operational",
            "databricks": status,
            "timestamp": None
        }
    except Exception as e:
        logger.error(f"Error getting pipeline status: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.post("/initialize", summary="Initialize Databricks catalog and schema")
async def initialize_pipeline():
    """Initialize Databricks landscape (catalog + schema)."""
    try:
        db_service = get_databricks_service()
        
        # Create catalog
        catalog_result = await db_service.create_catalog()
        logger.info(f"Catalog result: {catalog_result}")
        
        # Create schema
        schema_result = await db_service.create_schema()
        logger.info(f"Schema result: {schema_result}")
        
        return {
            "status": "initialized",
            "catalog": catalog_result,
            "schema": schema_result
        }
    except Exception as e:
        logger.error(f"Error initializing pipeline: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.post("/create-tables", summary="Create data layer tables")
async def create_data_layers():
    """Create Bronze, Silver, and Gold layer tables."""
    try:
        db_service = get_databricks_service()
        
        # Create all three layers
        bronze = await db_service.create_bronze_table()
        silver = await db_service.create_silver_table()
        gold = await db_service.create_gold_table()
        
        return {
            "status": "tables_created",
            "layers": {
                "bronze": bronze,
                "silver": silver,
                "gold": gold
            }
        }
    except Exception as e:
        logger.error(f"Error creating data layers: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.get("/tables", summary="List all tables in schema")
async def list_tables():
    """Get all tables in the Databricks schema."""
    try:
        db_service = get_databricks_service()
        tables = await db_service.get_tables()
        return tables
    except Exception as e:
        logger.error(f"Error listing tables: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.post("/run-bronze", summary="Run Bronze layer ingestion")
async def run_bronze_pipeline(use_real_data: bool = Query(True, description="Use real data from yfinance (true) or sample data (false)")):
    """Trigger Bronze layer data ingestion.
    
    Parameters:
        use_real_data: Boolean flag to use real data (default: true)
    """
    try:
        db_service = get_databricks_service()
        ingestion_service = get_data_ingestion_service(db_service)
        
        result = await ingestion_service.ingest_bronze_data(use_real_data=use_real_data)
        return result
    except Exception as e:
        logger.error(f"Error running bronze pipeline: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.post("/run-silver", summary="Run Silver layer transformation")
async def run_silver_pipeline():
    """Trigger Silver layer data transformation."""
    try:
        db_service = get_databricks_service()
        ingestion_service = get_data_ingestion_service(db_service)
        
        result = await ingestion_service.transform_to_silver()
        return result
    except Exception as e:
        logger.error(f"Error running silver pipeline: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.post("/run-gold", summary="Run Gold layer aggregation")
async def run_gold_pipeline():
    """Trigger Gold layer data aggregation."""
    try:
        db_service = get_databricks_service()
        ingestion_service = get_data_ingestion_service(db_service)
        
        result = await ingestion_service.aggregate_to_gold()
        return result
    except Exception as e:
        logger.error(f"Error running gold pipeline: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.post("/full-run", summary="Run complete pipeline")
async def run_full_pipeline():
    """Run complete pipeline (Bronze -> Silver -> Gold)."""
    try:
        db_service = get_databricks_service()
        ingestion_service = get_data_ingestion_service(db_service)
        
        logger.info("Starting full pipeline execution: Bronze -> Silver -> Gold")
        
        # Execute Bronze (ingestion)
        bronze_result = await ingestion_service.ingest_bronze_data()
        if bronze_result["status"] != "success":
            return {
                "status": "failed",
                "message": "Bronze layer ingestion failed",
                "bronze": bronze_result
            }
        
        # Execute Silver (transformation)
        silver_result = await ingestion_service.transform_to_silver()
        if silver_result["status"] != "success":
            return {
                "status": "failed",
                "message": "Silver layer transformation failed",
                "bronze": bronze_result,
                "silver": silver_result
            }
        
        # Execute Gold (aggregation)
        gold_result = await ingestion_service.aggregate_to_gold()
        if gold_result["status"] != "success":
            return {
                "status": "failed",
                "message": "Gold layer aggregation failed",
                "bronze": bronze_result,
                "silver": silver_result,
                "gold": gold_result
            }
        
        logger.info("Full pipeline completed successfully")
        return {
            "status": "success",
            "message": "Full pipeline executed successfully (Bronze -> Silver -> Gold)",
            "results": {
                "bronze": bronze_result,
                "silver": silver_result,
                "gold": gold_result
            }
        }
    except Exception as e:
        logger.error(f"Error running full pipeline: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )
