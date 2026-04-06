"""
InsightGenie Middleware Package

Provides middleware layer for API gateway, authentication, rate limiting,
request validation, and caching.
"""

from .middleware import create_middleware_app, get_client
from .auth import JWTManager, create_token, verify_token
from .cache import CacheManager
from .validators import RequestValidator

__all__ = [
    "create_middleware_app",
    "get_client",
    "JWTManager",
    "create_token",
    "verify_token",
    "CacheManager",
    "RequestValidator",
]

__version__ = "1.0.0"
