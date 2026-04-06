"""
Frontend configuration module.
"""

import logging
import os
from functools import lru_cache
from pathlib import Path

from pydantic import BaseModel


class Settings(BaseModel):
    """Application settings."""

    # App configuration
    app_name: str = "InsightGenie AI"
    app_version: str = "1.0.0"
    app_description: str = "Advanced AI-powered stock analysis platform"

    # API Configuration
    backend_url: str = os.getenv("BACKEND_URL", "http://localhost:8001")
    api_timeout: int = 30

    # Frontend Configuration
    frontend_port: int = int(os.getenv("FRONTEND_PORT", "8501"))
    debug: bool = os.getenv("DEBUG", "false").lower() == "true"

    # Cache Configuration
    cache_ttl: int = 300  # 5 minutes

    # UI Configuration
    page_width: str = "wide"
    theme: str = "light"

    # Feature Flags
    enable_portfolio_analysis: bool = True
    enable_comparison_analysis: bool = True
    enable_real_time_monitor: bool = True
    enable_backtesting: bool = False

    # Stock Configuration
    default_stock_symbols: list = [
        "RELIANCE",
        "TCS",
        "INFY",
        "WIPRO",
        "HDFC",
    ]
    nse_symbols_file: str = "data/nse_symbols.json"

    # Analysis Configuration
    default_analysis_type: str = "comprehensive"
    quick_update_interval: int = 60  # seconds
    full_update_interval: int = 300  # seconds

    # Logging Configuration
    log_level: str = os.getenv("LOG_LEVEL", "INFO")
    log_format: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    log_file: str = "logs/frontend.log"

    class Config:
        """Pydantic config."""

        env_file = ".env"
        case_sensitive = False


@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance."""
    return Settings()


def setup_logging() -> None:
    """Setup logging configuration."""
    settings = get_settings()

    # Create logs directory if not exists
    Path(settings.log_file).parent.mkdir(exist_ok=True)

    logging.basicConfig(
        level=settings.log_level,
        format=settings.log_format,
        handlers=[
            logging.FileHandler(settings.log_file),
            logging.StreamHandler(),
        ],
    )
