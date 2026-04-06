"""
Geopolitical risks page module.
"""

import streamlit as st

from utils import APIClient, get_api_client, run_async


def render():
    """Render geopolitical risks page."""
    st.title("🌍 Geopolitical Risks")

    st.markdown(
        "Track global geopolitical events and assess their impact on "
        "Indian market and your investments."
    )

    col1, col2 = st.columns(2)

    with col1:
        view_type = st.radio(
            "View Type",
            ["Global Events", "Country Risk", "Stock Impact"],
            horizontal=True,
        )

    with col2:
        if st.button("🔄 Refresh Data", use_container_width=True):
            st.rerun()

    st.markdown("---")

    if view_type == "Global Events":
        st.subheader("🌐 Recent Geopolitical Events")

        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Critical Events", 2)
        with col2:
            st.metric("High Risk", 5)
        with col3:
            st.metric("Medium Risk", 8)
        with col4:
            st.metric("Low Risk", 12)

        st.markdown("### Major Events")

        events = [
            {
                "title": "US-China Trade Tensions",
                "severity": "CRITICAL",
                "impact": "Trade policies affecting Indian tech exports",
                "date": "2026-04-06",
            },
            {
                "title": "Russia-Europe Energy Crisis",
                "severity": "HIGH",
                "impact": "Oil prices increasing, energy inflation",
                "date": "2026-04-05",
            },
            {
                "title": "Middle East Political Unrest",
                "severity": "HIGH",
                "impact": "Oil supply disruptions possible",
                "date": "2026-04-04",
            },
        ]

        for event in events:
            col1, col2 = st.columns([3, 1])
            with col1:
                st.markdown(f"**{event['title']}**")
                st.caption(f"Impact: {event['impact']}")
                st.caption(f"Date: {event['date']}")

            with col2:
                severity = event["severity"]
                if severity == "CRITICAL":
                    st.error(severity)
                elif severity == "HIGH":
                    st.warning(severity)
                else:
                    st.info(severity)

    elif view_type == "Country Risk":
        st.subheader("🏙️ Country Risk Assessment")

        col1, col2, col3 = st.columns(3)

        countries = {
            "United States": {"risk_score": 0.65, "trend": "↑", "factors": 3},
            "China": {"risk_score": 0.72, "trend": "↑", "factors": 4},
            "Russia": {"risk_score": 0.85, "trend": "↓", "factors": 5},
            "Europe": {"risk_score": 0.58, "trend": "→", "factors": 2},
            "Middle East": {"risk_score": 0.78, "trend": "↑", "factors": 4},
            "Japan": {"risk_score": 0.42, "trend": "→", "factors": 1},
        }

        for idx, (country, data) in enumerate(countries.items()):
            with st.container():
                col1, col2, col3 = st.columns([2, 1, 1])

                with col1:
                    st.write(f"**{country}**")

                with col2:
                    risk_score = data["risk_score"]
                    st.metric(
                        "Risk Score",
                        f"{risk_score:.2f}",
                        delta=data["trend"],
                    )

                with col3:
                    st.caption(f"Factors: {data['factors']}")

    else:  # Stock Impact
        st.subheader("📈 Stock Impact Assessment")

        symbol = st.text_input(
            "Stock Symbol", value="RELIANCE", help="NSE symbol"
        ).upper()

        if st.button("Assess Geopolitical Impact"):
            with st.spinner(f"Assessing geopolitical impact on {symbol}..."):
                client = get_api_client()
                result = run_async(client.analyze_stock(symbol, "comprehensive"))

                if result and result.get("success"):
                    data = result.get("data", {})
                    geo_data = data.get("geopolitical", {})

                    # Risk metrics
                    col1, col2, col3 = st.columns(3)

                    with col1:
                        risk_level = geo_data.get("risk_level", "MEDIUM")
                        if risk_level == "CRITICAL":
                            st.error(f"Risk Level: {risk_level}")
                        elif risk_level == "HIGH":
                            st.warning(f"Risk Level: {risk_level}")
                        else:
                            st.info(f"Risk Level: {risk_level}")

                    with col2:
                        risk_score = geo_data.get("risk_score", 0)
                        st.metric("Risk Score", f"{risk_score:.2f}/1.0")

                    with col3:
                        affected_sectors = geo_data.get(
                            "affected_sectors_count", 0
                        )
                        st.metric("Affected Sectors", affected_sectors)

                    # Affected sectors
                    st.markdown("### Affected Sectors")

                    sectors = geo_data.get("affected_sectors", [])
                    for sector in sectors:
                        st.write(f"• {sector}")

                    # Recommendations
                    st.markdown("### Impact Assessment")
                    st.info(geo_data.get("assessment", "No assessment available"))

                else:
                    st.error("Failed to assess geopolitical impact")
