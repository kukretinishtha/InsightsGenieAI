# InsightGenie AI - Quick Reference Guide

## 🚀 Start Here

### 1. First Time Setup

```bash
cd backend
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
```

### 2. Run Application

```bash
# Local development
uvicorn app.main:app --reload

# With Docker
docker-compose up -d

# API Docs: http://localhost:8000/docs
```

### 3. Run Tests

```bash
# All tests
pytest tests/ -v

# With coverage
pytest tests/ --cov=app --cov-report=html
```

## 📚 Key Files Reference

| File | Purpose |
|------|---------|
| `app/main.py` | FastAPI application entry |
| `app/agents/base_agent.py` | Agent abstract class |
| `app/models/` | Pydantic data models |
| `app/services/genie_api_client.py` | Genie API integration |
| `app/middleware/` | Request/response middleware |
| `app/utils/async_utils.py` | Async utilities |
| `requirements.txt` | Python dependencies |
| `docker-compose.yml` | Multi-service orchestration |

## 🔌 Common API Calls

```bash
# Health check
curl http://localhost:8000/health/check

# Get stock data
curl http://localhost:8000/api/v1/stocks/data/AAPL

# Analyze stock
curl http://localhost:8000/api/v1/stocks/analyze/AAPL

# List agents
curl http://localhost:8000/api/v1/agents/

# Predict price
curl -X POST http://localhost:8000/api/v1/predictions/predict/AAPL
```

## 🔧 Using Agents

```python
from app.agents import StockAnalyzerAgent
from app.models.agent import AgentConfig, AgentTask
import asyncio

async def main():
    config = AgentConfig(
        name="my_analyzer",
        description="Analyze stocks",
        agent_type="stock_analyzer"
    )
    agent = StockAnalyzerAgent(config)
    
    task = AgentTask(
        task_id="task-1",
        agent_name="my_analyzer",
        task_type="analyze",
        input_data={"symbol": "AAPL"}
    )
    
    result = await agent.execute_task(task)
    return result

result = asyncio.run(main())
```

## 🏗️ Architecture Overview

```
Request
  ↓
Middleware (CORS, Logging, Auth)
  ↓
Route Handler (FastAPI)
  ↓
Agent Execution (BaseAgent subclass)
  ↓
Service Layer (Cache, API, Queue)
  ↓
Data Model (Pydantic)
  ↓
Response (APIResponse wrapper)
```

## 📊 Configuration Quick Reference

Key environment variables:

```env
# Core
ENVIRONMENT=development     # development|production
DEBUG=false                 # Enable debug mode

# Server
HOST=0.0.0.0              # Server host
PORT=8000                 # Server port

# Database
DATABASE_URL=postgresql+asyncpg://...  # PostgreSQL
MONGODB_URL=mongodb://...              # MongoDB

# Cache
REDIS_URL=redis://localhost:6379/0    # Redis

# Genie API
GENIE_API_KEY=your-key
GENIE_API_BASE_URL=https://api.genie.com

# Logging
LOG_LEVEL=INFO            # DEBUG|INFO|WARNING|ERROR
LOG_FORMAT=json           # json|text
```

## 🧪 Testing Quick Reference

```bash
# Run specific test
pytest tests/unit/test_agents.py::test_stock_analyzer_agent_initialization

# Run with markers
pytest -m asyncio               # Only async tests
pytest -m "not asyncio"         # Skip async tests

# Debug mode
pytest tests/ -v -s             # Show print statements

# Generate coverage report
pytest tests/ --cov=app --cov-report=html
# Open htmlcov/index.html in browser
```

## 🐛 Troubleshooting

### Issue: `ModuleNotFoundError: No module named 'app'`
**Solution**: Make sure you're in the `backend` directory and Python path is correct.

### Issue: Database connection error
**Solution**: Check `DATABASE_URL` in `.env` and ensure PostgreSQL is running.

### Issue: Redis connection error
**Solution**: Start Redis with `docker-compose up redis` or check Redis configuration.

### Issue: Tests fail
**Solution**: Run `pytest tests/ -v` to see detailed error messages.

## 📈 Performance Tips

1. **Use async functions** - Leverage `async`/`await` for I/O operations
2. **Cache results** - Use `CacheService` for frequently accessed data
3. **Batch processing** - Use `AsyncBatchProcessor` for bulk operations
4. **Monitor logs** - Check `logs/app.log` for performance issues

## 🔒 Security Checklist

- [ ] Update `SECRET_KEY` in production
- [ ] Set `ENVIRONMENT=production`
- [ ] Configure HTTPS
- [ ] Set up proper database credentials
- [ ] Enable authentication middleware
- [ ] Configure CORS origins
- [ ] Set up error monitoring (Sentry)
- [ ] Run security scanning

## 📚 Documentation References

- [FastAPI Docs](https://fastapi.tiangolo.com)
- [Pydantic Docs](https://docs.pydantic.dev)
- [AsyncIO Docs](https://docs.python.org/3/library/asyncio.html)
- [Pytest Docs](https://docs.pytest.org)
- [Docker Docs](https://docs.docker.com)

## 💡 Common Patterns

### Error Handling

```python
from app.utils.exceptions import ValidationError

try:
    if not symbol:
        raise ValidationError("Symbol required")
except ValidationError as e:
    logger.error(f"Validation failed: {e.message}")
    return {"error": e.message}
```

### Async Retry

```python
from app.utils.async_utils import execute_with_retry

result = await execute_with_retry(
    async_function,
    max_retries=3,
    initial_delay=1.0
)
```

### Caching

```python
from app.services import CacheService

cache = CacheService()
result = await cache.get_or_set(
    key="stock_AAPL",
    fetch_func=fetch_stock_data,
    symbol="AAPL"
)
```

## 📞 Getting Help

1. Check the [README.md](README.md) for detailed documentation
2. Review [IMPLEMENTATION_SUMMARY.md](IMPLEMENTATION_SUMMARY.md) for architecture
3. Look at test files in `tests/` for usage examples
4. Check docstrings in source code (`app/`)

## 🚀 Next Steps

1. **Customize agents** - Add your own agent implementations
2. **Integrate databases** - Set up PostgreSQL and MongoDB connections
3. **Add authentication** - Implement JWT or OAuth
4. **Configure monitoring** - Set up Sentry and log aggregation
5. **Deploy** - Use Docker-Compose or Kubernetes
6. **Optimize** - Profile and optimize for production

---

**Happy Coding! 🎉**
