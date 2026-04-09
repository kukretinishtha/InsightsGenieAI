"""
Real-time monitoring page module.
"""

import time
import streamlit as st
import pandas as pd
import plotly.express as px


def render():
    """Render real-time monitor page."""
    st.title("⚡ Real-Time Monitor")

    st.markdown(
        "Monitor market movements and track key metrics for selected stocks."
    )

    # Monitoring setup
    col1, col2, col3 = st.columns(3)

    with col1:
        symbols_input = st.text_input(
            "Stocks to Monitor (comma-separated)",
            value="RELIANCE,TCS,INFY",
        )
        symbols = [s.strip().upper() for s in symbols_input.split(",") if s.strip()]

    with col2:
        refresh_interval = st.selectbox(
            "Refresh Interval", 
            [30, 60, 120, 300],
            format_func=lambda x: f"{x}s",
        )

    with col3:
        if st.button("🔴 Start Monitoring", use_container_width=True):
            st.session_state.monitoring = True

    st.markdown("---")

    if st.session_state.get("monitoring", False):
        # Sample real-time data
        live_data = {
            "RELIANCE": {
                "price": 2850.50,
                "change": 2.5,
                "volume": 12500000,
                "bid": 2849.75,
                "ask": 2851.25,
                "52w_high": 3200,
                "52w_low": 2400,
            },
            "TCS": {
                "price": 3450.75,
                "change": 1.8,
                "volume": 8900000,
                "bid": 3449.50,
                "ask": 3451.90,
                "52w_high": 3750,
                "52w_low": 2950,
            },
            "INFY": {
                "price": 1760.25,
                "change": 0.5,
                "volume": 10200000,
                "bid": 1759.75,
                "ask": 1760.75,
                "52w_high": 1900,
                "52w_low": 1550,
            },
        }

        st.subheader("📊 Live Market Data")

        # Create monitoring table
        monitor_data = []
        for symbol in symbols:
            if symbol in live_data:
                data = live_data[symbol]
                monitor_data.append({
                    "Symbol": symbol,
                    "Price (₹)": f"{data['price']:.2f}",
                    "Change (%)": f"{data['change']:+.2f}",
                    "Volume": f"{data['volume']:,}",
                    "Bid": f"{data['bid']:.2f}",
                    "Ask": f"{data['ask']:.2f}",
                    "52W High": f"{data['52w_high']:.2f}",
                    "52W Low": f"{data['52w_low']:.2f}",
                })

        monitor_df = pd.DataFrame(monitor_data)
        st.dataframe(monitor_df, use_container_width=True, height=150)

        st.markdown("---")

        # Price movement chart
        st.subheader("📈 Price Movement")

        # Historical data for chart
        hours = list(range(0, 6))
        price_data = {
            "RELIANCE": [2795, 2810, 2825, 2835, 2845, 2851],
            "TCS": [3380, 3400, 3420, 3435, 3445, 3451],
            "INFY": [1730, 1740, 1750, 1760, 1760, 1760],
        }

        chart_df = pd.DataFrame({
            "Hour": hours * len(symbols),
            "Price": [p for prices in price_data.values() for p in prices],
            "Stock": [[s] * 6 for s in symbols][0] + [[s] * 6 for s in symbols][1] + 
                     [[s] * 6 for s in symbols][2],
        })
        
        # Simplified chart data
        chart_data = []
        for symbol in symbols:
            if symbol in price_data:
                for hour, price in enumerate(price_data[symbol]):
                    chart_data.append({"Hour": hour, "Price (₹)": price, "Stock": symbol})

        chart_df = pd.DataFrame(chart_data)
        
        fig = px.line(
            chart_df,
            x="Hour",
            y="Price (₹)",
            color="Stock",
            title="Price Movement (Last 6 Hours)",
            markers=True
        )
        st.plotly_chart(fig, use_container_width=True)

        st.markdown("---")

        # Key metrics
        st.subheader("📌 Key Metrics")

        metric_cols = st.columns(len(symbols))
        for col, symbol in zip(metric_cols, symbols):
            if symbol in live_data:
                with col:
                    data = live_data[symbol]
                    st.metric(
                        symbol,
                        f"₹{data['price']:.2f}",
                        delta=f"{data['change']:+.2f}%"
                    )

        st.markdown("---")
        st.info("💡 Tip: Data updates every {} seconds when auto-refresh is enabled".format(refresh_interval))
                    for symbol in symbols:
                        result = run_async(
                            client.analyze_stock(symbol, "quick")
                        )
                        if result and result.get("success"):
                            live_data[symbol] = result.get("data", {})

                    if live_data:
                        # Display in columns
                        cols = st.columns(len(symbols))

                        for col, symbol in zip(cols, symbols):
                            with col:
                                data = live_data.get(symbol, {})
                                price = data.get("price", 0)
                                change = data.get("change", 0)
                                recommendation = data.get(
                                    "recommendation", "HOLD"
                                )

                                st.metric(
                                    symbol,
                                    f"₹{price:.2f}",
                                    delta=f"{change:.2f}%",
                                )

                                if recommendation in ["STRONG BUY", "BUY"]:
                                    st.success(recommendation)
                                elif recommendation in ["SELL", "STRONG SELL"]:
                                    st.error(recommendation)
                                else:
                                    st.info(recommendation)

                    # Status and alerts
                    with status_placeholder.container():
                        col1, col2, col3 = st.columns(3)

                        with col1:
                            st.info(f"✅ Data refreshed at {time.strftime('%H:%M:%S')}")

                        with col2:
                            st.write(f"📊 Monitoring {len(symbols)} stocks")

                        with col3:
                            if auto_refresh:
                                st.write(f"🔄 Next refresh in {refresh_interval}s")

                    # Alert detection
                    st.markdown("---")
                    st.subheader("🚨 Alerts")

                    alerts_found = False
                    for symbol in symbols:
                        data = live_data.get(symbol, {})
                        change = data.get("change", 0)

                        if change > 3:
                            st.success(
                                f"📈 **{symbol}** up {change:.2f}% - Strong upward movement"
                            )
                            alerts_found = True

                        elif change < -3:
                            st.error(
                                f"📉 **{symbol}** down {change:.2f}% - Significant decline"
                            )
                            alerts_found = True

                    if not alerts_found:
                        st.info("No significant alerts at this time")

                if auto_refresh:
                    time.sleep(refresh_interval)
                else:
                    break

        except KeyboardInterrupt:
            SessionState.set("monitoring", False)
            st.info("Monitoring stopped")

    # Historical view
    st.markdown("---")
    st.subheader("📈 Historical View")

    time_period = st.selectbox(
        "Time Period",
        ["1 Day", "1 Week", "1 Month", "3 Months"],
    )

    st.info("Chart and historical data visualization would be displayed here")

    # Watchlist
    st.markdown("---")
    st.subheader("⭐ Your Watchlist")

    watchlist = SessionState.get("watchlist", [])

    col1, col2 = st.columns([3, 1])
    with col1:
        new_symbol = st.text_input("Add to watchlist")

    with col2:
        if st.button("Add"):
            if new_symbol and new_symbol.upper() not in watchlist:
                watchlist.append(new_symbol.upper())
                SessionState.set("watchlist", watchlist)
                st.rerun()

    if watchlist:
        st.write("**Current Watchlist:**")
        for symbol in watchlist:
            col1, col2 = st.columns([3, 1])
            with col1:
                st.write(f"• {symbol}")

            with col2:
                if st.button(f"Remove", key=f"remove_{symbol}"):
                    watchlist.remove(symbol)
                    SessionState.set("watchlist", watchlist)
                    st.rerun()
