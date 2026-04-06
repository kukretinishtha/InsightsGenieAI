"""
Real-time monitoring page module.
"""

import time

import streamlit as st

from utils import APIClient, SessionState, get_api_client, run_async


def render():
    """Render real-time monitor page."""
    st.title("⚡ Real-Time Monitor")

    st.markdown(
        "Monitor market movements in real-time and get instant alerts "
        "for significant changes."
    )

    # Monitoring setup
    col1, col2, col3 = st.columns(3)

    with col1:
        symbols_input = st.text_input(
            "Stocks to Monitor (comma-separated)",
            value="RELIANCE,TCS,INFY",
        )
        symbols = [s.strip().upper() for s in symbols_input.split(",")]

    with col2:
        refresh_interval = st.selectbox(
            "Refresh Interval",
            [30, 60, 120, 300],
            format_func=lambda x: f"{x}s",
        )

    with col3:
        auto_refresh = st.checkbox("Auto Refresh", value=True)

    if st.button("🔴 Start Live Monitoring"):
        SessionState.set("monitoring", True)

    st.markdown("---")

    if SessionState.get("monitoring"):
        # Live data display
        placeholder = st.empty()
        status_placeholder = st.empty()

        try:
            while SessionState.get("monitoring"):
                with placeholder.container():
                    st.subheader("📊 Live Market Data")

                    client = get_api_client()

                    # Fetch data for all symbols
                    live_data = {}
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
