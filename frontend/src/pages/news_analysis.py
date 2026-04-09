"""
News analysis page module.
"""

import streamlit as st
import pandas as pd
import plotly.express as px


def render():
    """Render news analysis page."""
    st.title("📰 News Analysis")
    st.markdown("Analyze market news sentiment and impact on stocks.")

    col1, col2, col3 = st.columns(3)

    with col1:
        symbol = st.text_input("Stock Symbol", value="INFY").upper()

    with col2:
        time_period = st.selectbox("Time Period", ["7 days", "30 days", "90 days"])

    with col3:
        if st.button("🔍 Analyze News"):
            with st.spinner(f"Analyzing news for {symbol}..."):
                st.info(f"Analyzed {symbol} - 45 articles found")
                
                col1, col2, col3, col4 = st.columns(4)
                with col1:
                    st.metric("Sentiment", "7.2/10")
                with col2:
                    st.metric("Articles", "45")
                with col3:
                    st.metric("Positive", "32")
                with col4:
                    st.metric("Negative", "13")
                
                st.subheader("Sentiment Distribution")
                data = pd.DataFrame({'Sentiment': ['Positive', 'Negative', 'Neutral'], 'Count': [32, 13, 5]})
                fig = px.pie(data, values='Count', names='Sentiment', color_discrete_map={'Positive': '#00CC96', 'Negative': '#EF553B', 'Neutral': '#FFA15A'})
                st.plotly_chart(fig, use_container_width=True)
                
                st.subheader("Top Topics")
                st.write("• EV Expansion: 15 mentions")
                st.write("• Q4 Results: 12 mentions")
                st.write("• Partnerships: 8 mentions")

