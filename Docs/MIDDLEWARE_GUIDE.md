# Middleware Layer Guide

## Overview

The middleware layer serves as an API gateway between the Streamlit frontend and FastAPI backend.

**Key Responsibilities**:
- Request validation and transformation
- Authentication (JWT)
- Rate limiting
- Response caching
- Error handling
- Request logging

---

## Getting Started

### Installation

```bash
cd middleware
pip install -r requirements.txt
```

### Configuration

Create `.env` file from example:
```bash
cp .env.example .env
```

Edit `.env` with your settings:
```
BACKEND_URL=http://localhost:8000
MIDDLEWARE_PORT=8001
JWT_SECRET_KEY=your-secret-key-here
REDIS_URL=redis://localhost:6379/0
```

### Run Middleware

**Development**:
```bash
python -m uvicorn src.middleware:create_middleware_app --reload --port 8001
```

**Production**:
```bash
uvicorn src.middleware:create_middleware_app --host 0.0.0.0 --port 8001 --workers 4
```

---

## Architecture

### Module Breakdown

#### 1. middleware.py
Main FastAPI application with all endpoints.

**Key Functions**:
- `create_middleware_app()` - Creates FastAPI app with all middleware
- `get_client()` - Gets async HTTP client for backend communication

**Endpoints**:
```
POST   /api/analyze              - Submit analysis
GET    /api/analyze/{id}         - Get status
POST   /api/batch-analyze        - Batch analysis
GET    /api/data/{layer}/{symbol} - Data layer access
GET    /health                   - Health check
```

#### 2. auth.py
JWT token management and authentication.

**Key Classes**:
- `JWTManager` - Creates and verifies tokens
- `get_current_user()` - FastAPI dependency

**Usage**:
```python
# Create token
token = create_token({"sub": "user_id", "role": "admin"})

# Use in endpoint
@app.get("/protected")
async def protected(user = Depends(get_current_user)):
    return {"user": user}
```

#### 3. cache.py
Redis-based caching layer.

**Key Class**: `CacheManager`

**Methods**:
- `get(key)` - Retrieve from cache
- `set(key, value, ttl)` - Store in cache
- `delete(key)` - Remove from cache
- `exists(key)` - Check existence
- `clear_pattern(pattern)` - Clear matching keys

**Usage**:
```python
cache = get_cache_manager()
cache.set("stock:RELIANCE", data, ttl=600)
cached = cache.get("stock:RELIANCE")
```

#### 4. config.py
Configuration management using Pydantic.

**Environment Variables**:
```
BACKEND_URL         - Backend API URL
MIDDLEWARE_PORT     - Middleware port
REDIS_URL          - Redis connection URL
JWT_SECRET_KEY     - JWT signing key
LOG_LEVEL          - Logging level
CACHE_TTL          - Default cache TTL
RATE_LIMIT_REQUESTS - Requests per window
```

#### 5. validators.py
Request validation models.

**Models**:
- `AnalysisRequest` - Single stock analysis
- `BatchAnalysisRequest` - Multiple stocks
- `PortfolioRequest` - Portfolio analysis
- `DataLayerRequest` - Data layer query

**Validation Features**:
- Symbol validation (uppercase, trim)
- Weight normalization (must sum to 1.0)
- Enum validation for analysis types
- Min/max constraints

#### 6. models.py
Response models.

**Key Models**:
- `APIResponse` - Standard success response
- `ErrorResponse` - Error response
- `JobStatus` - Job status tracking
- `HealthCheck` - Health check response

---

## Request Flow

### Analysis Request

```
1. Client sends POST /api/analyze
   {
     "symbol": "RELIANCE",
     "analysis_type": "comprehensive"
   }

2. Middleware validates request
   - Check symbol format
   - Validate analysis_type enum
   - Generate request_id

3. Check cache for recent analysis
   - Key: "analysis:RELIANCE:comprehensive"
   - If found, return cached result

4. Forward to backend
   - POST /api/analyze
   - Include request_id header

5. Receive response from backend

6. Cache result (10 min TTL)

7. Return to client
   {
     "success": true,
     "message": "Analysis completed",
     "data": {...},
     "request_id": "..."
   }
```

---

## Authentication

### Create User Token

```bash
# Generate JWT token
curl -X POST http://localhost:8001/auth/token \
  -d "username=user&password=pass"
```

### Use Token

```bash
# Include in Authorization header
curl -H "Authorization: Bearer <token>" \
  http://localhost:8001/api/analyze
```

### Token Structure

```python
{
  "sub": "user_id",           # Subject (user)
  "exp": 1234567890,          # Expiration
  "iat": 1234567800,          # Issued at
  "role": "user"              # Optional role
}
```

---

## Caching Strategy

### Cache Keys

```
analysis:{SYMBOL}:{TYPE}     - Analysis result
data:{LAYER}:{SYMBOL}        - Data layer
status:{REQUEST_ID}          - Job status
health:backend               - Backend status
```

### TTL Configuration

```
Bronze layer data:  5 min
Silver layer data: 10 min
Gold layer data:   30 min
Analysis result:   10 min
Health check:       1 min
```

### Cache Management

**View Cache**:
```bash
redis-cli KEYS "analysis:*"
redis-cli TTL "analysis:RELIANCE:comprehensive"
```

**Clear Cache**:
```python
cache.clear_pattern("analysis:*")
cache.delete("analysis:RELIANCE:comprehensive")
```

---

## Rate Limiting

### Configuration

```
# .env
RATE_LIMIT_ENABLED=true
RATE_LIMIT_REQUESTS=100
RATE_LIMIT_WINDOW=60
```

### Limits Per IP

- 100 requests per 60 seconds
- Returns `429 Too Many Requests` when exceeded

### Monitoring Rate Limits

```bash
redis-cli KEYS "rate_limit:*"
redis-cli TTL "rate_limit:192.168.1.1"
```

---

## Error Handling

### Status Codes

```
200 OK                    - Successful request
400 Bad Request           - Validation error
401 Unauthorized          - Auth required
429 Too Many Requests     - Rate limit exceeded
500 Internal Server Error - Server error
503 Service Unavailable   - Service down
```

### Error Response Format

```json
{
  "success": false,
  "message": "Request failed",
  "error": "Invalid symbol INVALID",
  "details": {
    "field": "symbol",
    "issue": "Min length is 1"
  }
}
```

---

## Logging

### Log Format

```
[REQUEST_ID] METHOD PATH - STATUS_CODE - PROCESS_TIME
```

### Example

```
[550e8400-e29b-41d4-a716-446655440000] POST /api/analyze - 200 - 0.345s
```

### Log Levels

```
DEBUG   - Detailed diagnostic info
INFO    - General informational messages
WARNING - Warning messages
ERROR   - Error messages
CRITICAL - Critical failures
```

### Log File

Logs written to `logs/middleware.log`

---

## Health Checks

### Endpoint

```bash
curl http://localhost:8001/health
```

### Response

```json
{
  "status": "healthy",
  "version": "1.0.0",
  "timestamp": "2026-04-06T10:00:00Z",
  "services": {
    "backend": "healthy",
    "cache": "healthy"
  }
}
```

### Monitoring

```bash
# Kubernetes liveness probe
curl -f http://localhost:8001/health || exit 1

# Docker healthcheck
HEALTHCHECK CMD curl -f http://localhost:8001/health || exit 1
```

---

## Development Tips

### Debug Mode

Enable debug logging:
```python
# In config.py
debug = True
log_level = "DEBUG"
```

### Testing Endpoints

```bash
# Health check
curl http://localhost:8001/health

# Analysis with cache
curl -X POST http://localhost:8001/api/analyze \
  -H "Content-Type: application/json" \
  -d '{"symbol":"RELIANCE","analysis_type":"quick"}'

# Batch analysis
curl -X POST http://localhost:8001/api/batch-analyze \
  -H "Content-Type: application/json" \
  -d '{"symbols":["RELIANCE","TCS"],"analysis_type":"quick"}'
```

### Performance Testing

```bash
# Simple load test
for i in {1..100}; do
  curl -X POST http://localhost:8001/api/analyze \
    -H "Content-Type: application/json" \
    -d '{"symbol":"RELIANCE","analysis_type":"quick"}' &
done
wait
```

---

## Deployment

### Docker

```bash
docker build -f docker/Dockerfile.middleware -t insightgenie-middleware .
docker run -p 8001:8001 insightgenie-middleware
```

### Docker Compose

```bash
docker-compose up middleware
```

### Kubernetes

```bash
kubectl apply -f k8s/middleware-deployment.yaml
```

---

## Troubleshooting

### Backend Connection Error

```
Error: Cannot connect to backend at http://localhost:8000

Solution:
1. Check backend is running
2. Verify BACKEND_URL in .env
3. Check network connectivity
```

### Cache Not Working

```
Error: Cache operations failing

Solution:
1. Check Redis is running
2. Verify REDIS_URL in .env
3. Test with: redis-cli ping
```

### Rate Limit Issues

```
Error: 429 Too Many Requests

Solution:
1. Wait for window to reset (60 sec)
2. Increase RATE_LIMIT_REQUESTS if needed
3. Use Redis to clear limits: redis-cli FLUSHDB
```

### JWT Token Expired

```
Error: Token expired

Solution:
1. Request new token
2. Check JWT_EXPIRATION (default: 1 hour)
3. Implement refresh token flow
```

---

## Next Steps

1. **Add Authentication Endpoint**
   - Implement `/auth/token` for user login
   - Support refresh tokens
   - Role-based access control

2. **Advanced Caching**
   - Cache invalidation triggers
   - Cache warming strategies
   - Analytics on cache efficiency

3. **Rate Limiting Enhancements**
   - Per-user limits
   - Per-endpoint limits
   - Whitelist/blacklist support

4. **Monitoring & Alerting**
   - Prometheus metrics
   - Custom health checks
   - Alert on failures

5. **API Versioning**
   - Support multiple API versions
   - Backward compatibility
   - Version deprecation strategy
