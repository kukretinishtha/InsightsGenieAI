"""
Main middleware application module.
"""

import logging
import time
import uuid
from datetime import datetime
from typing import Callable, Optional

import aiohttp
import httpx
from fastapi import FastAPI, HTTPException, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from .auth import get_current_user, get_optional_user
from .cache import get_cache_manager
from .config import get_settings
from .models import APIResponse, ErrorResponse, HealthCheck
from .validators import RequestValidator

logger = logging.getLogger(__name__)
settings = get_settings()

# Global HTTP client
_http_client: Optional[httpx.AsyncClient] = None


async def get_client() -> httpx.AsyncClient:
    """Get HTTP client for backend communication."""
    global _http_client
    if _http_client is None:
        _http_client = httpx.AsyncClient(
            base_url=settings.backend_url,
            timeout=settings.backend_timeout,
        )
    return _http_client


def create_middleware_app() -> FastAPI:
    """Create and configure FastAPI middleware application."""

    app = FastAPI(
        title=settings.api_title,
        version=settings.api_version,
        description=settings.api_description,
        debug=settings.debug,
    )

    # Add CORS middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins,
        allow_credentials=settings.cors_allow_credentials,
        allow_methods=settings.cors_allow_methods,
        allow_headers=settings.cors_allow_headers,
    )

    cache_manager = get_cache_manager()

    # ==================== LIFECYCLE EVENTS ====================

    @app.on_event("startup")
    async def startup_event():
        """Initialize on startup."""
        logger.info("Middleware starting up...")
        cache_manager.connect()

    @app.on_event("shutdown")
    async def shutdown_event():
        """Cleanup on shutdown."""
        logger.info("Middleware shutting down...")
        client = await get_client()
        await client.aclose()
        cache_manager.disconnect()

    # ==================== MIDDLEWARE HANDLERS ====================

    @app.middleware("http")
    async def add_request_id_middleware(
        request: Request, call_next: Callable
    ):
        """Add request ID to all requests."""
        request_id = str(uuid.uuid4())
        request.state.request_id = request_id
        request.state.start_time = time.time()

        response = await call_next(request)
        response.headers["X-Request-ID"] = request_id

        process_time = time.time() - request.state.start_time
        response.headers["X-Process-Time"] = str(process_time)

        logger.info(
            f"[{request_id}] {request.method} {request.url.path} - "
            f"{response.status_code} - {process_time:.3f}s"
        )
        return response

    # ==================== HEALTH CHECK ====================

    @app.get("/health", response_model=HealthCheck)
    async def health_check():
        """Health check endpoint."""
        try:
            client = await get_client()
            backend_status = "healthy"
            try:
                response = await client.get("/health")
                if response.status_code != 200:
                    backend_status = "unhealthy"
            except Exception:
                backend_status = "unavailable"

            cache_status = "healthy" if cache_manager.enabled else "disabled"

            return HealthCheck(
                status="healthy",
                version=settings.api_version,
                timestamp=datetime.utcnow().isoformat(),
                services={
                    "backend": backend_status,
                    "cache": cache_status,
                },
            )
        except Exception as e:
            logger.error(f"Health check failed: {e}")
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Service unavailable",
            )

    # ==================== ANALYSIS ENDPOINTS ====================

    @app.post("/api/analyze")
    async def analyze_stock(request: Request, body: dict):
        """Submit stock analysis request."""
        request_id = request.state.request_id

        try:
            # Validate request
            validated = RequestValidator.validate_analysis_request(body)

            # Check cache
            cache_key = f"analysis:{validated.symbol}:{validated.analysis_type}"
            cached = cache_manager.get(cache_key)
            if cached:
                logger.info(f"[{request_id}] Cache hit for {cache_key}")
                return APIResponse(
                    success=True,
                    message="Analysis retrieved from cache",
                    data=cached,
                    request_id=request_id,
                )

            # Forward to backend
            client = await get_client()
            response = await client.post(
                "/api/analyze",
                json=validated.dict(),
                headers={"X-Request-ID": request_id},
            )

            if response.status_code != 200:
                return APIResponse(
                    success=False,
                    message="Backend analysis failed",
                    error=response.text,
                    request_id=request_id,
                )

            result = response.json()

            # Cache result
            cache_manager.set(cache_key, result, ttl=600)

            return APIResponse(
                success=True,
                message="Analysis completed successfully",
                data=result,
                request_id=request_id,
            )

        except Exception as e:
            logger.error(f"[{request_id}] Analysis error: {e}")
            return APIResponse(
                success=False,
                message="Analysis failed",
                error=str(e),
                request_id=request_id,
            )

    @app.get("/api/analyze/{request_id}")
    async def get_analysis_status(request_id: str, request: Request):
        """Get analysis status and results."""
        try:
            client = await get_client()
            response = await client.get(
                f"/api/analyze/{request_id}",
                headers={"X-Request-ID": request.state.request_id},
            )

            if response.status_code != 200:
                return APIResponse(
                    success=False,
                    message="Request not found",
                    error="Analysis request not found",
                    request_id=request.state.request_id,
                )

            return APIResponse(
                success=True,
                message="Status retrieved",
                data=response.json(),
                request_id=request.state.request_id,
            )

        except Exception as e:
            logger.error(f"Status check error: {e}")
            return APIResponse(
                success=False,
                message="Status check failed",
                error=str(e),
                request_id=request.state.request_id,
            )

    @app.post("/api/batch-analyze")
    async def batch_analyze(request: Request, body: dict):
        """Submit batch analysis request."""
        request_id = request.state.request_id

        try:
            validated = RequestValidator.validate_batch_request(body)

            client = await get_client()
            response = await client.post(
                "/api/batch-analyze",
                json=validated.dict(),
                headers={"X-Request-ID": request_id},
            )

            if response.status_code != 200:
                return APIResponse(
                    success=False,
                    message="Batch analysis failed",
                    error=response.text,
                    request_id=request_id,
                )

            return APIResponse(
                success=True,
                message="Batch analysis submitted",
                data=response.json(),
                request_id=request_id,
            )

        except Exception as e:
            logger.error(f"[{request_id}] Batch analysis error: {e}")
            return APIResponse(
                success=False,
                message="Batch analysis failed",
                error=str(e),
                request_id=request_id,
            )

    @app.get("/api/data/{layer}/{symbol}")
    async def get_data_layer(layer: str, symbol: str, request: Request):
        """Get data from specific layer."""
        request_id = request.state.request_id

        try:
            validated = RequestValidator.validate_data_layer_request(
                {"layer": layer, "symbol": symbol}
            )

            cache_key = f"data:{layer}:{symbol}"
            cached = cache_manager.get(cache_key)
            if cached:
                return APIResponse(
                    success=True,
                    message=f"{layer} layer data",
                    data=cached,
                    request_id=request_id,
                )

            client = await get_client()
            response = await client.get(
                f"/api/data/{layer}/{symbol}",
                headers={"X-Request-ID": request_id},
            )

            if response.status_code != 200:
                return APIResponse(
                    success=False,
                    message="Data retrieval failed",
                    error=response.text,
                    request_id=request_id,
                )

            result = response.json()
            cache_manager.set(cache_key, result, ttl=300)

            return APIResponse(
                success=True,
                message=f"{layer} layer data",
                data=result,
                request_id=request_id,
            )

        except Exception as e:
            logger.error(f"[{request_id}] Data layer error: {e}")
            return APIResponse(
                success=False,
                message="Data retrieval failed",
                error=str(e),
                request_id=request_id,
            )

    # ==================== ERROR HANDLERS ====================

    @app.exception_handler(HTTPException)
    async def http_exception_handler(request: Request, exc: HTTPException):
        """Handle HTTP exceptions."""
        return JSONResponse(
            status_code=exc.status_code,
            content=ErrorResponse(
                message="Request failed",
                error=exc.detail,
                success=False,
            ).dict(),
        )

    @app.exception_handler(Exception)
    async def general_exception_handler(request: Request, exc: Exception):
        """Handle general exceptions."""
        request_id = getattr(request.state, "request_id", "unknown")
        logger.error(f"[{request_id}] Unhandled exception: {exc}")

        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content=ErrorResponse(
                message="Internal server error",
                error=str(exc),
                success=False,
            ).dict(),
        )

    return app


if __name__ == "__main__":
    import uvicorn

    app = create_middleware_app()
    uvicorn.run(
        app,
        host=settings.middleware_host,
        port=settings.middleware_port,
        workers=settings.middleware_workers,
    )
