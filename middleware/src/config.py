"""
Configuration module for middleware.
"""

import os
from functools import lru_cache
from typing import Optional

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings."""

    # API Configuration
    api_title: str = "InsightGenie Middleware"
    api_version: str = "1.0.0"
    api_description: str = "Middleware layer for InsightGenie AI"
    debug: bool = os.getenv("DEBUG", "false").lower() == "true"

    # Backend Configuration
    backend_url: str = os.getenv(
        "BACKEND_URL", "http://localhost:8000"
    )
    backend_timeout: int = int(os.getenv("BACKEND_TIMEOUT", "30"))

    # Frontend Configuration
    frontend_url: str = os.getenv("FRONTEND_URL", "http://localhost:8501")

    # Middleware Configuration
    middleware_host: str = os.getenv("MIDDLEWARE_HOST", "0.0.0.0")
    middleware_port: int = int(os.getenv("MIDDLEWARE_PORT", "8001"))
    middleware_workers: int = int(os.getenv("MIDDLEWARE_WORKERS", "4"))

    # Cache Configuration
    cache_enabled: bool = True
    cache_ttl: int = 300  # 5 minutes
    redis_url: str = os.getenv(
        "REDIS_URL", "redis://localhost:6379/0"
    )

    # Database Configuration
    postgres_url: str = os.getenv(
        "DATABASE_URL",
        "postgresql://insightgenie:changeme@localhost:5432/insightgenie",
    )
    mongodb_url: str = os.getenv(
        "MONGODB_URL",
        "mongodb://insightgenie:changeme@localhost:27017/insightgenie",
    )

    # JWT Configuration
    jwt_secret_key: str = os.getenv(
        "JWT_SECRET_KEY", "your-secret-key-change-in-production"
    )
    jwt_algorithm: str = "HS256"
    jwt_expiration: int = 3600  # 1 hour

    # Rate Limiting
    rate_limit_enabled: bool = True
    rate_limit_requests: int = 100  # requests per window
    rate_limit_window: int = 60  # seconds

    # CORS Configuration
    cors_origins: list = [
        "http://localhost:3000",
        "http://localhost:8501",
        "http://localhost:8000",
    ]
    cors_allow_credentials: bool = True
    cors_allow_methods: list = ["GET", "POST", "PUT", "DELETE", "OPTIONS"]
    cors_allow_headers: list = ["*"]

    # Logging Configuration
    log_level: str = os.getenv("LOG_LEVEL", "INFO")
    log_format: str = "json"
    log_file: Optional[str] = os.getenv("LOG_FILE", None)

    # API Keys
    api_keys: dict = {
        "default": os.getenv("DEFAULT_API_KEY", "sk-default-key"),
    }

    class Config:
        """Pydantic settings configuration."""

        env_file = ".env"
        case_sensitive = False


@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance."""
    return Settings()
