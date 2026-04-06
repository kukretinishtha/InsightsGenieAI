"""
InsightGenie AI - Streamlit Frontend Application

Interactive dashboard for stock analysis, portfolio management,
and real-time market insights powered by AI agents.
"""

import logging
import os

import streamlit as st
from PIL import Image

from config import get_settings, setup_logging
from pages import (
    comparison_analysis,
    geopolitical_risks,
    home,
    news_analysis,
    portfolio_analysis,
    real_time_monitor,
    stock_analysis,
)

# Setup logging
setup_logging()
logger = logging.getLogger(__name__)

# Page configuration
st.set_page_config(
    page_title="InsightGenie AI",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Load configuration
settings = get_settings()

# Custom CSS
st.markdown(
    """
    <style>
    .main {
        padding-top: 0;
    }
    .header-container {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 30px;
        border-radius: 10px;
        color: white;
        margin-bottom: 30px;
    }
    .metric-card {
        background: #f0f2f6;
        padding: 20px;
        border-radius: 10px;
        border-left: 5px solid #667eea;
    }
    .success-card {
        background: #d4edda;
        border-left-color: #28a745;
    }
    .warning-card {
        background: #fff3cd;
        border-left-color: #ffc107;
    }
    .danger-card {
        background: #f8d7da;
        border-left-color: #dc3545;
    }
    </style>
    """,
    unsafe_allow_html=True,
)


def main():
    """Main application entry point."""
    # Sidebar navigation
    with st.sidebar:
        st.title("📊 InsightGenie AI")
        st.markdown("---")

        # Navigation menu
        page = st.radio(
            "Navigate to:",
            [
                "🏠 Home",
                "📈 Stock Analysis",
                "💼 Portfolio Analysis",
                "📰 News Analysis",
                "🌍 Geopolitical Risks",
                "📊 Comparison Analysis",
                "⚡ Real-Time Monitor",
            ],
        )

        st.markdown("---")

        # Settings section
        with st.expander("⚙️ Settings"):
            st.markdown("### API Configuration")
            api_url = st.text_input(
                "API URL",
                value=settings.backend_url,
            )
            analysis_type = st.selectbox(
                "Default Analysis Type",
                ["quick", "comprehensive", "deep"],
            )

        # About section
        with st.expander("ℹ️ About"):
            st.markdown(
                f"""
                **InsightGenie AI v{settings.app_version}**
                
                Advanced AI-powered stock analysis platform combining:
                - Real-time market data (NSE/BSE)
                - News sentiment analysis
                - Geopolitical impact assessment
                - Portfolio optimization
                
                Powered by multi-agent system with 15+ specialized tools.
                """
            )

    # Route to selected page
    if page == "🏠 Home":
        home.render()
    elif page == "📈 Stock Analysis":
        stock_analysis.render()
    elif page == "💼 Portfolio Analysis":
        portfolio_analysis.render()
    elif page == "📰 News Analysis":
        news_analysis.render()
    elif page == "🌍 Geopolitical Risks":
        geopolitical_risks.render()
    elif page == "📊 Comparison Analysis":
        comparison_analysis.render()
    elif page == "⚡ Real-Time Monitor":
        real_time_monitor.render()


if __name__ == "__main__":
    main()
