# API Documentation

## Endpoints

### Health & Status

#### GET /health
Liveness probe - quick health check.

**Response:**
```json
{
  "status": "ok",
  "timestamp": "2024-01-17T10:30:45.123Z"
}
```

**Status Codes:**
- `200 OK` - Service is running
- `503 Service Unavailable` - Service is down

---

#### GET /ready
Readiness probe - full system readiness check.

**Response:**
```json
{
  "status": "ready",
  "timestamp": "2024-01-17T10:30:45.123Z",
  "checks": {
    "database": "ok",
    "redis": "ok",
    "telegram": "ok"
  }
}
```

**Status Codes:**
- `200 OK` - All systems ready
- `503 Service Unavailable` - One or more systems not ready

---

#### GET /metrics
Prometheus metrics endpoint.

**Response:**
Text format Prometheus metrics

**Example:**
```
# HELP news_processed_total Total processed news
# TYPE news_processed_total counter
news_processed_total{source="ign",status="ok"} 150
```

---

#### GET /stats
Application statistics and status.

**Response:**
```json
{
  "timestamp": "2024-01-17T10:30:45.123Z",
  "queue": {
    "publication_size": 15,
    "dead_letter_size": 2
  },
  "connections": {
    "active": 5
  }
}
```

---

## Response Format

### Success Response

```json
{
  "status": "ok",
  "data": { ... },
  "timestamp": "2024-01-17T10:30:45.123Z"
}
```

### Error Response

```json
{
  "status": "error",
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Invalid input",
    "details": { ... }
  },
  "timestamp": "2024-01-17T10:30:45.123Z"
}
```

---

## Error Codes

### Client Errors (4xx)

```
400 BAD_REQUEST         - Invalid input
401 UNAUTHORIZED        - Missing/invalid token
403 FORBIDDEN           - Access denied
404 NOT_FOUND           - Resource not found
422 VALIDATION_ERROR    - Input validation failed
429 RATE_LIMITED        - Rate limit exceeded
```

### Server Errors (5xx)

```
500 INTERNAL_ERROR      - Internal server error
502 BAD_GATEWAY         - External service error
503 UNAVAILABLE         - Service unavailable
504 TIMEOUT             - Request timeout
```

---

## Rate Limiting

### Limits

- **Global**: 100 requests/minute
- **Per IP**: 60 requests/minute
- **Health checks**: Unlimited

### Rate Limit Headers

```
X-RateLimit-Limit: 60
X-RateLimit-Remaining: 45
X-RateLimit-Reset: 1705507200
```

### Exceeding Limit

```json
HTTP/1.1 429 Too Many Requests

{
  "status": "error",
  "error": {
    "code": "RATE_LIMITED",
    "message": "Rate limit exceeded",
    "retry_after": 60
  }
}
```

---

## Authentication

Currently, no authentication is required for public endpoints.

For future implementation:
- Bearer token in Authorization header
- API key in X-API-Key header
- JWT for user sessions

---

## CORS

CORS is disabled by default. Enable in settings:

```
CORS_ENABLED=true
CORS_ORIGINS=http://localhost:3000,https://example.com
```

---

## Versioning

API version: v1 (current)

Future versions will use:
- URL prefix: `/api/v2/...`
- Header: `X-API-Version: 2`

---

## Pagination

Not currently implemented. Future pagination:

```
GET /api/news?page=1&limit=20
GET /api/feeds?offset=0&limit=50
```

---

## Filtering & Sorting

Not currently implemented. Future filtering:

```
GET /api/news?source=ign&status=published&sort=-created_at
```

---

## Examples

### Check Service Health

```bash
curl -s http://localhost:8000/health | jq .
```

### Check Readiness

```bash
curl -s http://localhost:8000/ready | jq .
```

### Get Prometheus Metrics

```bash
curl http://localhost:8000/metrics | grep news_processed
```

### Get Application Stats

```bash
curl -s http://localhost:8000/stats | jq .
```

---

## Performance Characteristics

### Latency

```
/health     - < 10ms
/ready      - < 100ms
/metrics    - < 1s
/stats      - < 100ms
```

### Caching

```
/health     - Not cached
/ready      - Cached 10s
/metrics    - Not cached
/stats      - Cached 30s
```

---

## Security

### HTTPS

Production deployments use TLS/HTTPS.

### HTTPS Redirect

```
http://example.com -> https://example.com
```

### HSTS

```
Strict-Transport-Security: max-age=31536000; includeSubDomains
```

### Security Headers

```
X-Content-Type-Options: nosniff
X-Frame-Options: DENY
X-XSS-Protection: 1; mode=block
```

---

## Changelog

### v1.0 (2024-01-17)

- Initial release
- Health check endpoints
- Prometheus metrics
- Statistics endpoint

---

## Support

For issues or questions:
- GitHub Issues: https://github.com/yourusername/ultrabot/issues
- Documentation: See docs/ folder
- Slack: ultrabot-dev channel (if available)
