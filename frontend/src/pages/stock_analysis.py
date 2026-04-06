"""
Stock analysis page module.
"""

import streamlit as st

from utils import APIClient, SessionState, get_api_client, run_async


def render():
    """Render stock analysis page."""
    st.title("📈 Stock Analysis")

    st.markdown(
        "Comprehensive AI-powered analysis of individual stocks with technical, "
        "fundamental, and sentiment insights."
    )

    # User inputs
    col1, col2, col3 = st.columns(3)

    with col1:
        symbol = st.text_input(
            "Stock Symbol",
            value="RELIANCE",
            help="Enter NSE stock symbol (e.g., RELIANCE, TCS, INFY)",
        ).upper()

    with col2:
        analysis_type = st.selectbox(
            "Analysis Type",
            ["quick", "comprehensive", "deep"],
            help="Choose analysis depth",
        )

    with col3:
        if st.button("🔍 Analyze", use_container_width=True):
            SessionState.set("analyzing", True)
            SessionState.set("current_symbol", symbol)

    st.markdown("---")

    if SessionState.get("analyzing") and SessionState.get("current_symbol") == symbol:
        with st.spinner(f"Analyzing {symbol}..."):
            client = get_api_client()
            result = run_async(client.analyze_stock(symbol, analysis_type))

            if result and result.get("success"):
                data = result.get("data", {})

                # Display tabs
                tab1, tab2, tab3, tab4, tab5 = st.tabs(
                    ["Overview", "Technical", "News", "Geopolitical", "Details"]
                )

                with tab1:
                    col1, col2, col3, col4 = st.columns(4)
                    with col1:
                        st.metric(
                            "Current Price",
                            f"₹{data.get('price', 0):.2f}",
                        )
                    with col2:
                        st.metric(
                            "Day Change",
                            f"{data.get('change', 0):.2f}%",
                        )
                    with col3:
                        st.metric(
                            "Market Cap",
                            f"₹{data.get('market_cap', 0):,.0f}Cr",
                        )
                    with col4:
                        recommendation = data.get("recommendation", "HOLD")
                        st.metric("Recommendation", recommendation)

                    st.markdown("### Analysis Summary")
                    st.info(data.get("summary", "No summary available"))

                with tab2:
                    st.markdown("### Technical Indicators")
                    tech_data = data.get("technical", {})
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        st.metric("SMA 50", f"{tech_data.get('sma_50', 0):.2f}")
                    with col2:
                        st.metric("RSI", f"{tech_data.get('rsi', 0):.2f}")
                    with col3:
                        st.metric("MACD", f"{tech_data.get('macd', 0):.4f}")

                with tab3:
                    st.markdown("### News Sentiment")
                    news_data = data.get("news", {})
                    sentiment = news_data.get("sentiment_score", 0)
                    st.metric("Sentiment Score", f"{sentiment:.2f}")

                    col1, col2 = st.columns(2)
                    with col1:
                        st.markdown("**Recent News**")
                        for article in news_data.get("articles", [])[:5]:
                            st.caption(article)

                with tab4:
                    st.markdown("### Geopolitical Impact")
                    geo_data = data.get("geopolitical", {})
                    risk_level = geo_data.get("risk_level", "MEDIUM")
                    risk_score = geo_data.get("risk_score", 0)

                    col1, col2 = st.columns(2)
                    with col1:
                        st.metric("Risk Level", risk_level)
                    with col2:
                        st.metric("Risk Score", f"{risk_score:.2f}")

                with tab5:
                    st.markdown("### Detailed Data")
                    st.json(data)

            else:
                st.error("Failed to analyze stock. Please try again.")

        SessionState.set("analyzing", False)

    # Data layer inspection
    st.markdown("---")
    st.subheader("📊 Data Layer Inspection")

    layer = st.radio(
        "Select Layer",
        ["Bronze", "Silver", "Gold"],
        horizontal=True,
    )

    if st.button("View Layer Data"):
        with st.spinner(f"Loading {layer} layer data..."):
            client = get_api_client()
            layer_name = layer.lower()
            result = run_async(client.get_data_layer(symbol, layer_name))

            if result and result.get("success"):
                st.json(result.get("data", {}))
            else:
                st.error("Failed to load layer data")
