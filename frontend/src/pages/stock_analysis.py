"""
Stock analysis page module.
"""

import streamlit as st
import pandas as pd
import plotly.express as px


def render():
    """Render stock analysis page."""
    st.title("📈 Stock Analysis")
    st.markdown("Analyze individual stocks with technical and sentiment insights.")

    col1, col2, col3 = st.columns(3)
    with col1:
        symbol = st.text_input("Stock Symbol", value="INFY").upper()
    with col2:
        period = st.selectbox("Period", ["1D", "1M", "3M", "1Y"])
    with col3:
        analysis_type = st.selectbox("Analysis Type", ["Technical", "Fundamental", "Sentiment"])

    if st.button("🔍 Analyze Stock"):
        st.info(f"Analyzing {symbol} ({period}) - {analysis_type} Analysis")
        
        # Sample data
        dates = pd.date_range('2026-03-01', periods=20, freq='D')
        prices = pd.DataFrame({
            'Date': dates,
            'Price': [1800 + i*5 + (i%3)*2 for i in range(20)],
            'Volume': [2500000 + i*50000 for i in range(20)]
        })
        
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Current Price", f"₹{prices['Price'].iloc[-1]:.2f}")
        with col2:
            change = prices['Price'].iloc[-1] - prices['Price'].iloc[0]
            st.metric("Change", f"₹{change:.2f}", f"{(change/prices['Price'].iloc[0]*100):.1f}%")
        with col3:
            st.metric("Avg Volume", f"{prices['Volume'].mean()/1e6:.1f}M")
        
        tab1, tab2, tab3 = st.tabs(["Chart", "Indicators", "Details"])
        
        with tab1:
            fig = px.line(prices, x='Date', y='Price', title=f"{symbol} Price Trend")
            st.plotly_chart(fig, use_container_width=True)
        
        with tab2:
            st.subheader(f"{analysis_type} Analysis")
            if analysis_type == "Technical":
                st.write("• **Support Level:** ₹1850")
                st.write("• **Resistance Level:** ₹1950")
                st.write("• **RSI:** 65 (Overbought)")
                st.write("• **MACD:** Positive signal")
            elif analysis_type == "Fundamental":
                st.write("• **P/E Ratio:** 22.5")
                st.write("• **Market Cap:** ₹8.5L Cr")
                st.write("• **ROE:** 15.2%")
                st.write("• **Dividend Yield:** 1.8%")
            else:  # Sentiment
                st.write("• **Sentiment Score:** 7.2/10 (Positive)")
                st.write("• **News Mentions:** 245 (Last 30 days)")
                st.write("• **Social Media:** 85% positive")
        
        with tab3:
            st.json({
                "symbol": symbol,
                "price": prices['Price'].iloc[-1],
                "volume": prices['Volume'].iloc[-1],
                "timestamp": prices['Date'].iloc[-1].isoformat()
            })

