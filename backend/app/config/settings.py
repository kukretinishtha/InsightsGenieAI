"""Application settings and configuration management."""

import os
from typing import Optional
from functools import lru_cache
from pydantic_settings import BaseSettings
from pydantic import Field, validator


class Settings(BaseSettings):
    """Application configuration settings."""
    
    # Application
    APP_NAME: str = "InsightGenie AI"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = Field(default=False, env="DEBUG")
    ENVIRONMENT: str = Field(default="development", env="ENVIRONMENT")
    
    # Server
    HOST: str = Field(default="0.0.0.0", env="HOST")
    PORT: int = Field(default=8000, env="PORT")
    WORKERS: int = Field(default=4, env="WORKERS")
    
    # Database
    DATABASE_URL: str = Field(default="postgresql+asyncpg://user:password@localhost/insightgenie", env="DATABASE_URL")
    MONGODB_URL: str = Field(default="mongodb+srv://user:password@cluster/insightgenie", env="MONGODB_URL")
    DATABASE_ECHO: bool = Field(default=False, env="DATABASE_ECHO")
    
    # Redis
    REDIS_URL: str = Field(default="redis://localhost:6379/0", env="REDIS_URL")
    REDIS_TIMEOUT: int = Field(default=5, env="REDIS_TIMEOUT")
    
    # API Keys and Credentials
    GENIE_API_KEY: str = Field(default="", env="GENIE_API_KEY")
    GENIE_API_BASE_URL: str = Field(default="https://api.genie.com", env="GENIE_API_BASE_URL")
    GENIE_API_TIMEOUT: int = Field(default=30, env="GENIE_API_TIMEOUT")
    
    # Celery / Task Queue
    CELERY_BROKER_URL: str = Field(default="redis://localhost:6379/1", env="CELERY_BROKER_URL")
    CELERY_RESULT_BACKEND: str = Field(default="redis://localhost:6379/2", env="CELERY_RESULT_BACKEND")
    
    # Logging
    LOG_LEVEL: str = Field(default="INFO", env="LOG_LEVEL")
    LOG_FORMAT: str = Field(default="json", env="LOG_FORMAT")
    LOG_FILE: str = Field(default="logs/app.log", env="LOG_FILE")
    
    # Security
    SECRET_KEY: str = Field(default="change-me-in-production", env="SECRET_KEY")
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # CORS
    CORS_ORIGINS: list = Field(default=["http://localhost:3000", "http://localhost:8501"], env="CORS_ORIGINS")
    CORS_ALLOW_CREDENTIALS: bool = True
    CORS_ALLOW_METHODS: list = ["*"]
    CORS_ALLOW_HEADERS: list = ["*"]
    
    # Cache
    CACHE_TTL: int = Field(default=3600, env="CACHE_TTL")
    CACHE_MAX_SIZE: int = Field(default=1000, env="CACHE_MAX_SIZE")
    
    # Async Configuration
    MAX_CONCURRENT_TASKS: int = Field(default=10, env="MAX_CONCURRENT_TASKS")
    TASK_TIMEOUT: int = Field(default=300, env="TASK_TIMEOUT")
    
    # Monitoring
    SENTRY_DSN: Optional[str] = Field(default=None, env="SENTRY_DSN")
    ENABLE_METRICS: bool = Field(default=True, env="ENABLE_METRICS")
    
    # Databricks Configuration
    DATABRICKS_HOST: str = Field(default="", env="DATABRICKS_HOST")
    DATABRICKS_TOKEN: str = Field(default="", env="DATABRICKS_TOKEN")
    DATABRICKS_CATALOG: str = Field(default="default", env="DATABRICKS_CATALOG")
    DATABRICKS_SCHEMA: str = Field(default="default", env="DATABRICKS_SCHEMA")
    DATABRICKS_WAREHOUSE_ID: Optional[str] = Field(default=None, env="DATABRICKS_WAREHOUSE_ID")
    ENABLE_DATABRICKS: bool = Field(default=False, env="ENABLE_DATABRICKS")
    
    @validator("CORS_ORIGINS", pre=True)
    def parse_cors_origins(cls, v):
        if isinstance(v, str):
            return [origin.strip() for origin in v.split(",")]
        return v
    
    class Config:
        """Pydantic configuration."""
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = True
    
    @property
    def is_production(self) -> bool:
        """Check if running in production."""
        return self.ENVIRONMENT == "production"
    
    @property
    def is_development(self) -> bool:
        """Check if running in development."""
        return self.ENVIRONMENT == "development"


@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance."""
    return Settings()
