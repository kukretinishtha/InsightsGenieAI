"""Authentication middleware."""

from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse
from app.utils.logger import get_logger
import uuid

logger = get_logger(__name__)


class AuthMiddleware(BaseHTTPMiddleware):
    """Middleware for authentication."""
    
    EXCLUDED_PATHS = {"/health", "/docs", "/openapi.json", "/redoc", "/api/v1/auth/login"}
    
    async def dispatch(self, request: Request, call_next):
        """Check authentication for protected routes."""
        request_id = str(uuid.uuid4())
        request.state.request_id = request_id
        
        # Skip auth check for excluded paths
        if request.url.path in self.EXCLUDED_PATHS:
            return await call_next(request)
        
        # Check for authorization header
        auth_header = request.headers.get("Authorization")
        
        if not auth_header:
            logger.warning(
                f"Missing authorization header: {request.method} {request.url.path}",
                extra={"request_id": request_id}
            )
            return JSONResponse(
                status_code=401,
                content={
                    "error": "AUTHENTICATION_ERROR",
                    "message": "Missing authorization header",
                    "request_id": request_id
                }
            )
        
        # Store auth header in request state for later use
        request.state.auth_header = auth_header
        
        return await call_next(request)
