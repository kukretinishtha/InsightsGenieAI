"""Error handling middleware."""

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException
from app.utils.exceptions import InsightGenieException
from app.utils.logger import get_logger
from app.models.api import ErrorResponse
import uuid

logger = get_logger(__name__)


def setup_error_handlers(app: FastAPI) -> None:
    """
    Setup global error handlers.
    
    Args:
        app: FastAPI application
    """
    
    @app.exception_handler(InsightGenieException)
    async def insight_genie_exception_handler(request: Request, exc: InsightGenieException):
        """Handle InsightGenie exceptions."""
        request_id = str(uuid.uuid4())
        
        logger.warning(
            f"InsightGenieException raised: {exc.code} - {exc.message}",
            extra={"request_id": request_id}
        )
        
        error_response = ErrorResponse(
            error=exc.code,
            message=exc.message,
            details=exc.details,
            request_id=request_id
        )
        
        return JSONResponse(
            status_code=exc.status_code,
            content=error_response.model_dump()
        )
    
    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(request: Request, exc: RequestValidationError):
        """Handle request validation errors."""
        request_id = str(uuid.uuid4())
        
        logger.warning(
            f"Validation error on {request.url.path}",
            extra={"request_id": request_id, "errors": exc.errors()}
        )
        
        error_response = ErrorResponse(
            error="VALIDATION_ERROR",
            message="Request validation failed",
            details={"errors": exc.errors()},
            request_id=request_id
        )
        
        return JSONResponse(
            status_code=400,
            content=error_response.model_dump()
        )
    
    @app.exception_handler(HTTPException)
    async def http_exception_handler(request: Request, exc: HTTPException):
        """Handle HTTP exceptions."""
        request_id = str(uuid.uuid4())
        
        error_response = ErrorResponse(
            error="HTTP_ERROR",
            message=exc.detail,
            request_id=request_id
        )
        
        return JSONResponse(
            status_code=exc.status_code,
            content=error_response.model_dump()
        )
    
    @app.exception_handler(Exception)
    async def general_exception_handler(request: Request, exc: Exception):
        """Handle general exceptions."""
        request_id = str(uuid.uuid4())
        
        logger.error(
            f"Unhandled exception on {request.url.path}: {str(exc)}",
            exc_info=True,
            extra={"request_id": request_id}
        )
        
        error_response = ErrorResponse(
            error="INTERNAL_ERROR",
            message="An unexpected error occurred",
            request_id=request_id
        )
        
        return JSONResponse(
            status_code=500,
            content=error_response.model_dump()
        )
