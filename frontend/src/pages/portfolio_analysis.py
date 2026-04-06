"""
Portfolio analysis page module.
"""

import streamlit as st

from utils import APIClient, get_api_client, run_async


def render():
    """Render portfolio analysis page."""
    st.title("💼 Portfolio Analysis")

    st.markdown(
        "Analyze your entire investment portfolio with AI-powered "
        "optimization and risk assessment."
    )

    # Portfolio input
    st.subheader("📋 Your Portfolio")

    col1, col2 = st.columns(2)

    with col1:
        portfolio_size = st.number_input(
            "Portfolio Size (₹)", value=1000000, step=10000
        )

    with col2:
        num_stocks = st.number_input("Number of Stocks", value=5, step=1)

    # Stock inputs
    portfolio_stocks = {}
    st.markdown("### Stock Allocation")

    cols = st.columns(num_stocks)
    for idx in range(num_stocks):
        with cols[idx]:
            symbol = st.text_input(
                f"Stock {idx + 1}", value="RELIANCE", key=f"stock_{idx}"
            ).upper()
            weight = st.number_input(
                f"Weight {idx + 1} (%)",
                value=20.0,
                key=f"weight_{idx}",
            )
            portfolio_stocks[symbol] = weight / 100.0

    # Normalize weights
    total_weight = sum(portfolio_stocks.values())
    if total_weight > 0:
        portfolio_stocks = {
            k: v / total_weight for k, v in portfolio_stocks.items()
        }

    col1, col2 = st.columns(2)

    with col1:
        analysis_type = st.selectbox("Analysis Type", ["quick", "comprehensive"])

    with col2:
        if st.button("📊 Analyze Portfolio", use_container_width=True):
            with st.spinner("Analyzing portfolio..."):
                client = get_api_client()
                result = run_async(
                    client.batch_analyze(
                        list(portfolio_stocks.keys()), analysis_type
                    )
                )

                if result and result.get("success"):
                    data = result.get("data", {})

                    st.success("Portfolio analysis completed!")

                    # Summary metrics
                    col1, col2, col3, col4 = st.columns(4)
                    with col1:
                        st.metric("Portfolio Value", f"₹{portfolio_size:,.0f}")
                    with col2:
                        st.metric("Stocks Analyzed", len(portfolio_stocks))
                    with col3:
                        st.metric(
                            "Avg Recommendation",
                            data.get("avg_recommendation", "HOLD"),
                        )
                    with col4:
                        st.metric(
                            "Portfolio Risk", data.get("risk_level", "MEDIUM")
                        )

                    # Holdings breakdown
                    st.markdown("---")
                    st.subheader("📈 Holdings Performance")

                    holdings = data.get("holdings", {})
                    for symbol, info in holdings.items():
                        col1, col2, col3 = st.columns([2, 1, 1])
                        with col1:
                            st.write(f"**{symbol}** - {info.get('name', '')}")
                        with col2:
                            st.write(f"₹{info.get('price', 0):.2f}")
                        with col3:
                            st.write(f"{info.get('change', 0):.2f}%")

                    # Recommendations
                    st.markdown("---")
                    st.subheader("💡 Recommendations")

                    recommendations = data.get("recommendations", [])
                    for rec in recommendations:
                        if rec.get("action") == "BUY":
                            st.success(
                                f"**{rec.get('symbol')}**: {rec.get('reason')}"
                            )
                        elif rec.get("action") == "SELL":
                            st.error(
                                f"**{rec.get('symbol')}**: {rec.get('reason')}"
                            )
                        else:
                            st.info(
                                f"**{rec.get('symbol')}**: {rec.get('reason')}"
                            )

                else:
                    st.error("Portfolio analysis failed")

    # Risk assessment
    st.markdown("---")
    st.subheader("⚠️ Risk Assessment")

    col1, col2, col3 = st.columns(3)
    with col1:
        st.info("**Portfolio Beta**: 1.2")
    with col2:
        st.warning("**Max Drawdown**: 15.3%")
    with col3:
        st.error("**Concentration Risk**: High (30% in one stock)")
