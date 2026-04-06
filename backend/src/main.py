"""
Main FastAPI application for InsightGenie AI backend.
"""

import asyncio
import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from src.config import settings
from src.utils import setup_logging, get_logger
from src.models import APIResponse, ErrorResponse
from src.utils.exceptions import InsightGenieException
from src.orchestrator import get_orchestrator, close_orchestrator
from src.data.pipeline import get_pipeline, close_pipeline
from src.routes.analysis import router as analysis_router

# Setup logging
setup_logging(
    log_level=settings.log_level,
    log_file=settings.log_file,
    log_format=settings.log_format,
)

logger = get_logger(__name__)


# Lifespan event handler
@asynccontextmanager
async def lifespan(app: FastAPI):
    """Manage application startup and shutdown."""
    logger.info("Application starting up...")
    
    # Initialize orchestrator and pipeline
    try:
        orchestrator = await get_orchestrator()
        pipeline = await get_pipeline()
        logger.info("Orchestrator and pipeline initialized")
    except Exception as e:
        logger.error(f"Failed to initialize orchestrator/pipeline: {e}")
    
    # Initialize Databricks if enabled
    if settings.enable_databricks:
        try:
            from src.data.databricks_client import get_databricks_client
            from src.data.databricks_pipeline import get_databricks_pipeline
            from src.genie import get_genie_manager
            
            # Initialize Databricks client
            db_client = get_databricks_client(
                host=settings.databricks_host,
                token=settings.databricks_token,
                catalog=settings.databricks_catalog,
                schema=settings.databricks_schema,
            )
            
            if db_client:
                logger.info("Databricks client initialized")
                
                # Setup catalog and schema
                if db_client.setup_catalog_and_schema():
                    logger.info("Databricks catalog and schema setup complete")
                
                # Initialize Databricks pipeline
                db_pipeline = get_databricks_pipeline(
                    db_client,
                    catalog=settings.databricks_catalog,
                    schema=settings.databricks_schema,
                )
                
                if db_pipeline:
                    logger.info("Databricks pipeline initialized")
                    
                    # Create layer tables
                    if db_pipeline.create_layer_tables():
                        logger.info("Databricks layer tables created")
                
                # Initialize Genie space manager
                genie_manager = get_genie_manager(db_client)
                if genie_manager:
                    logger.info("Genie space manager initialized")
                    
                    # Create Genie space
                    if genie_manager.create_genie_space(
                        settings.genie_space_name,
                        description="Automated analytics and insights from stock market data",
                    ):
                        logger.info(f"Genie space '{settings.genie_space_name}' created")
        except Exception as e:
            logger.error(f"Failed to initialize Databricks/Genie: {e}")
    
    yield
    
    logger.info("Application shutting down...")
    
    # Close orchestrator and pipeline
    try:
        await close_orchestrator()
        await close_pipeline()
        logger.info("Orchestrator and pipeline closed")
    except Exception as e:
        logger.error(f"Error closing services: {e}")
    
    # Close Databricks connection
    if settings.enable_databricks:
        try:
            from src.data.databricks_client import close_databricks_client
            close_databricks_client()
            logger.info("Databricks client closed")
        except Exception as e:
            logger.error(f"Error closing Databricks: {e}")


# Create FastAPI app
app = FastAPI(
    title=settings.api_title,
    description=settings.api_description,
    version=settings.api_version,
    lifespan=lifespan,
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Exception handlers
@app.exception_handler(InsightGenieException)
async def insight_genie_exception_handler(
    request: Request,
    exc: InsightGenieException,
):
    """Handle InsightGenie exceptions."""
    logger.error(f"InsightGenie error: {exc.error_code} - {exc.message}")
    
    return JSONResponse(
        status_code=400,
        content={
            "success": False,
            "error": exc.message,
            "error_code": exc.error_code,
            "details": exc.details,
        },
    )


@app.exception_handler(Exception)
async def general_exception_handler(
    request: Request,
    exc: Exception,
):
    """Handle unexpected exceptions."""
    logger.error(f"Unexpected error: {str(exc)}", exc_info=True)
    
    return JSONResponse(
        status_code=500,
        content={
            "success": False,
            "error": "Internal server error",
            "error_code": "INTERNAL_ERROR",
        },
    )


# Health check endpoint
@app.get("/health", response_model=APIResponse)
async def health_check():
    """Health check endpoint."""
    return APIResponse(
        success=True,
        message="Service is healthy",
        data={
            "status": "healthy",
            "version": settings.api_version,
        }
    )


# Root endpoint
@app.get("/", response_model=APIResponse)
async def root():
    """Root endpoint."""
    return APIResponse(
        success=True,
        message="InsightGenie AI Backend",
        data={
            "api_name": settings.api_title,
            "version": settings.api_version,
            "description": settings.api_description,
            "endpoints": {
                "analysis": "/api/analyze",
                "batch": "/api/batch-analyze",
                "status": "/api/analyze/{request_id}",
                "data_layers": "/api/data/{layer}/{symbol}",
                "health": "/health"
            }
        }
    )


# Include routers
app.include_router(analysis_router)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        app,
        host=settings.server_host,
        port=settings.server_port
    )
        data={
            "api": settings.api_title,
            "version": settings.api_version,
            "docs": "/docs",
        }
    )


if __name__ == "__main__":
    import uvicorn
    
    uvicorn.run(
        app,
        host=settings.server_host,
        port=settings.server_port,
        workers=settings.server_workers,
    )
