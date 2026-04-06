"""
Home page module.
"""

import streamlit as st


def render():
    """Render home page."""
    # Header
    st.markdown(
        """
        <div class="header-container">
            <h1>📊 InsightGenie AI</h1>
            <p>Advanced AI-Powered Stock Analysis & Portfolio Management</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # Key features
    col1, col2, col3 = st.columns(3)

    with col1:
        st.info(
            """
            **🔍 Smart Analysis**
            
            Multi-agent system analyzing:
            - Technical indicators
            - News sentiment
            - Market trends
            """
        )

    with col2:
        st.info(
            """
            **💼 Portfolio Management**
            
            - Real-time monitoring
            - Risk assessment
            - Optimization suggestions
            """
        )

    with col3:
        st.info(
            """
            **🌍 Global Insights**
            
            - Geopolitical impacts
            - Trade policy effects
            - Country risk scores
            """
        )

    st.markdown("---")

    # Quick stats
    st.subheader("📈 Market Overview")

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric("NSE Live", "21,456.32", "+1.2%")

    with col2:
        st.metric("BSE Live", "44,892.15", "+1.5%")

    with col3:
        st.metric("Nifty 50", "18,456.25", "+0.8%")

    with col4:
        st.metric("Sensex", "62,456.32", "+1.0%")

    st.markdown("---")

    # Features section
    st.subheader("🎯 Features")

    features = {
        "📈 Stock Analysis": "Detailed analysis of individual stocks with technical, fundamental, and news-based insights",
        "💼 Portfolio Analysis": "Monitor and optimize your investment portfolio with real-time recommendations",
        "📰 News Analysis": "Sentiment analysis of latest market news and its impact on stock prices",
        "🌍 Geopolitical Risks": "Track geopolitical events and their potential market impacts",
        "📊 Comparison Analysis": "Compare multiple stocks side-by-side for better decision making",
        "⚡ Real-Time Monitor": "Monitor market movements and get instant alerts for significant changes",
    }

    cols = st.columns(2)
    for idx, (feature, description) in enumerate(features.items()):
        with cols[idx % 2]:
            st.markdown(f"**{feature}**")
            st.caption(description)

    st.markdown("---")

    # How it works
    st.subheader("⚙️ How It Works")

    st.markdown(
        """
        InsightGenie AI uses a sophisticated multi-agent system to analyze stocks:
        
        1. **Data Collection**: Real-time data from NSE, BSE, and news sources
        2. **Processing**: Three-layer pipeline (Bronze → Silver → Gold)
        3. **Analysis**: 15+ specialized tools across 3 agents
        4. **Insights**: AI-generated recommendations backed by data
        
        **Three-Layer Architecture:**
        - **Bronze Layer**: Raw market data and articles
        - **Silver Layer**: Cleaned, normalized, and enriched data
        - **Gold Layer**: Final analysis with signals and targets
        """
    )

    st.markdown("---")

    # Getting started
    st.subheader("🚀 Getting Started")

    col1, col2 = st.columns(2)

    with col1:
        st.markdown(
            """
            ### Quick Start
            
            1. **Select Analysis Type** → Choose quick, comprehensive, or deep analysis
            2. **Enter Stock Symbol** → Use NSE symbols (e.g., RELIANCE, TCS, INFY)
            3. **View Results** → Get detailed insights with recommendations
            4. **Track Progress** → Monitor your requests in real-time
            """
        )

    with col2:
        st.markdown(
            """
            ### Popular Stocks
            
            - **RELIANCE** (Reliance Industries)
            - **TCS** (Tata Consultancy Services)
            - **INFY** (Infosys Limited)
            - **WIPRO** (Wipro Limited)
            - **HDFC** (Housing Development Finance)
            """
        )

    st.markdown("---")

    # Footer
    st.markdown(
        """
        <div style='text-align: center; color: #888; margin-top: 30px;'>
            <p>InsightGenie AI v1.0.0 | Powered by FastAPI, Streamlit & Advanced AI</p>
        </div>
        """,
        unsafe_allow_html=True,
    )
