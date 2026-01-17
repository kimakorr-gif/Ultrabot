"""Prometheus metrics for monitoring."""

from prometheus_client import Counter, Gauge, Histogram


# News processing metrics
NEWS_PROCESSED_TOTAL = Counter(
    "news_processed_total",
    "Total number of news items processed",
    ["source", "status"],  # status: ok, filtered, duplicate
)

NEWS_SCORE_DISTRIBUTION = Histogram(
    "news_score_distribution",
    "Distribution of news scores",
    buckets=(0, 2, 4, 6, 8, 10, 15, 20),
)

NEWS_PUBLICATION_LATENCY = Histogram(
    "news_publication_latency_seconds",
    "Latency from fetch to publication",
    buckets=(30, 60, 120, 300, 600, 900, 1800),
)

# RSS fetching metrics
RSS_FETCH_DURATION = Histogram(
    "rss_fetch_duration_seconds",
    "Time to fetch and parse RSS feed",
    ["feed_name"],
    buckets=(1, 2, 5, 10, 30),
)

RSS_FETCH_ERRORS = Counter(
    "rss_fetch_errors_total",
    "Total RSS fetch errors",
    ["feed_name", "error_type"],
)

RSS_ENTRIES_COUNT = Gauge(
    "rss_entries_count",
    "Number of entries in last fetch",
    ["feed_name"],
)

# Translation metrics
TRANSLATION_DURATION = Histogram(
    "translation_duration_seconds",
    "Time to translate content",
    ["source_lang", "target_lang"],
    buckets=(0.5, 1, 2, 5, 10, 30),
)

TRANSLATION_ERRORS = Counter(
    "translation_errors_total",
    "Total translation API errors",
    ["error_type"],
)

TRANSLATION_CACHE_HITS = Counter(
    "translation_cache_hits_total",
    "Translation cache hits",
)

TRANSLATION_CACHE_MISSES = Counter(
    "translation_cache_misses_total",
    "Translation cache misses",
)

# Publication metrics
TELEGRAM_PUBLISH_DURATION = Histogram(
    "telegram_publish_duration_seconds",
    "Time to publish to Telegram",
    buckets=(0.5, 1, 2, 5, 10),
)

TELEGRAM_PUBLISH_ERRORS = Counter(
    "telegram_publish_errors_total",
    "Total Telegram publication errors",
    ["error_type"],
)

PUBLICATION_QUEUE_SIZE = Gauge(
    "publication_queue_size",
    "Current size of publication queue",
)

PUBLICATION_QUEUE_DEPTH = Histogram(
    "publication_queue_depth",
    "Depth of items in publication queue",
    buckets=(0, 5, 10, 20, 50, 100),
)

DEAD_LETTER_QUEUE_SIZE = Gauge(
    "dead_letter_queue_size",
    "Current size of dead letter queue",
)

# Database metrics
DATABASE_QUERY_DURATION = Histogram(
    "database_query_duration_seconds",
    "Database query execution time",
    ["query_type"],  # select, insert, update, delete
    buckets=(0.01, 0.05, 0.1, 0.5, 1, 5),
)

DATABASE_ERRORS = Counter(
    "database_errors_total",
    "Total database errors",
    ["error_type"],
)

# Cache metrics
CACHE_HIT_RATIO = Gauge(
    "cache_hit_ratio",
    "Cache hit ratio (0-1)",
    ["cache_type"],  # redis, memory
)

CACHE_SIZE = Gauge(
    "cache_size_bytes",
    "Cache size in bytes",
    ["cache_type"],
)

# Circuit breaker metrics
CIRCUIT_BREAKER_STATE = Gauge(
    "circuit_breaker_state",
    "Circuit breaker state (0=closed, 0.5=half_open, 1=open)",
    ["service"],
)

CIRCUIT_BREAKER_ERRORS = Counter(
    "circuit_breaker_errors_total",
    "Errors detected by circuit breaker",
    ["service"],
)

# API metrics
API_REQUEST_DURATION = Histogram(
    "api_request_duration_seconds",
    "API request duration",
    ["endpoint", "method", "status"],
    buckets=(0.01, 0.05, 0.1, 0.5, 1, 5),
)

API_REQUESTS_TOTAL = Counter(
    "api_requests_total",
    "Total API requests",
    ["endpoint", "method", "status"],
)

# System metrics
ACTIVE_CONNECTIONS = Gauge(
    "active_connections",
    "Active database connections",
)

SYSTEM_UPTIME = Gauge(
    "system_uptime_seconds",
    "System uptime in seconds",
)

# Job metrics
JOB_EXECUTION_DURATION = Histogram(
    "job_execution_duration_seconds",
    "Background job execution time",
    ["job_name"],
    buckets=(1, 5, 10, 30, 60, 300),
)

JOB_EXECUTION_ERRORS = Counter(
    "job_execution_errors_total",
    "Total job execution errors",
    ["job_name", "error_type"],
)

JOB_LAST_RUN_TIMESTAMP = Gauge(
    "job_last_run_timestamp",
    "Unix timestamp of last job execution",
    ["job_name"],
)

# Deduplication metrics
NEWS_DEDUPLICATED_TOTAL = Counter(
    "news_deduplicated_total",
    "Total deduplication operations",
    ["action"],  # action: duplicate_detected, new_item, error
)
