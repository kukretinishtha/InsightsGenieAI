# Frontend User Guide

## Overview

InsightGenie AI Frontend is an interactive Streamlit dashboard for AI-powered stock analysis.

**Key Features**:
- Real-time stock analysis
- Portfolio management
- News sentiment tracking
- Geopolitical risk monitoring
- Comparative analysis
- Live market monitoring

---

## Getting Started

### Installation

```bash
cd frontend
pip install -r requirements.txt
```

### Configuration

Create `.env` file:
```bash
cp .env.example .env
```

Edit with your settings:
```
BACKEND_URL=http://localhost:8001
STREAMLIT_SERVER_PORT=8501
DEBUG=false
```

### Run Frontend

**Development**:
```bash
streamlit run src/main.py
```

**With Configuration**:
```bash
streamlit run src/main.py \
  --server.port 8501 \
  --server.address 0.0.0.0 \
  --logger.level info
```

Open browser to: `http://localhost:8501`

---

## Pages Overview

### 1. Home 🏠

**Purpose**: Landing page and system overview

**Sections**:
- Feature highlights (Smart Analysis, Portfolio Management, Global Insights)
- Quick market stats (NSE, BSE, Nifty, Sensex)
- Features overview with descriptions
- How it works explanation
- Getting started guide

**Navigation**: Select from sidebar menu

---

### 2. Stock Analysis 📈

**Purpose**: Detailed analysis of individual stocks

**Workflow**:
1. Enter stock symbol (e.g., RELIANCE, TCS, INFY)
2. Select analysis type:
   - **Quick**: Fast overview (5-10s)
   - **Comprehensive**: Full analysis (10-15s)
   - **Deep**: Detailed analysis (15-20s)
3. Click "🔍 Analyze"
4. View results in tabs

**Tabs**:

#### Overview Tab
- Current price and change percentage
- Market cap
- AI recommendation (BUY/SELL/HOLD)
- Analysis summary

#### Technical Tab
- SMA 50, RSI, MACD
- Bollinger Bands
- Volume trends
- Support/resistance levels

#### News Tab
- Sentiment score (-1 to +1)
- Recent articles
- Trending topics
- Entity mentions

#### Geopolitical Tab
- Risk level (LOW/MEDIUM/HIGH/CRITICAL)
- Risk score (0-1)
- Affected sectors
- Impact assessment

#### Details Tab
- Full JSON response
- All calculated metrics
- Historical data

**Data Layer Inspection**:
- View Bronze layer (raw data)
- View Silver layer (cleaned data)
- View Gold layer (analysis)

---

### 3. Portfolio Analysis 💼

**Purpose**: Multi-stock portfolio management and analysis

**Features**:

#### Portfolio Setup
1. Enter total portfolio size (₹)
2. Specify number of stocks
3. Enter each stock symbol
4. Set allocation weights (%)
   - System automatically normalizes weights
4. Select analysis type
5. Click "📊 Analyze Portfolio"

#### Results Display

**Summary Metrics**:
- Total portfolio value
- Number of stocks analyzed
- Average recommendation
- Overall portfolio risk level

**Holdings Performance**:
- Stock prices
- Daily changes
- Sector allocation

**AI Recommendations**:
- BUY recommendations with reasons
- SELL recommendations with reasons
- HOLD recommendations with reasons

**Risk Assessment**:
- Portfolio beta
- Maximum drawdown
- Concentration risk

---

### 4. News Analysis 📰

**Purpose**: Market news sentiment and impact analysis

**Features**:

#### Input
- Stock symbol
- Time period (7/30/90 days)
- Click "🔍 Analyze News"

#### Results

**Sentiment Overview**:
- Overall sentiment score
- Total articles analyzed
- Positive vs negative count

**Distribution**:
- Sentiment distribution chart
- Trending topics list

**Articles**:
- Recent articles (title, source, summary)
- Sentiment indicators (✅ positive, ❌ negative, ➖ neutral)
- Click to read full article

**Key Entities**:
- Mentioned companies
- Mentioned countries
- Mentioned people

---

### 5. Geopolitical Risks 🌍

**Purpose**: Track global events and assess market impact

**Three Views**:

#### Global Events View
- Critical/High/Medium/Low risk event counts
- Major geopolitical events
- Impact assessment
- Severity indicators

#### Country Risk View
- Risk scores for major countries
- Trend indicators (↑/↓/→)
- Impacting factors count
- Countries: US, China, Russia, Europe, Middle East, Japan

#### Stock Impact View
1. Enter stock symbol
2. Click "Assess Geopolitical Impact"
3. View impact metrics:
   - Risk level
   - Risk score
   - Affected sectors
   - Detailed assessment

---

### 6. Comparison Analysis 📊

**Purpose**: Compare multiple stocks side-by-side

**Workflow**:
1. Select number of stocks (2-5)
2. Enter symbols
3. Choose analysis type
4. Click "🔄 Compare Stocks"

**Comparison Views**:

**Price Metrics Table**:
- Current price
- Change percentage
- PE ratio
- Market cap

**Technical Indicators**:
- RSI, SMA 50, EMA 20
- Displayed in columns per stock
- Easy visual comparison

**Sentiment Comparison**:
- Sentiment scores
- Color indicators (positive/negative)
- Side-by-side display

**Summary**:
- Best performer highlight
- Best recommendation highlight

---

### 7. Real-Time Monitor ⚡

**Purpose**: Live market monitoring with alerts

**Setup**:
1. Enter stocks (comma-separated)
2. Select refresh interval (30/60/120/300s)
3. Toggle auto-refresh
4. Click "🔴 Start Live Monitoring"

**Live Display**:
- Price ticker (₹)
- Daily change percentage
- AI recommendation
- Color-coded status

**Alert Detection**:
- Triggers on >3% movement
- Instant notification
- Stock, direction, and percentage shown

**Watchlist Management**:
- Add stocks to watchlist
- Remove from watchlist
- Easy tracking of favorite stocks

**Historical View**:
- Toggle between live and historical
- Time period selection (1D/1W/1M/3M)
- Chart visualization

---

## Common Workflows

### Analyze a Stock

```
1. Home → Stock Analysis
2. Enter "RELIANCE"
3. Select "Comprehensive"
4. Click Analyze
5. View all tabs for complete picture
```

### Compare Two Stocks

```
1. Home → Comparison Analysis
2. Select 2 stocks
3. Enter "RELIANCE" and "TCS"
4. Click Compare
5. View side-by-side metrics
```

### Build Portfolio

```
1. Home → Portfolio Analysis
2. Enter portfolio size (₹10,00,000)
3. Add 5 stocks with weights
4. Click Analyze Portfolio
5. Review recommendations
```

### Monitor Market

```
1. Home → Real-Time Monitor
2. Enter symbols: "RELIANCE,TCS,INFY"
3. Set 60s refresh
4. Enable auto-refresh
5. Monitor alerts
```

### Track News

```
1. Home → News Analysis
2. Enter "INFY"
3. Select 30 days period
4. View sentiment and trending
5. Read relevant articles
```

---

## Tips & Tricks

### Performance Tips
- Use "Quick" analysis for fast overview
- Use "Comprehensive" for decision making
- Cache hits improve response time
- Batch analysis (portfolio) is faster than individual stocks

### Best Practices
- Compare before investing
- Check news sentiment before major trades
- Monitor geopolitical risks
- Use watchlist for tracking

### Shortcuts
- Bookmark favorite stocks
- Use browser back button
- Cmd+K (Mac) / Ctrl+K (Windows) for search

---

## Features & Components

### API Client

All pages use `APIClient` from utils:

```python
client = get_api_client()

# Single stock analysis
result = await client.analyze_stock("RELIANCE", "comprehensive")

# Batch analysis
result = await client.batch_analyze(["RELIANCE", "TCS"], "quick")

# Get data layer
result = await client.get_data_layer("RELIANCE", "gold")

# Health check
healthy = await client.health_check()
```

### Session State

Streamlit session state for maintaining state:

```python
# Store analysis state
SessionState.set("analyzing", True)
SessionState.set("current_symbol", "RELIANCE")

# Retrieve
is_analyzing = SessionState.get("analyzing")

# Clear
SessionState.delete("analyzing")
```

### Utilities

Formatting and display utilities:

```python
# Currency formatting
format_currency(2750.50)  # ₹2,750.50

# Percentage formatting
format_percent(1.25)  # 1.25%

# Recommendation formatting
emoji, color = format_recommendation("BUY")  # 🟢, green

# Display cards and alerts
display_metric_card("Price", "₹2750.50", "success")
display_alert("Analysis complete!", "success")
```

---

## Error Handling

### Backend Connection Error

```
Error: "Failed to analyze RELIANCE: Connection error"

Solutions:
1. Verify middleware is running
2. Check BACKEND_URL in .env
3. Restart frontend
4. Check network connectivity
```

### Invalid Symbol

```
Error: "Failed to analyze INVALID_SYMBOL"

Solutions:
1. Use valid NSE symbol (RELIANCE, TCS, INFY, etc.)
2. Check symbol spelling
3. Ensure symbol is uppercase
```

### Rate Limit

```
Error: "Request failed: 429 Too Many Requests"

Solutions:
1. Wait before making new requests
2. Use "Quick" analysis instead of "Comprehensive"
3. Reduce refresh frequency on real-time monitor
```

### Cache Issues

```
Issue: Stale data displayed

Solutions:
1. Refresh the page (Cmd+R / Ctrl+R)
2. Clear browser cache
3. Click "Refresh Data" button
4. Cache automatically clears after TTL
```

---

## Customization

### Change Theme

Edit `frontend/src/config.py`:
```python
class Settings(BaseModel):
    theme: str = "dark"  # Change to "dark"
```

Or via Streamlit config:
```toml
# .streamlit/config.toml
[theme]
primaryColor = "#FF6B6B"
backgroundColor = "#F5F5F5"
```

### Add Custom CSS

In page files:
```python
st.markdown("""
<style>
.custom-class {
    color: blue;
    font-weight: bold;
}
</style>
""", unsafe_allow_html=True)
```

### Modify Sidebar

Edit `main.py`:
```python
with st.sidebar:
    # Add custom widgets
    st.markdown("---")
    custom_option = st.selectbox("Custom", ["Option 1", "Option 2"])
```

---

## Deployment

### Local Development

```bash
streamlit run src/main.py
```

### Docker

```bash
docker build -f docker/Dockerfile.frontend -t insightgenie-frontend .
docker run -p 8501:8501 insightgenie-frontend
```

### Docker Compose

```bash
docker-compose up frontend
```

### Production Settings

```toml
# .streamlit/config.toml
[client]
showErrorDetails = false

[logger]
level = "warning"

[browser]
gatherUsageStats = true
```

---

## Troubleshooting

### Blank Page on Load

```
Solution:
1. Check browser console for errors
2. Verify backend is running
3. Clear browser cache
4. Try incognito/private window
```

### Slow Performance

```
Solution:
1. Use "Quick" analysis type
2. Reduce refresh frequency
3. Check network speed
4. Monitor backend logs
```

### Buttons Not Responding

```
Solution:
1. Wait for previous request to complete
2. Refresh page
3. Check backend connection
4. Restart frontend
```

---

## Next Steps

1. **Advanced Charts**
   - Interactive price charts
   - Technical indicator visualization
   - Portfolio allocation pie charts

2. **Alerts & Notifications**
   - Email alerts on price movements
   - Desktop notifications
   - Custom alert rules

3. **User Accounts**
   - Save preferences
   - Saved watchlists
   - Trade history
   - Portfolio snapshots

4. **Mobile App**
   - Responsive design
   - Native mobile app
   - Push notifications

5. **Backtesting**
   - Test strategies on historical data
   - Performance analysis
   - Risk metrics
