"""Request logging middleware."""

from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import Response
import time
import uuid
from app.utils.logger import get_logger

logger = get_logger(__name__)


class RequestLoggingMiddleware(BaseHTTPMiddleware):
    """Middleware for logging HTTP requests."""
    
    async def dispatch(self, request: Request, call_next) -> Response:
        """Log request and response."""
        request_id = str(uuid.uuid4())
        request.state.request_id = request_id
        
        start_time = time.time()
        
        try:
            response = await call_next(request)
        except Exception as exc:
            process_time = time.time() - start_time
            logger.error(
                f"Request failed: {request.method} {request.url.path}",
                extra={
                    "request_id": request_id,
                    "method": request.method,
                    "path": request.url.path,
                    "duration_seconds": process_time,
                    "exception": str(exc)
                }
            )
            raise
        
        process_time = time.time() - start_time
        
        log_level = "info" if 200 <= response.status_code < 400 else "warning"
        log_func = getattr(logger, log_level)
        
        log_func(
            f"Request completed: {request.method} {request.url.path} - {response.status_code}",
            extra={
                "request_id": request_id,
                "method": request.method,
                "path": request.url.path,
                "status_code": response.status_code,
                "duration_seconds": f"{process_time:.3f}",
                "query_params": dict(request.query_params)
            }
        )
        
        response.headers["X-Request-ID"] = request_id
        return response
