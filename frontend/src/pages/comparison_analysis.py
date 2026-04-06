"""
Comparison analysis page module.
"""

import streamlit as st

from utils import APIClient, SessionState, get_api_client, run_async


def render():
    """Render comparison analysis page."""
    st.title("📊 Comparison Analysis")

    st.markdown(
        "Compare multiple stocks side-by-side to make better investment decisions."
    )

    # Setup columns
    num_stocks = st.slider("Number of Stocks to Compare", 2, 5, 3)

    col1, col2 = st.columns(2)

    with col1:
        analysis_type = st.selectbox("Analysis Type", ["quick", "comprehensive"])

    with col2:
        if st.button("🔄 Compare Stocks", use_container_width=True):
            SessionState.set("comparing", True)

    st.markdown("---")

    # Stock input
    symbols = []
    cols = st.columns(num_stocks)

    for idx in range(num_stocks):
        with cols[idx]:
            symbol = st.text_input(
                f"Stock {idx + 1}",
                value=["RELIANCE", "TCS", "INFY", "WIPRO", "HDFC"][idx],
                key=f"compare_stock_{idx}",
            ).upper()
            symbols.append(symbol)

    if SessionState.get("comparing"):
        with st.spinner("Comparing stocks..."):
            client = get_api_client()

            comparison_data = {}
            for symbol in symbols:
                result = run_async(client.analyze_stock(symbol, analysis_type))
                if result and result.get("success"):
                    comparison_data[symbol] = result.get("data", {})

            if comparison_data:
                st.success("Comparison completed!")

                # Metrics comparison table
                st.subheader("📊 Price Metrics")

                metrics_cols = ["Current Price", "Change %", "PE Ratio", "Market Cap"]
                col_specs = [2] + [1] * len(metrics_cols)
                cols = st.columns(col_specs)

                with cols[0]:
                    st.write("**Stock**")
                for col, metric in zip(cols[1:], metrics_cols):
                    with col:
                        st.write(f"**{metric}**")

                for symbol in symbols:
                    cols = st.columns(col_specs)
                    data = comparison_data.get(symbol, {})

                    with cols[0]:
                        st.write(f"**{symbol}**")

                    with cols[1]:
                        st.write(f"₹{data.get('price', 0):.2f}")

                    with cols[2]:
                        st.write(f"{data.get('change', 0):.2f}%")

                    with cols[3]:
                        st.write(f"{data.get('pe_ratio', 0):.2f}")

                    with cols[4]:
                        st.write(f"₹{data.get('market_cap', 0)/10**5:.0f}Cr")

                st.markdown("---")

                # Technical indicators comparison
                st.subheader("🔧 Technical Indicators")

                tech_cols = st.columns(len(symbols))
                for col, symbol in zip(tech_cols, symbols):
                    with col:
                        data = comparison_data.get(symbol, {})
                        tech = data.get("technical", {})

                        st.write(f"**{symbol}**")
                        st.metric("RSI", f"{tech.get('rsi', 0):.2f}")
                        st.metric("SMA 50", f"{tech.get('sma_50', 0):.2f}")
                        st.metric("EMA 20", f"{tech.get('ema_20', 0):.2f}")

                st.markdown("---")

                # Sentiment comparison
                st.subheader("💭 News Sentiment")

                sentiment_cols = st.columns(len(symbols))
                for col, symbol in zip(sentiment_cols, symbols):
                    with col:
                        data = comparison_data.get(symbol, {})
                        news = data.get("news", {})
                        sentiment = news.get("sentiment_score", 0)

                        st.write(f"**{symbol}**")
                        if sentiment > 0.5:
                            st.success(f"Positive: {sentiment:.2f}")
                        elif sentiment < -0.5:
                            st.error(f"Negative: {sentiment:.2f}")
                        else:
                            st.info(f"Neutral: {sentiment:.2f}")

                st.markdown("---")

                # Recommendations
                st.subheader("💡 Comparison Summary")

                col1, col2 = st.columns(2)

                with col1:
                    st.markdown("### Best Performer")
                    best = max(
                        symbols,
                        key=lambda s: comparison_data.get(s, {}).get("change", 0),
                    )
                    st.success(f"🏆 {best}")

                with col2:
                    st.markdown("### Best Recommendation")
                    best_rec = max(
                        symbols,
                        key=lambda s: {
                            "STRONG BUY": 5,
                            "BUY": 4,
                            "HOLD": 3,
                            "SELL": 2,
                            "STRONG SELL": 1,
                        }.get(
                            comparison_data.get(s, {}).get("recommendation", "HOLD"),
                            0,
                        ),
                    )
                    st.info(f"🎯 {best_rec}")

        SessionState.set("comparing", False)
