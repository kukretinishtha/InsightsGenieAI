"""CORS middleware setup."""

from fastapi.middleware.cors import CORSMiddleware
from fastapi import FastAPI
from app.config import get_settings


def setup_cors(app: FastAPI) -> None:
    """
    Setup CORS middleware.
    
    Args:
        app: FastAPI application
    """
    settings = get_settings()
    
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.CORS_ORIGINS,
        allow_credentials=settings.CORS_ALLOW_CREDENTIALS,
        allow_methods=settings.CORS_ALLOW_METHODS,
        allow_headers=settings.CORS_ALLOW_HEADERS,
    )
