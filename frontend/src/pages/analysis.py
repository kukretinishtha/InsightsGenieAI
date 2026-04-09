"""
Analysis insights and recommendations page.
"""

import streamlit as st
import pandas as pd
import requests
import plotly.express as px
import plotly.graph_objects as go


def render():
    """Render analysis page."""
    st.title("🤖 AI Analysis & Insights")
    st.markdown("**Powered by Gold layer data from Databricks**")

    # API Base URL
    API_URL = "http://localhost:8000/api/v1/analysis"

    # Sidebar for quick analysis
    st.sidebar.header("📊 Quick Analysis")
    
    analysis_type = st.sidebar.radio(
        "Select Analysis:",
        ["📈 Trends", "🎯 Buy/Sell Signals", "⚠️ Risk Assessment", "💼 Portfolio", "🔍 Complete Analysis"]
    )

    if st.sidebar.button("🚀 Run Analysis"):
        st.session_state.run_analysis = True

    # Initialize session state
    if "run_analysis" not in st.session_state:
        st.session_state.run_analysis = False

    # Main tabs
    tab1, tab2, tab3, tab4, tab5 = st.tabs(["📈 Trends", "🎯 Signals", "⚠️ Risk", "💼 Portfolio", "🔍 Complete"])

    # Trend Analysis Tab
    with tab1:
        st.subheader("Trend Analysis")
        st.markdown("**Identify bullish, bearish, and neutral stocks**")
        
        if st.button("Analyze Trends"):
            with st.spinner("Analyzing trends..."):
                try:
                    response = requests.get(f"{API_URL}/trends", timeout=60)
                    if response.status_code == 200:
                        result = response.json()
                        
                        col1, col2, col3 = st.columns(3)
                        with col1:
                            st.metric("📈 Bullish", len(result.get("trends", {}).get("bullish", [])))
                        with col2:
                            st.metric("📉 Bearish", len(result.get("trends", {}).get("bearish", [])))
                        with col3:
                            st.metric("➡️ Neutral", len(result.get("trends", {}).get("neutral", [])))
                        
                        st.success(result.get("summary"))
                        
                        # Display data
                        trends_data = result.get("trends", {})
                        if trends_data.get("bullish"):
                            st.write("**Bullish Stocks:** " + ", ".join(trends_data["bullish"]))
                        if trends_data.get("bearish"):
                            st.write("**Bearish Stocks:** " + ", ".join(trends_data["bearish"]))
                        
                        # Chart
                        chart_data = pd.DataFrame({
                            "Category": ["Bullish", "Bearish", "Neutral"],
                            "Count": [
                                len(trends_data.get("bullish", [])),
                                len(trends_data.get("bearish", [])),
                                len(trends_data.get("neutral", []))
                            ]
                        })
                        fig = px.pie(chart_data, values="Count", names="Category",
                                    color_discrete_map={"Bullish": "#00CC96", "Bearish": "#EF553B", "Neutral": "#FFA15A"})
                        st.plotly_chart(fig, use_container_width=True)
                    else:
                        st.error(f"Error: {response.text}")
                except Exception as e:
                    st.error(f"Error: {str(e)}")
        else:
            # Show sample data
            st.info("Click 'Analyze Trends' to generate trend analysis from Gold layer data")
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("📈 Bullish", 3)
            with col2:
                st.metric("📉 Bearish", 1)
            with col3:
                st.metric("➡️ Neutral", 1)

    # Buy/Sell Signals Tab
    with tab2:
        st.subheader("Buy/Sell Signals")
        st.markdown("**AI-generated trading signals with confidence levels**")
        
        if st.button("Generate Signals"):
            with st.spinner("Generating signals..."):
                try:
                    response = requests.get(f"{API_URL}/signals", timeout=60)
                    if response.status_code == 200:
                        result = response.json()
                        
                        signals = result.get("signals", {})
                        col1, col2, col3 = st.columns(3)
                        with col1:
                            st.metric("🟢 BUY", len(signals.get("buy", [])))
                        with col2:
                            st.metric("🔴 SELL", len(signals.get("sell", [])))
                        with col3:
                            st.metric("🟡 HOLD", len(signals.get("hold", [])))
                        
                        st.success(result.get("summary"))
                        
                        # Display signals
                        if signals.get("buy"):
                            st.write("**BUY Signals:**")
                            for stock in signals["buy"]:
                                st.write(f"• {stock['symbol']}: {stock['confidence']} confidence @ {stock['price']}")
                        
                        if signals.get("sell"):
                            st.write("**SELL Signals:**")
                            for stock in signals["sell"]:
                                st.write(f"• {stock['symbol']}: {stock['confidence']} confidence @ {stock['price']}")
                        
                        if signals.get("hold"):
                            st.write("**HOLD Signals:**")
                            for stock in signals["hold"]:
                                st.write(f"• {stock['symbol']}: {stock['confidence']} confidence @ {stock['price']}")
                    else:
                        st.error(f"Error: {response.text}")
                except Exception as e:
                    st.error(f"Error: {str(e)}")
        else:
            st.info("Click 'Generate Signals' to get AI trading recommendations")
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("🟢 BUY", 3)
            with col2:
                st.metric("🔴 SELL", 0)
            with col3:
                st.metric("🟡 HOLD", 2)

    # Risk Assessment Tab
    with tab3:
        st.subheader("Risk Assessment")
        st.markdown("**Identify high-risk and low-risk stocks based on volatility**")
        
        if st.button("Assess Risk"):
            with st.spinner("Assessing risk..."):
                try:
                    response = requests.get(f"{API_URL}/risk", timeout=60)
                    if response.status_code == 200:
                        result = response.json()
                        
                        risk_levels = result.get("risk_levels", {})
                        col1, col2, col3 = st.columns(3)
                        with col1:
                            st.metric("🟢 Low Risk", len(risk_levels.get("low", [])))
                        with col2:
                            st.metric("🟡 Medium Risk", len(risk_levels.get("medium", [])))
                        with col3:
                            st.metric("🔴 High Risk", len(risk_levels.get("high", [])))
                        
                        st.success(result.get("summary"))
                        st.info(f"💡 {result.get('recommendation')}")
                        
                        # Display by risk level
                        if risk_levels.get("low"):
                            st.write("**Low Risk Stocks (Stable):**")
                            for stock in risk_levels["low"]:
                                st.write(f"• {stock['symbol']}: Volatility {stock['volatility']}% | Risk Score {stock['risk_score']}")
                        
                        if risk_levels.get("medium"):
                            st.write("**Medium Risk Stocks (Balanced):**")
                            for stock in risk_levels["medium"]:
                                st.write(f"• {stock['symbol']}: Volatility {stock['volatility']}% | Risk Score {stock['risk_score']}")
                        
                        if risk_levels.get("high"):
                            st.write("**High Risk Stocks (Growth):**")
                            for stock in risk_levels["high"]:
                                st.write(f"• {stock['symbol']}: Volatility {stock['volatility']}% | Risk Score {stock['risk_score']}")
                    else:
                        st.error(f"Error: {response.text}")
                except Exception as e:
                    st.error(f"Error: {str(e)}")
        else:
            st.info("Click 'Assess Risk' to evaluate stock volatility and risk levels")
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("🟢 Low Risk", 1)
            with col2:
                st.metric("🟡 Medium Risk", 3)
            with col3:
                st.metric("🔴 High Risk", 1)

    # Portfolio Recommendations Tab
    with tab4:
        st.subheader("Portfolio Recommendations")
        st.markdown("**Get personalized portfolio strategies based on risk tolerance**")
        
        if st.button("Get Recommendations"):
            with st.spinner("Generating recommendations..."):
                try:
                    response = requests.get(f"{API_URL}/portfolio", timeout=60)
                    if response.status_code == 200:
                        result = response.json()
                        
                        st.success(result.get("summary"))
                        st.info(f"🎯 Best Choice: {result.get('best_choice')}")
                        
                        recommendations = result.get("recommendations", {})
                        
                        # Create tabs for each strategy
                        strat1, strat2, strat3 = st.tabs(["Aggressive", "Balanced", "Conservative"])
                        
                        with strat1:
                            aggressive = recommendations.get("aggressive", {})
                            st.write(f"**Stocks:** {', '.join(aggressive.get('stocks', []))}")
                            st.write(f"**Allocation:** {aggressive.get('allocation')}")
                            st.write(f"**Expected Return:** {aggressive.get('expected_return')}")
                        
                        with strat2:
                            balanced = recommendations.get("balanced", {})
                            st.write(f"**Stocks:** {', '.join(balanced.get('stocks', []))}")
                            st.write(f"**Allocation:** {balanced.get('allocation')}")
                            st.write(f"**Expected Return:** {balanced.get('expected_return')}")
                        
                        with strat3:
                            conservative = recommendations.get("conservative", {})
                            st.write(f"**Stocks:** {', '.join(conservative.get('stocks', []))}")
                            st.write(f"**Allocation:** {conservative.get('allocation')}")
                            st.write(f"**Expected Return:** {conservative.get('expected_return')}")
                    else:
                        st.error(f"Error: {response.text}")
                except Exception as e:
                    st.error(f"Error: {str(e)}")
        else:
            st.info("Click 'Get Recommendations' to receive personalized portfolio strategies")
            with st.expander("View Sample Strategies"):
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.write("**Aggressive**\nHigh growth stocks\nExpected: 12-15%")
                with col2:
                    st.write("**Balanced**\nMixed allocation\nExpected: 8-10%")
                with col3:
                    st.write("**Conservative**\nStable stocks\nExpected: 5-7%")

    # Complete Analysis Tab
    with tab5:
        st.subheader("Complete Analysis Dashboard")
        st.markdown("**Run all analysis types and get comprehensive insights**")
        
        col1, col2 = st.columns([3, 1])
        with col1:
            st.write("This runs Trends + Signals + Risk + Portfolio analysis in one go")
        with col2:
            if st.button("▶️ Run Complete Analysis"):
                st.session_state.complete_analysis = True
        
        if st.session_state.get("complete_analysis"):
            with st.spinner("Running complete analysis..."):
                try:
                    response = requests.get(f"{API_URL}/complete", timeout=120)
                    if response.status_code == 200:
                        result = response.json()
                        
                        st.success("✅ Complete analysis finished!")
                        
                        analysis = result.get("analysis_results", {})
                        
                        # Show summary boxes
                        col1, col2, col3, col4 = st.columns(4)
                        
                        with col1:
                            trends = analysis.get("trends", {})
                            st.metric("Trends", trends.get("summary", "N/A"))
                        
                        with col2:
                            signals = analysis.get("signals", {})
                            st.metric("Signals", signals.get("summary", "N/A"))
                        
                        with col3:
                            risk = analysis.get("risk", {})
                            st.metric("Risk", risk.get("summary", "N/A"))
                        
                        with col4:
                            portfolio = analysis.get("portfolio", {})
                            st.metric("Portfolio", portfolio.get("best_choice", "N/A"))
                        
                        st.divider()
                        
                        # Show detailed results
                        st.write("**Detailed Analysis Results:**")
                        st.json(analysis)
                        
                    else:
                        st.error(f"Error: {response.text}")
                except Exception as e:
                    st.error(f"Error: {str(e)}")
        else:
            st.info("👉 Click 'Run Complete Analysis' to see all insights in one dashboard")

    st.markdown("---")
    st.markdown("""
    **How Analysis Works:**
    - **Trends:** Analyzes price movements and identifies bullish/bearish patterns
    - **Signals:** Uses volatility & trends to generate BUY/SELL/HOLD recommendations
    - **Risk:** Assesses stock volatility and overall portfolio risk levels
    - **Portfolio:** Suggests optimal allocations based on risk tolerance
    
    All analysis is powered by data in the Gold layer from Databricks.
    """)
