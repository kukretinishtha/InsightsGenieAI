"""
News analysis page module.
"""

import streamlit as st

from utils import APIClient, get_api_client, run_async


def render():
    """Render news analysis page."""
    st.title("📰 News Analysis")

    st.markdown(
        "Analyze market news sentiment and its impact on stock prices "
        "using advanced NLP."
    )

    col1, col2, col3 = st.columns(3)

    with col1:
        symbol = st.text_input(
            "Stock Symbol", value="RELIANCE", help="NSE symbol"
        ).upper()

    with col2:
        time_period = st.selectbox("Time Period", ["7 days", "30 days", "90 days"])

    with col3:
        if st.button("🔍 Analyze News", use_container_width=True):
            with st.spinner(f"Analyzing news for {symbol}..."):
                client = get_api_client()
                result = run_async(client.analyze_stock(symbol, "comprehensive"))

                if result and result.get("success"):
                    data = result.get("data", {})
                    news_data = data.get("news", {})

                    # Sentiment overview
                    col1, col2, col3, col4 = st.columns(4)
                    with col1:
                        sentiment = news_data.get("sentiment_score", 0)
                        st.metric("Sentiment Score", f"{sentiment:.2f}")

                    with col2:
                        st.metric("Total Articles", news_data.get("article_count", 0))

                    with col3:
                        positive = news_data.get("positive_count", 0)
                        st.metric("Positive", positive)

                    with col4:
                        negative = news_data.get("negative_count", 0)
                        st.metric("Negative", negative)

                    st.markdown("---")

                    # Sentiment distribution
                    st.subheader("📊 Sentiment Distribution")

                    col1, col2 = st.columns(2)

                    with col1:
                        sentiment_dist = news_data.get("sentiment_distribution", {})
                        st.bar_chart(sentiment_dist)

                    with col2:
                        # Trending topics
                        st.markdown("### 🏷️ Trending Topics")
                        trends = news_data.get("trending_topics", [])
                        for topic in trends[:10]:
                            st.caption(f"• {topic}")

                    st.markdown("---")

                    # Recent articles
                    st.subheader("📄 Recent Articles")

                    articles = news_data.get("articles", [])
                    for article in articles[:10]:
                        col1, col2 = st.columns([4, 1])
                        with col1:
                            st.markdown(f"**{article.get('title', 'Untitled')}**")
                            st.caption(article.get("source", "Unknown source"))
                            st.caption(article.get("summary", "No summary"))

                        with col2:
                            sentiment_label = article.get("sentiment", "neutral")
                            if sentiment_label == "positive":
                                st.success("✅")
                            elif sentiment_label == "negative":
                                st.error("❌")
                            else:
                                st.info("➖")

                    # Key entities
                    st.markdown("---")
                    st.subheader("🏢 Key Entities Mentioned")

                    entities = news_data.get("entities", {})
                    col1, col2, col3 = st.columns(3)

                    with col1:
                        st.markdown("**Companies**")
                        for entity in entities.get("companies", [])[:5]:
                            st.caption(f"• {entity}")

                    with col2:
                        st.markdown("**Countries**")
                        for entity in entities.get("countries", [])[:5]:
                            st.caption(f"• {entity}")

                    with col3:
                        st.markdown("**People**")
                        for entity in entities.get("people", [])[:5]:
                            st.caption(f"• {entity}")

                else:
                    st.error("Failed to analyze news")
