"""
Frontend utilities module.
"""

import asyncio
import logging
from typing import Any, Dict, List, Optional

import httpx
import streamlit as st

from config import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()


class APIClient:
    """API client for backend communication."""

    def __init__(self, base_url: str = None):
        """Initialize API client."""
        self.base_url = base_url or settings.backend_url

    async def analyze_stock(
        self, symbol: str, analysis_type: str = "comprehensive"
    ) -> Dict[str, Any]:
        """Analyze single stock."""
        async with httpx.AsyncClient() as client:
            try:
                response = await client.post(
                    f"{self.base_url}/api/analyze",
                    json={"symbol": symbol, "analysis_type": analysis_type},
                    timeout=settings.api_timeout,
                )
                response.raise_for_status()
                return response.json()
            except httpx.RequestError as e:
                logger.error(f"API error: {e}")
                st.error(f"Failed to analyze {symbol}: {str(e)}")
                return {}

    async def batch_analyze(
        self, symbols: List[str], analysis_type: str = "quick"
    ) -> Dict[str, Any]:
        """Analyze multiple stocks."""
        async with httpx.AsyncClient() as client:
            try:
                response = await client.post(
                    f"{self.base_url}/api/batch-analyze",
                    json={"symbols": symbols, "analysis_type": analysis_type},
                    timeout=settings.api_timeout,
                )
                response.raise_for_status()
                return response.json()
            except httpx.RequestError as e:
                logger.error(f"Batch analysis error: {e}")
                st.error(f"Batch analysis failed: {str(e)}")
                return {}

    async def get_analysis_status(
        self, request_id: str
    ) -> Dict[str, Any]:
        """Get analysis status and results."""
        async with httpx.AsyncClient() as client:
            try:
                response = await client.get(
                    f"{self.base_url}/api/analyze/{request_id}",
                    timeout=settings.api_timeout,
                )
                response.raise_for_status()
                return response.json()
            except httpx.RequestError as e:
                logger.error(f"Status check error: {e}")
                return {}

    async def get_data_layer(
        self, symbol: str, layer: str = "gold"
    ) -> Dict[str, Any]:
        """Get data from specific layer."""
        async with httpx.AsyncClient() as client:
            try:
                response = await client.get(
                    f"{self.base_url}/api/data/{layer}/{symbol}",
                    timeout=settings.api_timeout,
                )
                response.raise_for_status()
                return response.json()
            except httpx.RequestError as e:
                logger.error(f"Data layer error: {e}")
                st.error(f"Failed to get {layer} data for {symbol}")
                return {}

    async def health_check(self) -> bool:
        """Check API health."""
        async with httpx.AsyncClient() as client:
            try:
                response = await client.get(
                    f"{self.base_url}/health",
                    timeout=5,
                )
                return response.status_code == 200
            except Exception:
                return False


@st.cache_resource
def get_api_client() -> APIClient:
    """Get cached API client instance."""
    return APIClient()


def run_async(coro):
    """Run async function in Streamlit."""
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        return loop.run_until_complete(coro)
    finally:
        loop.close()


def format_currency(value: float, currency: str = "₹") -> str:
    """Format number as currency."""
    if value is None:
        return "N/A"
    return f"{currency}{value:,.2f}"


def format_percent(value: float, decimals: int = 2) -> str:
    """Format number as percentage."""
    if value is None:
        return "N/A"
    return f"{value:,.{decimals}f}%"


def format_recommendation(recommendation: str) -> tuple:
    """Format recommendation with color."""
    colors = {
        "STRONG BUY": ("🟢", "#00CC00"),
        "BUY": ("🟢", "#00FF00"),
        "HOLD": ("🟡", "#FFD700"),
        "SELL": ("🔴", "#FF4500"),
        "STRONG SELL": ("🔴", "#DC143C"),
    }
    emoji, color = colors.get(recommendation, ("⚫", "#808080"))
    return emoji, color


def display_metric_card(
    title: str, value: str, status: str = "neutral"
) -> None:
    """Display a metric card."""
    status_class = f"{status}-card"
    st.markdown(
        f"""
        <div class="metric-card {status_class}">
            <h4>{title}</h4>
            <h2>{value}</h2>
        </div>
        """,
        unsafe_allow_html=True,
    )


def display_alert(
    message: str, alert_type: str = "info", dismissible: bool = True
) -> None:
    """Display an alert."""
    if alert_type == "success":
        st.success(message)
    elif alert_type == "warning":
        st.warning(message)
    elif alert_type == "error":
        st.error(message)
    else:
        st.info(message)


def display_dataframe_with_formatting(
    df, column_formats: Dict[str, str] = None
) -> None:
    """Display DataFrame with custom formatting."""
    if column_formats:
        st.dataframe(df, use_container_width=True)
    else:
        st.dataframe(df, use_container_width=True)


class SessionState:
    """Manages Streamlit session state."""

    @staticmethod
    def set(key: str, value: Any) -> None:
        """Set session state value."""
        st.session_state[key] = value

    @staticmethod
    def get(key: str, default: Any = None) -> Any:
        """Get session state value."""
        return st.session_state.get(key, default)

    @staticmethod
    def delete(key: str) -> None:
        """Delete session state value."""
        if key in st.session_state:
            del st.session_state[key]

    @staticmethod
    def clear() -> None:
        """Clear all session state."""
        for key in list(st.session_state.keys()):
            del st.session_state[key]
