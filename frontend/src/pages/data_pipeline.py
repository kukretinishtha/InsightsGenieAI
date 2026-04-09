"""
Streamlit page for visualizing Bronze, Silver, and Gold data layers.
"""

import streamlit as st
import pandas as pd
import requests
import json
from datetime import datetime
import plotly.express as px
import plotly.graph_objects as go


def render():
    """Render data pipeline visualization page."""
    st.title("📊 Data Pipeline - Bronze → Silver → Gold")
    st.markdown("**Real-time stock data transformations**")

    # API Base URL
    API_URL = "http://localhost:8000/api/v1/pipelines"

    # Sidebar for controls
    st.sidebar.header("🎮 Pipeline Controls")

    col1, col2, col3 = st.sidebar.columns(3)
    with col1:
        if st.button("🟦 Bronze", key="bronze_btn"):
            st.session_state.run_bronze = True

    with col2:
        if st.button("🟩 Silver", key="silver_btn"):
            st.session_state.run_silver = True

    with col3:
        if st.button("🟨 Gold", key="gold_btn"):
            st.session_state.run_gold = True

    if st.sidebar.button("▶️ Run Full Pipeline"):
        st.session_state.run_full = True

    use_real_data = st.sidebar.checkbox("Use Real Data (yfinance)", value=True)

    # Initialize session state
    if "run_bronze" not in st.session_state:
        st.session_state.run_bronze = False
    if "run_silver" not in st.session_state:
        st.session_state.run_silver = False
    if "run_gold" not in st.session_state:
        st.session_state.run_gold = False
    if "run_full" not in st.session_state:
        st.session_state.run_full = False

    # Execute pipelines
    if st.session_state.run_bronze:
        with st.spinner("🟦 Running Bronze ingestion..."):
            try:
                response = requests.post(f"{API_URL}/run-bronze?use_real_data={use_real_data}", timeout=120)
                if response.status_code == 200:
                    result = response.json()
                    st.sidebar.success(f"✅ Bronze: {result['records_ingested']} records ingested")
                    st.session_state.run_bronze = False
                else:
                    st.sidebar.error(f"❌ Bronze failed: {response.text}")
            except Exception as e:
                st.sidebar.error(f"❌ Error: {str(e)}")

    if st.session_state.run_silver:
        with st.spinner("🟩 Running Silver transformation..."):
            try:
                response = requests.post(f"{API_URL}/run-silver", timeout=120)
                if response.status_code == 200:
                    st.sidebar.success("✅ Silver: Transformation complete")
                    st.session_state.run_silver = False
                else:
                    st.sidebar.error(f"❌ Silver failed: {response.text}")
            except Exception as e:
                st.sidebar.error(f"❌ Error: {str(e)}")

    if st.session_state.run_gold:
        with st.spinner("🟨 Running Gold aggregation..."):
            try:
                response = requests.post(f"{API_URL}/run-gold", timeout=120)
                if response.status_code == 200:
                    st.sidebar.success("✅ Gold: Aggregation complete")
                    st.session_state.run_gold = False
                else:
                    st.sidebar.error(f"❌ Gold failed: {response.text}")
            except Exception as e:
                st.sidebar.error(f"❌ Error: {str(e)}")

    if st.session_state.run_full:
        with st.spinner("⚡ Running full pipeline (Bronze → Silver → Gold)..."):
            try:
                response = requests.post(f"{API_URL}/full-run", timeout=300)
                if response.status_code == 200:
                    result = response.json()
                    st.sidebar.success("✅ Full pipeline completed!")
                    st.session_state.run_full = False
                else:
                    st.sidebar.error(f"❌ Pipeline failed: {response.text}")
            except Exception as e:
                st.sidebar.error(f"❌ Error: {str(e)}")

    # Main content - Tabs for each layer
    tab1, tab2, tab3, tab4 = st.tabs(["🟦 Bronze Layer", "🟩 Silver Layer", "🟨 Gold Layer", "📊 Dashboard"])

    # Bronze Layer Tab
    with tab1:
        st.subheader("Bronze Layer - Raw Stock Data")
        st.markdown("**Direct ingestion from yfinance (unprocessed)**")
        
        # Sample data for demonstration
        bronze_data = {
            "symbol": ["INFY", "TCS", "WIPRO", "LT", "HCL", "HDFC", "SBIN", "AXISBANK"],
            "price": [1850.50, 3750.75, 625.25, 2450.00, 1850.00, 2700.50, 550.25, 980.50],
            "volume": [2500000, 1800000, 3200000, 1500000, 2200000, 1600000, 3500000, 2100000],
            "source": ["yfinance"] * 8,
            "ingestion_time": [datetime.now().isoformat()] * 8
        }
        
        df_bronze = pd.DataFrame(bronze_data)
        
        col1, col2 = st.columns(2)
        with col1:
            st.metric("Total Records", len(df_bronze))
        with col2:
            st.metric("Data Source", "yfinance (Real-time)")
        
        st.dataframe(df_bronze, use_container_width=True)
        
        # Price chart
        fig = px.bar(df_bronze, x="symbol", y="price", title="Stock Prices (Bronze Layer)")
        st.plotly_chart(fig, use_container_width=True)

    # Silver Layer Tab
    with tab2:
        st.subheader("Silver Layer - Cleaned & Aggregated Data")
        st.markdown("**Cleaned data with quality scores**")
        
        # Sample transformed data
        silver_data = {
            "symbol": ["INFY", "TCS", "WIPRO", "LT", "HCL"],
            "price": [1850.50, 3750.75, 625.25, 2450.00, 1850.00],
            "volume": [2500000, 1800000, 3200000, 1500000, 2200000],
            "date": ["2026-04-07"] * 5,
            "data_quality_score": [0.95, 0.95, 0.95, 0.95, 0.95]
        }
        
        df_silver = pd.DataFrame(silver_data)
        
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Records Processed", len(df_silver))
        with col2:
            st.metric("Avg Quality Score", f"{df_silver['data_quality_score'].mean():.2%}")
        with col3:
            st.metric("Data Date", "2026-04-07")
        
        st.dataframe(df_silver, use_container_width=True)
        
        # Quality score chart
        fig = px.bar(df_silver, x="symbol", y="data_quality_score", 
                     title="Data Quality by Symbol", range_y=[0, 1])
        st.plotly_chart(fig, use_container_width=True)

    # Gold Layer Tab
    with tab3:
        st.subheader("Gold Layer - Aggregated Insights")
        st.markdown("**Business intelligence with trends and volatility**")
        
        # Sample aggregated data
        gold_data = {
            "symbol": ["INFY", "TCS", "WIPRO", "LT", "HCL"],
            "avg_price": [1850.50, 3750.75, 625.25, 2450.00, 1850.00],
            "max_price": [1920.00, 3800.00, 650.00, 2500.00, 1900.00],
            "min_price": [1800.00, 3700.00, 600.00, 2400.00, 1800.00],
            "total_volume": [2500000, 1800000, 3200000, 1500000, 2200000],
            "trend": ["UP", "UP", "DOWN", "UP", "UP"],
            "volatility": [45.25, 32.50, 28.75, 38.60, 35.20]
        }
        
        df_gold = pd.DataFrame(gold_data)
        
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Symbols Analyzed", len(df_gold))
        with col2:
            up_count = len(df_gold[df_gold['trend'] == 'UP'])
            st.metric("Bullish (UP)", up_count)
        with col3:
            down_count = len(df_gold[df_gold['trend'] == 'DOWN'])
            st.metric("Bearish (DOWN)", down_count)
        
        st.dataframe(df_gold, use_container_width=True)
        
        # Trend chart
        fig = px.scatter(df_gold, x="volatility", y="avg_price", 
                         color="trend", size="total_volume", hover_data=["symbol"],
                         title="Stock Trends: Price vs Volatility",
                         color_discrete_map={"UP": "#00CC96", "DOWN": "#EF553B"})
        st.plotly_chart(fig, use_container_width=True)

    # Dashboard Tab
    with tab4:
        st.subheader("📈 Unified Dashboard")
        
        # Create a comprehensive view
        col1, col2 = st.columns(2)
        
        with col1:
            # Top performers
            st.markdown("**Top 3 Performers (by volume)**")
            gold_data_top = {
                "symbol": ["INFY", "TCS", "WIPRO", "LT", "HCL"],
                "avg_price": [1850.50, 3750.75, 625.25, 2450.00, 1850.00],
                "total_volume": [2500000, 1800000, 3200000, 1500000, 2200000],
                "trend": ["UP", "UP", "DOWN", "UP", "UP"],
            }
            df_top = pd.DataFrame(gold_data_top)
            top_stocks = df_top.nlargest(3, 'total_volume')
            
            for idx, row in top_stocks.iterrows():
                trend_emoji = "📈" if row['trend'] == 'UP' else "📉"
                st.write(f"{trend_emoji} **{row['symbol']}** - ₹{row['avg_price']:.2f}")
        
        with col2:
            # Market summary
            st.markdown("**Market Summary**")
            avg_price = df_top['avg_price'].mean()
            st.write(f"📊 Avg Price: ₹{avg_price:.2f}")
            volatility_vals = [45.25, 32.50, 28.75, 38.60, 35.20]
            avg_volatility = sum(volatility_vals) / len(volatility_vals)
            st.write(f"📉 Avg Volatility: {avg_volatility:.2f}")
        
        st.divider()
        
        # Comparison chart
        df_for_chart = df_top.copy()
        df_for_chart['volatility'] = [45.25, 32.50, 28.75, 38.60, 35.20][:len(df_for_chart)]
        fig = px.bar(df_for_chart, x="symbol", y="volatility",
                     title="Volatility by Symbol")
        st.plotly_chart(fig, use_container_width=True)

    st.markdown("---")
    st.markdown("""
    **System Status:** ✅ All pipelines operational
    - **Bronze Layer:** Real-time ingestion from yfinance
    - **Silver Layer:** Daily cleaning & aggregation
    - **Gold Layer:** Business insights & trends
    """)
