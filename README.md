# InsightGenie AI - Stock Market Prediction System

An advanced AI-powered stock market prediction system built with Python, FastAPI, and intelligent agents.

## Features

- **Intelligent Agents**: BaseAgent abstraction with Stock Analyzer and Price Predictor agents
- **Async Architecture**: Built on asyncio and aiohttp for high-performance async operations
- **FastAPI Backend**: Modern REST API with automatic documentation
- **Data Models**: Type-safe Pydantic models for all data structures
- **Error Handling**: Comprehensive custom exception framework
- **Logging**: Structured JSON logging with rotation
- **Genie API Integration**: Async client with polling support
- **Caching**: In-memory and Redis caching layers
- **Task Queue**: Async task queue for background jobs
- **Docker Support**: Complete Docker and Docker-Compose setup
- **CI/CD**: GitHub Actions pipeline with testing and deployment
- **Testing**: Comprehensive unit test suite with pytest

## Project Structure

```
InsightGenieAI/
├── backend/
│   ├── app/
│   │   ├── agents/              # Agent implementations
│   │   │   ├── base_agent.py   # Abstract base class
│   │   │   ├── stock_analyzer.py
│   │   │   └── predictor_agent.py
│   │   ├── models/              # Pydantic data models
│   │   │   ├── base.py
│   │   │   ├── stock.py
│   │   │   ├── agent.py
│   │   │   └── api.py
│   │   ├── api/                 # FastAPI routes
│   │   │   └── v1/
│   │   │       └── endpoints/
│   │   ├── middleware/          # FastAPI middleware
│   │   │   ├── cors_middleware.py
│   │   │   ├── error_handler.py
│   │   │   ├── request_logger.py
│   │   │   └── auth_middleware.py
│   │   ├── services/            # Business logic services
│   │   │   ├── genie_api_client.py
│   │   │   ├── cache_service.py
│   │   │   └── task_queue.py
│   │   ├── config/              # Configuration
│   │   │   └── settings.py
│   │   ├── utils/               # Utility modules
│   │   │   ├── logger.py
│   │   │   ├── exceptions.py
│   │   │   └── async_utils.py
│   │   └── main.py              # FastAPI application
│   ├── tests/                   # Test suite
│   │   ├── unit/
│   │   └── integration/
│   ├── requirements.txt
│   └── .env.example
├── docker/
│   └── Dockerfile
├── .github/
│   └── workflows/
│       └── ci-cd.yml
└── docker-compose.yml

```

## Getting Started

### Prerequisites

- Python 3.12+
- Docker and Docker-Compose
- PostgreSQL 16
- MongoDB 7.0
- Redis 7.0

### Local Development Setup

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd InsightGenieAI
   ```

2. **Create virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   cd backend
   pip install -r requirements.txt
   ```

4. **Setup environment**
   ```bash
   cp .env.example .env
   # Edit .env with your configuration
   ```

5. **Run application**
   ```bash
   uvicorn app.main:app --reload
   ```

The API will be available at `http://localhost:8000` with documentation at `http://localhost:8000/docs`.

### Docker Setup

1. **Build and run with Docker-Compose**
   ```bash
   docker-compose up -d
   ```

2. **Check services**
   ```bash
   docker-compose ps
   ```

3. **View logs**
   ```bash
   docker-compose logs -f backend
   ```

## API Endpoints

### Health Check
- `GET /health/check` - Health status
- `GET /health/status` - Detailed status

### Stocks
- `GET /api/v1/stocks/data/{symbol}` - Get market data
- `GET /api/v1/stocks/analyze/{symbol}` - Analyze stock

### Agents
- `GET /api/v1/agents/` - List available agents
- `POST /api/v1/agents/task` - Submit agent task

### Predictions
- `POST /api/v1/predictions/predict/{symbol}` - Predict price

## Configuration

Configuration is managed through environment variables. See `.env.example` for all available options.

### Key Settings

```env
# Application
ENVIRONMENT=development
DEBUG=false

# Database
DATABASE_URL=postgresql+asyncpg://user:pass@localhost/db
MONGODB_URL=mongodb://user:pass@localhost/db

# Cache
REDIS_URL=redis://localhost:6379/0

# Genie API
GENIE_API_KEY=your-api-key
GENIE_API_BASE_URL=https://api.genie.com

# Logging
LOG_LEVEL=INFO
LOG_FORMAT=json
```

## Testing

### Run all tests
```bash
pytest tests/ -v
```

### Run with coverage
```bash
pytest tests/ --cov=app --cov-report=html
```

### Run specific test file
```bash
pytest tests/unit/test_agents.py -v
```

## Agent Usage Examples

### Stock Analyzer Agent

```python
from app.agents import StockAnalyzerAgent
from app.models.agent import AgentConfig, AgentTask
import asyncio

async def analyze_stock():
    config = AgentConfig(
        name="analyzer",
        description="Stock Analyzer",
        agent_type="stock_analyzer"
    )
    agent = StockAnalyzerAgent(config)
    
    task = AgentTask(
        task_id="task-1",
        agent_name="analyzer",
        task_type="analyze",
        input_data={"symbol": "AAPL"}
    )
    
    result = await agent.execute_task(task)
    print(result)

asyncio.run(analyze_stock())
```

### Price Predictor Agent

```python
from app.agents import PredictorAgent
from app.models.agent import AgentConfig, AgentTask
import asyncio

async def predict_price():
    config = AgentConfig(
        name="predictor",
        description="Price Predictor",
        agent_type="predictor"
    )
    agent = PredictorAgent(config)
    
    task = AgentTask(
        task_id="task-2",
        agent_name="predictor",
        task_type="predict",
        input_data={"symbol": "AAPL", "days_ahead": 7}
    )
    
    result = await agent.execute_task(task)
    print(result)

asyncio.run(predict_price())
```

## Async Utilities

The framework provides several async utilities for common patterns:

```python
from app.utils.async_utils import (
    gather_with_timeout,
    execute_with_retry,
    AsyncBatchProcessor
)

# Gather with timeout
results = await gather_with_timeout(coro1, coro2, timeout=30)

# Retry with exponential backoff
result = await execute_with_retry(async_func, max_retries=3)

# Batch processing
processor = AsyncBatchProcessor(batch_size=10, max_concurrent=5)
await processor.process(items, async_processor)
```

## Genie API Integration

```python
from app.services import GenieAPIClient

async with GenieAPIClient() as client:
    # Submit prediction task
    task_id = await client.submit_prediction_task("AAPL", analysis_data)
    
    # Poll for result
    result = await client.poll_prediction_result(task_id)
    
    # Or submit and poll in one call
    result = await client.submit_and_poll("AAPL", analysis_data)
```

## CI/CD Pipeline

The project includes a comprehensive GitHub Actions pipeline that:

1. **Tests** - Runs unit tests with coverage
2. **Code Quality** - Linting, type checking, formatting
3. **Security** - Vulnerability scanning with Trivy
4. **Build** - Docker image build and push
5. **Deploy** - Deployment to dev/prod environments

## Production Deployment

### Environment Setup
1. Update `.env` with production credentials
2. Set `ENVIRONMENT=production`
3. Update `SECRET_KEY` and other security settings
4. Configure database connections
5. Set up monitoring and logging

### Running in Production
```bash
# Using Docker-Compose
docker-compose -f docker-compose.yml up -d

# Using Kubernetes (configure as needed)
kubectl apply -f k8s/
```

## Monitoring & Logging

- **Structured Logging**: All logs are JSON formatted for easy parsing
- **Request Tracking**: Each request gets a unique request ID
- **Error Tracking**: Integration with Sentry (optional)
- **Performance Monitoring**: Built-in async operation timing

## Contributing

1. Create feature branch
2. Make changes
3. Write tests
4. Run tests locally
5. Submit pull request

## License

MIT License - see LICENSE file for details

## Support

For issues and questions, please create an issue in the repository.
