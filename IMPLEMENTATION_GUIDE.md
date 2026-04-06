"""Implementation Guide for InsightGenie AI."""

# InsightGenie AI - Python Implementation Guide

## Overview

InsightGenie AI is a three-tier distributed system for real-time Indian stock market prediction with geopolitical analysis.

### Architecture Tiers

1. **Frontend**: Streamlit/Dash (Python-based UI)
2. **Middleware**: FastAPI (Request routing, rate limiting, caching)
3. **Backend**: FastAPI + Agents (Core analysis engine)

## Implementation Status

### ✅ Completed (Phase 1)

#### Backend Foundation
- [x] BaseAgent abstract class with tool registration
- [x] Tool execution framework with timeout handling
- [x] Parallel tool execution using asyncio.gather
- [x] Execution history tracking
- [x] Comprehensive error handling

#### Configuration & Setup
- [x] Pydantic Settings for environment management
- [x] .env.example with all required variables
- [x] Structured logging with JSON formatter
- [x] Log rotation and file handling

#### Data Models
- [x] StockData model with technical indicators
- [x] StockPrediction model with confidence scores
- [x] AnalysisResult combining all agent outputs
- [x] Request/Response models for API

#### Async Utilities
- [x] execute_with_timeout for timeout protection
- [x] execute_with_retry with exponential backoff
- [x] gather_with_timeout for parallel operations
- [x] batch_process for controlled concurrency
- [x] RateLimiter using token bucket algorithm
- [x] AsyncCache with TTL support

#### Genie MCP Integration
- [x] GenieApiClient with async/await
- [x] Task submission to Genie API
- [x] Intelligent polling with exponential backoff
- [x] PollingManager with multiple strategies
- [x] RequestQueue with priority support
- [x] Response caching and deduplication

#### Prompts Library
- [x] System prompts for all agent types
- [x] Stock analyzer prompt
- [x] Geopolitical analyst prompt
- [x] News sentiment analyst prompt
- [x] Prediction synthesis prompt

#### FastAPI Application
- [x] Main application setup with lifespan
- [x] CORS middleware configuration
- [x] Global exception handlers
- [x] Health check endpoint
- [x] Root endpoint with API info

#### Docker & Deployment
- [x] Dockerfile for backend service
- [x] docker-compose.yml with all services
- [x] PostgreSQL, MongoDB, Redis services
- [x] Volume management for persistence
- [x] Health checks in Docker

#### Tests & Documentation
- [x] Unit tests for agents
- [x] Unit tests for async utilities
- [x] Comprehensive README
- [x] Code examples in docstrings
- [x] Type hints throughout

## Next Steps (Phase 2-7)

### Phase 2: Agent Implementation (Weeks 5-8)

```python
# StockAnalyzerAgent
from src.agents.stock_analyzer import StockAnalyzerAgent

agent = StockAnalyzerAgent()
result = await agent.analyze(symbol="RELIANCE")

# Register additional tools
agent.register_tool(
    "fetch_fundamentals",
    "Get fundamental data",
    fetch_fundamentals_func
)
```

### Phase 3: Orchestration (Weeks 9-11)

```python
# Run agents in parallel
from src.orchestrator import AnalysisOrchestrator

orchestrator = AnalysisOrchestrator()
result = await orchestrator.analyze_stock("RELIANCE")

# Result includes:
# - Stock technical analysis
# - Geopolitical impact assessment
# - News sentiment analysis
# - Synthesized prediction
```

### Phase 4: API Endpoints (Weeks 12-14)

```python
# In src/routes/analysis.py
from fastapi import APIRouter, HTTPException
from src.models import AnalysisRequest, AnalysisResult

router = APIRouter(prefix="/api")

@router.post("/analyze", response_model=AnalysisResult)
async def analyze_stock(request: AnalysisRequest):
    """Analyze a stock comprehensively."""
    result = await orchestrator.analyze_stock(request.symbol)
    return result
```

### Phase 5: Frontend (Weeks 15-18)

```python
# In frontend/app.py
import streamlit as st
import requests

st.title("InsightGenie AI")

symbol = st.text_input("Stock Symbol", "RELIANCE")

if st.button("Analyze"):
    response = requests.post(
        "http://localhost:8000/api/analyze",
        json={"symbol": symbol}
    )
    
    result = response.json()
    
    st.write(f"Prediction: ₹{result['prediction']['predicted_price']}")
    st.write(f"Confidence: {result['prediction']['confidence_score']*100}%")
    st.write(f"Risk Level: {result['prediction']['risk_level']}")
```

## Code Examples

### Creating a Custom Agent

```python
from src.agents.base import BaseAgent
from src.utils import execute_with_retry, gather_with_timeout

class MyCustomAgent(BaseAgent):
    """Custom agent for specific analysis."""
    
    def __init__(self):
        super().__init__()
        self._register_tools()
    
    def _register_tools(self):
        self.register_tool(
            "tool1",
            "Description",
            self.tool1_func,
            timeout=30
        )
    
    async def tool1_func(self, **kwargs):
        # Implementation
        return {"result": "data"}
    
    async def analyze(self, symbol: str, **kwargs):
        # Execute tools
        results = await self.execute_tools_parallel(
            ["tool1"],
            symbol=symbol
        )
        
        # Synthesize
        return {"synthesis": results}
```

### Using Genie API

```python
from src.mcp import GenieApiClient, PollingManager

client = GenieApiClient(
    api_url="https://genie-api.databricks.com/v1",
    api_key="your_key"
)

# Direct execution
result = await client.execute(
    prompt="Analyze RELIANCE stock",
    task_type="analysis",
    priority="high"
)

# Or submit and poll separately
task_id = await client.submit_task(prompt)
result = await client.poll_task(task_id)

# Using polling profiles
config = PollingManager.get_profile("fast")
result = await client.poll_task(task_id, **config)
```

### Parallel Operations

```python
from src.utils import gather_with_timeout, execute_with_retry

# Parallel with timeout
results = await gather_with_timeout(
    agent1.analyze(symbol),
    agent2.analyze(symbol),
    agent3.analyze(symbol),
    timeout=30
)

# With retry
result = await execute_with_retry(
    agent.analyze,
    max_retries=3,
    backoff_multiplier=2.0
)
```

### Caching and Rate Limiting

```python
from src.utils import AsyncCache, RateLimiter

# Cache results
cache = AsyncCache(ttl=3600)

result = await cache.get("analysis:RELIANCE")
if result is None:
    result = await perform_analysis("RELIANCE")
    await cache.set("analysis:RELIANCE", result)

# Rate limit requests
limiter = RateLimiter(rate=100, period=60)

async def rate_limited_request():
    await limiter.acquire()
    # Proceed with request
```

## Configuration

### Environment Variables

```env
# API
API_TITLE=InsightGenie AI
API_VERSION=1.0.0
ALLOWED_ORIGINS=http://localhost:3000,http://localhost:8501

# Server
SERVER_HOST=0.0.0.0
SERVER_PORT=8000

# Database
DATABASE_URL=postgresql+asyncpg://user:pass@localhost:5432/db
MONGODB_URL=mongodb://localhost:27017/db

# Cache
REDIS_URL=redis://localhost:6379
CACHE_TTL=3600

# Genie API
GENIE_API_URL=https://genie-api.databricks.com/v1
GENIE_API_KEY=your_key
GENIE_MODEL=claude-3-5-sonnet
GENIE_POLLING_INTERVAL=100
GENIE_POLLING_MAX_DELAY=5000

# Data Sources
NSE_API_URL=https://www.nseindia.com/api
BSE_API_URL=https://api.bseindia.com/api
NEWS_API_KEY=your_key

# Performance
MAX_CONCURRENT_AGENTS=3
MAX_CONCURRENT_TOOLS=10
REQUEST_TIMEOUT=300
EXECUTION_TIMEOUT=300
```

## Running the System

### Development

```bash
# Terminal 1: Backend
cd backend
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
uvicorn src.main:app --reload

# Terminal 2: Tests
cd backend
pytest --watch

# Terminal 3: Frontend (later)
cd frontend
streamlit run app.py
```

### Production with Docker

```bash
# Build and run all services
docker-compose up -d

# View logs
docker-compose logs -f backend

# Scale backend
docker-compose up -d --scale backend=3

# Shutdown
docker-compose down
```

## Testing

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=src --cov-report=html

# Run specific test
pytest tests/test_agents.py::test_tool_registration

# Watch mode
ptw
```

## Troubleshooting

### Event Loop Issues
- Ensure using `asyncio.run()` in non-async context
- Don't use `await` outside async functions
- Check for blocking operations in async code

### Import Errors
- Activate virtual environment
- Install requirements: `pip install -r requirements.txt`
- Check PYTHONPATH

### Genie API Errors
- Verify API key in `.env`
- Check API URL and network connectivity
- Monitor rate limits
- Check response queue depth

### Database Connection
- Ensure PostgreSQL/MongoDB running
- Check connection string in `.env`
- Verify database and user exist
- Check firewall rules

## Performance Optimization

1. **Parallel Execution**: Use `asyncio.gather` for multiple agents
2. **Caching**: Cache frequent queries with TTL
3. **Rate Limiting**: Prevent API overload
4. **Batch Processing**: Process items in controlled batches
5. **Connection Pooling**: Reuse database connections
6. **Response Compression**: Compress API responses

## Security Considerations

1. **API Keys**: Never commit .env files with real keys
2. **Authentication**: Implement JWT for API access
3. **Rate Limiting**: Prevent abuse
4. **Input Validation**: Validate all inputs with Pydantic
5. **HTTPS**: Use SSL/TLS in production
6. **Secrets Management**: Use proper secret management tools

## Monitoring & Logging

- Structured JSON logging to file and console
- Log rotation every 10MB
- Request tracking with unique IDs
- Performance metrics collection
- Error and exception tracking
- Health check endpoints

## Next Actions

1. **Implement Agents**: Create StockAnalyzer, GeopoliticalAnalyst, NewsAnalyst
2. **Build Orchestrator**: Coordinate parallel agent execution
3. **Add API Routes**: Create RESTful endpoints
4. **Integrate Database**: Persist results and logs
5. **Build Frontend**: Create Streamlit/Dash UI
6. **Deploy**: Docker and Kubernetes setup
7. **Monitor**: Setup dashboards and alerts

## Resources

- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [Asyncio Documentation](https://docs.python.org/3/library/asyncio.html)
- [Pydantic Documentation](https://docs.pydantic.dev/)
- [Docker Documentation](https://docs.docker.com/)

## Support

For issues or questions, refer to:
- Code comments and docstrings
- README files in each directory
- Test files for usage examples
- This implementation guide
