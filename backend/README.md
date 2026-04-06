"""README for InsightGenie AI Backend."""

# InsightGenie AI Backend

Real-time Indian stock market prediction system with geopolitical analysis.

## Features

- **Async/Await Architecture**: Non-blocking I/O throughout
- **Multi-Agent System**: Stock, Geopolitical, and News analysts
- **Parallel Execution**: Tools and agents run concurrently
- **Genie API Integration**: With intelligent polling and retry logic
- **Comprehensive Logging**: Structured JSON logging
- **Type Safety**: Full type hints with Pydantic validation

## Project Structure

```
backend/
├── src/
│   ├── agents/           # Agent implementations
│   ├── models/           # Pydantic data models
│   ├── mcp/              # Genie API client
│   ├── prompts/          # System prompts
│   ├── config/           # Configuration management
│   ├── utils/            # Async helpers and utilities
│   └── main.py           # FastAPI application
├── requirements.txt      # Python dependencies
├── .env.example          # Environment variables template
└── Dockerfile           # Docker configuration
```

## Quick Start

### 1. Setup Environment

```bash
cd backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Setup environment
cp .env.example .env
# Edit .env with your configuration
```

### 2. Run Application

```bash
# Development with hot reload
uvicorn src.main:app --reload

# Production
uvicorn src.main:app --host 0.0.0.0 --port 8000 --workers 4
```

### 3. API Documentation

Visit `http://localhost:8000/docs` for interactive Swagger documentation.

## Docker

```bash
# Build image
docker build -t insight-genie-backend .

# Run container
docker run -p 8000:8000 -e GENIE_API_KEY=your_key insight-genie-backend

# With docker-compose (from root directory)
docker-compose up backend
```

## Key Components

### BaseAgent

Abstract agent class providing:
- Tool registration and execution
- Parallel tool execution
- Execution history tracking
- Error handling

```python
from src.agents.base import BaseAgent

class MyAgent(BaseAgent):
    async def analyze(self, **kwargs):
        results = await self.execute_tools_parallel(
            ["tool1", "tool2", "tool3"],
            **kwargs
        )
        return results
```

### GenieApiClient

Async client for Genie API with:
- Task submission
- Intelligent polling with exponential backoff
- Request caching
- Priority queue support

```python
from src.mcp import GenieApiClient

client = GenieApiClient(
    api_url="https://genie-api.databricks.com/v1",
    api_key="your_key"
)

result = await client.execute(prompt="Analyze this...")
```

### Async Utilities

```python
from src.utils import (
    execute_with_timeout,
    execute_with_retry,
    gather_with_timeout,
    RateLimiter,
    AsyncCache,
)

# With timeout
result = await execute_with_timeout(coro, timeout=30)

# With retry
result = await execute_with_retry(
    coro_func,
    max_retries=3,
    backoff_multiplier=2.0
)

# Parallel with timeout
results = await gather_with_timeout(coro1, coro2, coro3, timeout=60)

# Rate limiting
limiter = RateLimiter(rate=100, period=60)
await limiter.acquire()

# Caching
cache = AsyncCache(ttl=3600)
await cache.set("key", "value")
value = await cache.get("key")
```

## Configuration

Environment variables in `.env`:

```env
# API
API_TITLE=InsightGenie AI
SERVER_PORT=8000

# Genie API
GENIE_API_URL=https://genie-api.databricks.com/v1
GENIE_API_KEY=your_key
GENIE_MODEL=claude-3-5-sonnet

# Database
DATABASE_URL=postgresql+asyncpg://user:pass@localhost/db
MONGODB_URL=mongodb://localhost:27017/db

# Redis
REDIS_URL=redis://localhost:6379

# Performance
MAX_CONCURRENT_AGENTS=3
MAX_CONCURRENT_TOOLS=10
REQUEST_TIMEOUT=300
```

## API Endpoints

- `GET /` - Root endpoint
- `GET /health` - Health check
- `POST /api/analyze` - Analyze a stock
- `GET /api/status/{request_id}` - Check analysis status

## Error Handling

All exceptions are properly handled and return consistent error responses:

```json
{
  "success": false,
  "error": "Error message",
  "error_code": "ERROR_CODE",
  "details": {}
}
```

## Logging

Logs are written to both console and file (`logs/app.log`) in JSON format:

```json
{
  "timestamp": "2024-01-15T10:30:00.000Z",
  "level": "INFO",
  "logger": "src.agents.stock_analyzer",
  "message": "Analysis completed",
  "module": "stock_analyzer",
  "function": "analyze",
  "line": 42
}
```

## Testing

```bash
# Run tests
pytest

# With coverage
pytest --cov=src

# Watch mode
ptw
```

## Performance

- Parallel agent execution: ~5-10 seconds total
- Individual tool execution: <1-2 seconds each
- Genie API polling: Adaptive with exponential backoff
- Caching: 1-hour TTL for identical requests

## Troubleshooting

### Import Errors

If you get import errors, ensure:
1. Virtual environment is activated
2. Dependencies are installed: `pip install -r requirements.txt`
3. PYTHONPATH is set correctly

### Genie API Errors

Check:
1. API key is valid in `.env`
2. API URL is correct
3. Network connectivity is available
4. Rate limits are not exceeded

### Async Issues

Common issues:
- Using `await` without async context
- Blocking operations in async functions
- Event loop conflicts

## Contributing

1. Create feature branch
2. Add tests for new code
3. Run `pytest` and ensure all pass
4. Submit pull request

## License

MIT
