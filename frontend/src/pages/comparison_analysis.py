"""
Comparison analysis page module.
"""

import streamlit as st
import pandas as pd
import plotly.express as px


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
        time_period = st.selectbox("Time Period", ["1M", "3M", "6M", "1Y"])

    with col2:
        if st.button("🔄 Compare Stocks", use_container_width=True):
            st.session_state.comparing = True

    st.markdown("---")

    # Stock input
    symbols = []
    cols = st.columns(num_stocks)
    default_stocks = ["RELIANCE", "TCS", "INFY", "WIPRO", "HDFC"]

    for idx in range(num_stocks):
        with cols[idx]:
            symbol = st.text_input(
                f"Stock {idx + 1}",
                value=default_stocks[idx],
                key=f"compare_stock_{idx}",
            ).upper()
            symbols.append(symbol)

    if st.session_state.get("comparing", False):
        # Sample comparison data
        comparison_data = {
            "RELIANCE": {
                "price": 2850.50,
                "change": 2.5,
                "pe_ratio": 26.5,
                "market_cap": 25.8,
                "one_month": 3.2,
                "three_month": 5.8,
                "one_year": 12.5,
                "rsi": 68,
                "macd": "Positive"
            },
            "TCS": {
                "price": 3450.75,
                "change": 1.8,
                "pe_ratio": 24.2,
                "market_cap": 14.2,
                "one_month": 2.1,
                "three_month": 3.5,
                "one_year": 8.9,
                "rsi": 62,
                "macd": "Positive"
            },
            "INFY": {
                "price": 1760.25,
                "change": 0.5,
                "pe_ratio": 22.8,
                "market_cap": 7.5,
                "one_month": 1.2,
                "three_month": 2.3,
                "one_year": 5.2,
                "rsi": 55,
                "macd": "Neutral"
            },
            "WIPRO": {
                "price": 410.80,
                "change": -1.2,
                "pe_ratio": 18.5,
                "market_cap": 2.8,
                "one_month": -0.5,
                "three_month": 1.2,
                "one_year": 3.5,
                "rsi": 48,
                "macd": "Neutral"
            },
            "HDFC": {
                "price": 2720.50,
                "change": 3.1,
                "pe_ratio": 20.1,
                "market_cap": 5.9,
                "one_month": 4.2,
                "three_month": 6.8,
                "one_year": 15.2,
                "rsi": 72,
                "macd": "Positive"
            }
        }

        st.success("✅ Comparison ready!")

        # Metrics comparison table
        st.subheader("📊 Price Metrics")

        comparison_df = pd.DataFrame({
            "Stock": symbols,
            "Price (₹)": [comparison_data.get(s, {}).get("price", 0) for s in symbols],
            "Change (%)": [comparison_data.get(s, {}).get("change", 0) for s in symbols],
            "PE Ratio": [comparison_data.get(s, {}).get("pe_ratio", 0) for s in symbols],
            "Market Cap (Cr)": [comparison_data.get(s, {}).get("market_cap", 0) for s in symbols],
        })
        
        st.dataframe(comparison_df, use_container_width=True)

        st.markdown("---")

        # Performance comparison chart
        st.subheader("📈 Performance Comparison")
        
        perf_periods = [f"one_month", "three_month", "one_year"]
        perf_labels = ["1 Month", "3 Months", "1 Year"]
        
        perf_data = {}
        for symbol in symbols:
            perf_data[symbol] = [
                comparison_data.get(symbol, {}).get(p, 0) for p in perf_periods
            ]
        
        perf_df = pd.DataFrame(perf_data, index=perf_labels).T
        
        fig = px.bar(
            perf_df,
            barmode="group",
            title="Performance Comparison Over Time",
            labels={"value": "Return (%)", "index": "Stock"},
        )
        st.plotly_chart(fig, use_container_width=True)

        st.markdown("---")

        # Technical indicators comparison
        st.subheader("🔧 Technical Indicators")

        tech_cols = st.columns(len(symbols))
        for col, symbol in zip(tech_cols, symbols):
            with col:
                data = comparison_data.get(symbol, {})
                st.metric(f"{symbol} RSI", f"{data.get('rsi', 0):.0f}", 
                         delta=f"MACD: {data.get('macd', 'N/A')}")

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
