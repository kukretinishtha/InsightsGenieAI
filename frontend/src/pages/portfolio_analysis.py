"""Portfolio analysis page module."""

import streamlit as st
import pandas as pd
import plotly.express as px


def render():
    """Render portfolio analysis page."""
    st.title("💼 Portfolio Analysis")
    st.markdown("Analyze your investment portfolio with AI optimization.")
    
    col1, col2 = st.columns(2)
    with col1:
        portfolio_size = st.number_input("Portfolio Size (₹)", value=1000000, step=10000)
    with col2:
        risk_type = st.selectbox("Risk Type", ["Conservative", "Balanced", "Aggressive"])
    
    portfolio = pd.DataFrame({
        'Stock': ['INFY', 'TCS', 'WIPRO', 'LT', 'HCL'],
        'Weight': [25, 20, 20, 20, 15],
        'Value': [250000, 200000, 200000, 200000, 150000]
    })
    
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Portfolio Value", f"₹{portfolio_size/1e5:.1f}L")
    with col2:
        st.metric("Expected Return", "9.5%")
    with col3:
        st.metric("Risk Level", risk_type)
    with col4:
        st.metric("Diversification", "Good")
    
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("Allocation")
        fig = px.pie(portfolio, values='Weight', names='Stock')
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.subheader("Holdings")
        st.dataframe(portfolio, use_container_width=True)
    
    st.subheader("Recommendations")
    st.info("✅ Portfolio is well diversified")
    st.warning("⚠️ Consider rebalancing quarterly")

