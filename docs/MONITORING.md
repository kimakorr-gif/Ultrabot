# Monitoring & Observability

## Prometheus Metrics

### Application Metrics

#### News Processing

```
news_processed_total{source, status}
  - Total news items processed
  - Labels: source name, status (ok/filtered/duplicate)
  
news_score_distribution
  - Distribution of calculated scores
  - Histogram buckets: [0, 2, 4, 6, 8, 10, 15, 20]

news_publication_latency_seconds
  - Time from fetch to publication
  - Buckets: [30s, 60s, 2min, 5min, 10min, 30min]
```

#### RSS Fetching

```
rss_fetch_duration_seconds{feed_name}
  - Time to fetch and parse RSS feed
  - Histogram, per-feed tracking
  
rss_fetch_errors_total{feed_name, error_type}
  - Total fetch errors
  - Track by feed and error type

rss_entries_count{feed_name}
  - Number of entries in last fetch
  - Gauge for monitoring feed activity
```

#### Translation Service

```
translation_duration_seconds{source_lang, target_lang}
  - Translation API latency
  - Histogram: [0.5s, 1s, 2s, 5s, 10s, 30s]

translation_errors_total{error_type}
  - Translation failures
  - Track API errors, timeouts, etc.

translation_cache_hits_total
  - Cache hit counter

translation_cache_misses_total
  - Cache miss counter
```

#### Publication Queue

```
publication_queue_size
  - Current items in queue
  - Alert if > 100 items

publication_queue_depth
  - Distribution of queue depths
  - Histogram: [0, 5, 10, 20, 50, 100]

dead_letter_queue_size
  - Failed publications count
  - Alert if growing
```

#### Telegram Publishing

```
telegram_publish_duration_seconds{status}
  - Publication latency
  - Histogram: [0.5s, 1s, 2s, 5s, 10s]

telegram_publish_errors_total{error_type}
  - Publication failures
  - Rate limiting, API errors, etc.
```

#### Circuit Breaker

```
circuit_breaker_state{service}
  - Current state: 0=closed, 0.5=half-open, 1=open
  - Alert if OPEN for > 5 minutes

circuit_breaker_errors_total{service}
  - Errors triggering circuit breaker
```

#### Database

```
database_query_duration_seconds{query_type}
  - Query execution time
  - Buckets: [10ms, 50ms, 100ms, 500ms, 1s, 5s]

database_errors_total{error_type}
  - Database errors
```

---

## Alert Rules

### Critical Alerts

```yaml
# Pod restart rate
- alert: PodRestartingFrequently
  expr: rate(kube_pod_container_status_restarts_total[15m]) > 0.1
  for: 5m
  action: Page on-call

# High error rate
- alert: HighErrorRate
  expr: rate(api_errors_total[5m]) > 0.01
  for: 5m
  action: Page on-call

# Circuit breaker open
- alert: CircuitBreakerOpen
  expr: circuit_breaker_state > 0.9
  for: 5m
  action: Page on-call
```

### Warning Alerts

```yaml
# Queue backlog
- alert: PublicationQueueBacklog
  expr: publication_queue_size > 100
  for: 10m
  action: Create ticket

# High latency
- alert: HighPublicationLatency
  expr: histogram_quantile(0.95, publication_queue_depth) > 1800
  for: 10m
  action: Create ticket

# Cache hit ratio low
- alert: LowCacheHitRatio
  expr: cache_hit_ratio < 0.5
  for: 15m
  action: Create ticket
```

---

## Grafana Dashboards

### Dashboard 1: Overview

```
Row 1: Key Metrics
  - Total news processed (24h)
  - Publication success rate
  - Average publication latency
  - Queue size (current)

Row 2: Trends
  - News processed over time
  - Error rate trend
  - Latency percentiles (p50, p95, p99)

Row 3: System Health
  - Pod restarts
  - CPU usage
  - Memory usage
  - Network I/O
```

### Dashboard 2: RSS Feeds

```
Row 1: Feed Performance
  - Entries per feed (heatmap)
  - Fetch duration by feed
  - Error rate by feed

Row 2: Per-Feed Details
  - Table: Feed name, last fetch, entries, errors
```

### Dashboard 3: Translation & Content

```
Row 1: Translation Metrics
  - Cache hit ratio
  - Average translation time
  - Error rate

Row 2: Content Analysis
  - Average score distribution
  - Top performing keywords
  - Language statistics
```

### Dashboard 4: Publication & Queue

```
Row 1: Publication Metrics
  - Messages published (24h)
  - Telegram publish latency
  - Error types

Row 2: Queue Management
  - Queue depth over time
  - Dead letter queue size
  - Retry attempts
```

---

## Structured Logging

### Log Format

All logs are in JSON format:

```json
{
  "timestamp": "2024-01-17T10:30:45.123Z",
  "level": "INFO",
  "logger": "application.use_cases.process_feeds",
  "message": "Feed processed successfully",
  "correlation_id": "uuid-xxx",
  "context": {
    "feed_name": "ign.com",
    "news_count": 15,
    "duration_ms": 2340,
    "score_distribution": {"high": 5, "medium": 7, "low": 3}
  }
}
```

### Log Levels

- **DEBUG**: Development debugging
- **INFO**: Normal operations
- **WARNING**: Potential issues
- **ERROR**: Failures requiring attention
- **CRITICAL**: System failures

### Structured Fields

```
timestamp       - ISO 8601 format
level           - Log level
logger          - Logger name
message         - Human-readable message
correlation_id  - Request tracking ID
context         - Additional structured data
exception       - Stack trace (if error)
```

---

## Health Checks

### Liveness Probe

```bash
GET /health
Response: 200 OK
{
  "status": "ok",
  "timestamp": "2024-01-17T10:30:45.123Z"
}
```

### Readiness Probe

```bash
GET /ready
Response: 200 OK
{
  "status": "ready",
  "checks": {
    "database": "ok",
    "redis": "ok",
    "telegram": "ok"
  }
}
```

### Statistics Endpoint

```bash
GET /stats
Response: 200 OK
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

## Performance Baselines

### Expected Metrics

```
RSS Fetch:        5-15 seconds per feed
Translation:      1-5 seconds per text
Publication:      1-3 seconds per message
Database Query:   50-500ms
Cache Hit Ratio:  > 80% after warmup
News Score:       Average 6-8 points
Queue Depth:      < 10 items normally
```

### SLA Targets

```
Uptime:                     99.9%
News Publication Success:   > 95%
Max Queue Delay:            < 2 hours
RTO (Recovery):             < 5 minutes
RPO (Data):                 < 1 item
```

---

## Data Retention

### Metrics
- Raw metrics: 15 days
- Aggregated: 1 year
- Retention: Configurable in Prometheus

### Logs
- Application logs: 30 days
- Audit logs: 90 days
- Archive to S3: Optional

### Database
- News items: 7 days (auto-cleanup)
- Publications: 30 days
- Metrics logs: 60 days

---

## Troubleshooting Metrics

### High Error Rate

```
Check:
1. Recent deployments
2. External API status
3. Database connectivity
4. Redis availability

Prometheus Query:
rate(api_errors_total[5m]) > 0.01
```

### Queue Backlog

```
Check:
1. Publication latency
2. Telegram API rate limiting
3. Network connectivity

Prometheus Query:
publication_queue_size > 100
```

### Low Cache Hit Ratio

```
Check:
1. Cache expiration settings
2. Redis memory pressure
3. Query patterns

Prometheus Query:
rate(translation_cache_misses_total[5m]) / 
(rate(translation_cache_hits_total[5m]) + 
 rate(translation_cache_misses_total[5m]))
```

---

## Tools & Integrations

### Recommended Tools
- **Metrics**: Prometheus + Grafana
- **Logs**: ELK Stack / Loki
- **Tracing**: Jaeger (optional)
- **Alerting**: AlertManager / PagerDuty
- **Dashboards**: Grafana

### Export Options
- S3 for backup
- CloudWatch for AWS
- Stackdriver for GCP
- Azure Monitor for Azure
