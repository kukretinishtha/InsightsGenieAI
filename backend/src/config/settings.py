"""
Configuration management for InsightGenie AI application.
Uses Pydantic Settings for environment variable management.
"""

from typing import Optional
from pydantic_settings import BaseSettings
from functools import lru_cache
import logging

logger = logging.getLogger(__name__)


class Settings(BaseSettings):
    """Application configuration loaded from environment variables."""

    # Environment
    env: str = "development"
    debug: bool = True
    log_level: str = "INFO"

    # API Configuration
    api_title: str = "InsightGenie AI"
    api_version: str = "1.0.0"
    api_description: str = "Real-time Indian Stock Market Prediction"
    allowed_origins: list[str] = ["http://localhost:3000", "http://localhost:8501"]

    # Server Configuration
    server_host: str = "0.0.0.0"
    server_port: int = 8000
    server_workers: int = 4

    # Database Configuration
    database_url: str = "postgresql+asyncpg://user:password@localhost:5432/insight_genie"
    mongodb_url: str = "mongodb://localhost:27017/insight_genie"
    mongodb_db_name: str = "insight_genie"

    # Redis Configuration
    redis_url: str = "redis://localhost:6379"
    redis_db: int = 0
    cache_ttl: int = 3600

    # Genie API Configuration
    genie_api_url: str = "https://genie-api.databricks.com/v1"
    genie_api_key: str
    genie_model: str = "claude-3-5-sonnet"
    genie_max_retries: int = 3
    genie_timeout: int = 300
    genie_polling_interval: int = 100
    genie_polling_max_delay: int = 5000

    # Stock Market Data Sources
    nse_api_url: str = "https://www.nseindia.com/api"
    bse_api_url: str = "https://api.bseindia.com/api"
    alpha_vantage_api_key: Optional[str] = None
    finnhub_api_key: Optional[str] = None

    # News and Sentiment Analysis
    news_api_url: str = "https://newsapi.org/v2"
    news_api_key: Optional[str] = None
    financial_news_sources: list[str] = ["bloomberg", "cnbc", "reuters", "economictimes"]

    # Geopolitical Data
    geo_api_url: str = "https://geopolitical-api.example.com"
    geo_api_key: Optional[str] = None

    # Celery Configuration
    celery_broker_url: str = "redis://localhost:6379/1"
    celery_result_backend: str = "redis://localhost:6379/2"

    # Authentication
    secret_key: str = "your-secret-key-change-in-production"
    jwt_algorithm: str = "HS256"
    jwt_expiration_hours: int = 24

    # Logging
    log_file: str = "logs/app.log"
    log_format: str = "json"

    # Rate Limiting
    rate_limit_requests: int = 100
    rate_limit_period: int = 60

    # Performance Configuration
    max_concurrent_agents: int = 3
    max_concurrent_tools: int = 10
    request_timeout: int = 300
    execution_timeout: int = 300

    # Databricks Configuration
    databricks_host: Optional[str] = None
    databricks_token: Optional[str] = None
    databricks_catalog: str = "insightgenie"
    databricks_schema: str = "default"
    databricks_warehouse_id: Optional[str] = None
    databricks_http_path: Optional[str] = None
    enable_databricks: bool = False

    # Genie Space Configuration
    genie_space_name: str = "insightgenie-analytics"
    genie_auto_insights: bool = True
    genie_enable_dashboards: bool = True
    genie_dashboard_refresh_interval: int = 300

    # Feature Flags
    enable_geopolitical_analysis: bool = True
    enable_news_analysis: bool = True
    enable_technical_analysis: bool = True
    enable_fundamental_analysis: bool = True
    enable_caching: bool = True
    enable_async_processing: bool = True

    class Config:
        """Pydantic configuration."""
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False


@lru_cache()
def get_settings() -> Settings:
    """
    Get cached settings instance.
    
    Returns:
        Settings: Application settings from environment
    """
    return Settings()


# Export singleton
settings = get_settings()
