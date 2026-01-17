# Ultrabot - Архитектура системы

## 1. Обзор системы

**Ultrabot** — это production-ready система агрегации игровых новостей с публикацией в Telegram-канал. Система мониторит 50+ RSS-лент, фильтрует контент по релевантности, переводит с сохранением имен собственных и публикует в канал с медиа-вложениями.

### Ключевые метрики
- **Uptime**: 99.9%
- **Latency обработки новости**: < 30 сек
- **Успешная публикация**: > 95%
- **Максимум памяти**: < 512 MB на инстанс

---

## 2. Архитектурная диаграмма

```
┌─────────────────────────────────────────────────────────────────┐
│                       RSS SOURCES (50+)                          │
│  IGN, Polygon, Kotaku, Eurogamer, GameSpot, RockPaperShotgun     │
└────────────────────┬────────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────────────┐
│                  RSS Parser Service                              │
│  • Параллельная обработка 50+ фидов                             │
│  • Поддержка RSS 2.0, Atom, медиа-вложения                       │
│  • User-Agent ротация                                           │
│  • Извлечение полного текста по ссылке                          │
└────────────────────┬────────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────────────┐
│            Deduplication & Scoring Service                       │
│  • MD5 хеширование (title + content[:500])                       │
│  • 3-уровневая система ключевых слов (вес 1-3)                   │
│  • Бонусы за свежесть (+5 за < 15 мин)                          │
│  • Веса источников (IGN=10, Polygon=8, etc.)                     │
│  • Минимальный порог: 8 баллов                                  │
│  • Антикликбейт фильтр                                          │
└────────────────────┬────────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────────────┐
│          Translation Service (Yandex.Translate API)              │
│  • Трансляция заголовка + полного текста                         │
│  • Сохранение имен собственных через placeholder-замену         │
│  • Кэширование переводов (Redis, TTL 3600s)                     │
│  • Circuit breaker + Retry с exponential backoff                │
└────────────────────┬────────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────────────┐
│          Media Extraction & Validation Service                   │
│  • Извлечение изображений (макс 5 штук)                         │
│  • Поддержка YouTube, IGN, Vimeo embeds                          │
│  • Проверка доступности и размера                               │
│  • Кэширование метаданных медиа (TTL 86400s)                    │
└────────────────────┬────────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────────────┐
│              Content Formatter & Hashtag Generator               │
│  • Форматирование для Telegram HTML разметки                     │
│  • Структура: Title → Text → Media → Hashtags → Source          │
│  • Макс длина: 4096 символов                                    │
│  • Auto-генерация 10 хештегов на основе контента                │
│  • Извлечение названий игр, жанров, платформ                    │
└────────────────────┬────────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────────────┐
│             Publication Queue (Priority-based)                   │
│  • Асинхронная очередь с приоритетами                           │
│  • Задержка между постами: 600 сек (настраивается)              │
│  • Graceful shutdown с сохранением состояния                    │
│  • Dead Letter Queue для неудачных публикаций                   │
└────────────────────┬────────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────────────┐
│                  Telegram Publisher Bot                          │
│  • Асинхронная публикация в канал                                │
│  • Rate limiting (600 сек между постами)                        │
│  • Retry логика для неудачных попыток                           │
│  • Сохранение attribution к источникам                          │
└────────────────────┬────────────────────────────────────────────┘
                     │
                     ▼
            ┌───────────────────┐
            │   TELEGRAM CHANNEL │
            │   (до 10k подписчиков)
            └───────────────────┘

SUPPORTING INFRASTRUCTURE:
┌──────────────────────────────┬──────────────────────┬────────────────┐
│  PostgreSQL Database         │  Redis Cache         │  Prometheus    │
│  • News storage              │  • Translation cache │  • Metrics     │
│  • Dedup hashes (7д авто)   │  • Feed response     │  • Alerts      │
│  • Feed sources              │  • Media metadata    │  • Dashboards  │
│  • Publication logs          │                      │                │
└──────────────────────────────┴──────────────────────┴────────────────┘
```

---

## 3. Clean Architecture слои

### 3.1 Domain Layer (Бизнес-логика)
```
domain/
├── entities/
│   ├── news_item.py        # NewsItem, NewsItemContent
│   ├── feed.py             # Feed, FeedSource
│   └── publication.py      # Publication, PublicationStatus
├── value_objects/
│   ├── url.py              # URL валидация
│   ├── hash.py             # Dedup hash
│   ├── score.py            # Scoring результаты
│   └── language.py         # Language enum
├── services/
│   ├── scoring_service.py  # Расчет релевантности
│   ├── translator_service.py # С сохранением сущностей
│   ├── hashtag_service.py  # Генератор хештегов
│   └── media_service.py    # Извлечение медиа
└── repositories/
    ├── news_repository.py  # Abstract
    ├── feed_repository.py  # Abstract
    └── publication_repository.py # Abstract
```

**Ответственность**: Чистая бизнес-логика без зависимостей на фреймворки

### 3.2 Application Layer (Use Cases)
```
application/
├── use_cases/
│   ├── process_feeds_use_case.py      # Парсинг RSS
│   ├── translate_news_use_case.py    # Трансляция контента
│   ├── score_news_use_case.py        # Расчет баллов
│   ├── publish_news_use_case.py      # Публикация в Telegram
│   └── deduplicate_news_use_case.py  # Проверка дубликатов
├── ports/
│   ├── rss_parser_port.py            # RSS парсер interface
│   ├── translator_port.py            # Translator interface
│   ├── cache_port.py                 # Cache interface
│   └── telegram_port.py              # Telegram interface
└── dto/
    ├── process_feed_input.py
    └── publish_post_output.py
```

**Ответственность**: Координирование бизнес-процессов, использование интерфейсов

### 3.3 Infrastructure Layer (Адаптеры)
```
infrastructure/
├── database/
│   ├── models.py                 # SQLAlchemy ORM models
│   ├── repositories.py          # Repository реализации
│   └── migrations/              # Alembic миграции
├── external/
│   ├── rss_parser.py            # feedparser adapter
│   ├── yandex_translator.py     # Yandex API adapter
│   ├── telegram_client.py       # aiogram adapter
│   └── http_client.py           # aiohttp session manager
├── cache/
│   ├── redis_cache.py           # Redis реализация
│   └── memory_cache.py          # In-memory cache
└── monitoring/
    ├── metrics.py               # Prometheus метрики
    └── logger.py                # Structured logging
```

**Ответственность**: Конкретная реализация интерфейсов, работа с внешними сервисами

### 3.4 Presentation Layer
```
presentation/
├── telegram/
│   ├── bot.py                   # Bot initialization
│   ├── handlers.py              # Command handlers
│   └── dispatcher.py            # Message dispatcher
└── web/
    ├── health_api.py            # FastAPI health checks
    └── metrics_api.py           # Prometheus endpoint
```

**Ответственность**: Точки входа для пользователей/систем

### 3.5 Core Layer (Инфраструктура)
```
core/
├── di.py                        # Dishka DI контейнер
├── settings.py                  # Pydantic Settings
├── exceptions.py                # Кастомные исключения
├── metrics.py                   # Prometheus metrics
├── logger.py                    # Structured logging
└── constants.py                 # Глобальные константы
```

---

## 4. Dependency Injection (Dishka)

### Scope иерархия:
- **APP**: Единственный инстанс на приложение (Settings, DB Pool, Redis)
- **REQUEST**: Создается на каждый request/event (Use Cases)
- **SESSION**: Временный скоп (транзакции)

### Пример: UseCases автоматически разрешаются через DI
```python
# Dishka автоматически разрешает все зависимости:
process_feeds = container.get(ProcessFeedsUseCase)
# ↓ автоматически создает:
# - ProcessFeedsUseCase(
#     rss_parser=RSSParserAdapter,      # ← Infrastructure
#     news_scorer=ScoringService,        # ← Domain
#     repository=PostgresNewsRepository, # ← Infrastructure
#     logger=logger,                     # ← Core
#     metrics=prometheus_metrics         # ← Core
#   )
```

---

## 5. Основные потоки данных

### 5.1 Feed Processing Pipeline (каждые 5 минут)
```
1. RSS Parser Service
   ├─ Fetch feed (с кэшем 300s)
   ├─ Parse entries
   ├─ Extract full content via HTTP
   └─ Return NewsItem[]

2. Deduplication Service
   ├─ Calc MD5(title + content[:500])
   ├─ Check в database
   └─ Filter duplicates

3. Scoring Service
   ├─ Keyword extraction (High/Med/Low)
   ├─ Source weight bonus
   ├─ Freshness bonus (+5 за <15 мин)
   ├─ Anticlickbait check
   └─ Total score >= 8 ? → proceed : drop

4. Translation Service
   ├─ Extract named entities (regex + patterns)
   ├─ Replace with placeholders
   ├─ Send to Yandex.Translate
   ├─ Restore entities
   ├─ Cache result (3600s)
   └─ Return translated content

5. Media Extraction
   ├─ Find images (max 5)
   ├─ Extract video embeds
   ├─ Validate accessibility
   └─ Cache metadata (86400s)

6. Content Formatting
   ├─ Generate hashtags (max 10)
   ├─ Build Telegram HTML post
   ├─ Ensure < 4096 chars
   └─ Return FormattedPost

7. Publication Queue
   └─ Enqueue with priority → Queue

8. Publisher
   ├─ Dequeue with 600s delay
   ├─ Publish to Telegram
   ├─ On success: log + mark published
   └─ On failure: retry + Dead Letter Queue
```

### 5.2 Error Handling & Resilience
```
Circuit Breaker: Yandex API
├─ Failure threshold: 5
├─ Recovery timeout: 60s
├─ On OPEN: fail fast, log error

Retry Pattern:
├─ Max attempts: 3
├─ Backoff: exponential (1, 2, 4, 8 secs)
├─ Jitter: random ±20%

Dead Letter Queue:
├─ Failed publications after 3 retries
├─ Manual review + admin dashboard
└─ Metrics: dlq_size, dlq_age

Health Checks:
├─ /health: basic liveness
├─ /ready: readiness (DB, Redis, Telegram connected)
└─ /metrics: Prometheus endpoint
```

---

## 6. База данных

### ERD (Entity Relationship Diagram)
```
feeds
├─ id: UUID (PK)
├─ url: VARCHAR(2048)
├─ name: VARCHAR(255)
├─ source_weight: INT (default 5)
├─ enabled: BOOL
├─ created_at: TIMESTAMP
└─ updated_at: TIMESTAMP

news_items
├─ id: UUID (PK)
├─ feed_id: UUID (FK)
├─ title_en: TEXT
├─ title_ru: TEXT
├─ content_en: TEXT
├─ content_ru: TEXT
├─ dedup_hash: VARCHAR(32) (indexed)
├─ score: INT
├─ source_url: VARCHAR(2048)
├─ published_at: TIMESTAMP
├─ created_at: TIMESTAMP
└─ [automatically deleted after 7 days]

publications
├─ id: UUID (PK)
├─ news_item_id: UUID (FK)
├─ telegram_message_id: INT
├─ status: ENUM(pending, published, failed)
├─ media_urls: JSONB
├─ hashtags: JSONB
├─ published_at: TIMESTAMP
└─ error_message: TEXT

metrics_log
├─ id: UUID (PK)
├─ event_type: VARCHAR(50)
├─ source: VARCHAR(100)
├─ duration_ms: INT
├─ status: VARCHAR(20)
└─ timestamp: TIMESTAMP

Indexes:
- news_items(dedup_hash) UNIQUE
- news_items(published_at)
- news_items(score)
- publications(news_item_id)
- publications(status)
```

---

## 7. Кэширование

### Redis schema:
```
news:translated:{lang}:{hash}
└─ Translated content (TTL: 3600s)

feed:response:{feed_id}
└─ Raw feed response (TTL: 300s)

media:metadata:{url_hash}
└─ Media info (TTL: 86400s)

session:{user_id}
└─ User session state (TTL: 604800s)
```

### In-Memory Cache:
```
LocalCache (LRU, max 1000 items):
├─ Keyword patterns
├─ Game names database
├─ Platform/Genre taxonomy
└─ User-Agent list for rotation
```

---

## 8. Мониторинг & Observability

### Prometheus метрики:
```
news_processed_total{source, status}
├─ Counter: total news processed
└─ Labels: source name, status (ok/filtered/duplicate)

translation_duration_seconds{lang_pair}
├─ Histogram: translation latency
└─ Buckets: [0.1, 0.5, 1, 2, 5, 10, 30]

rss_fetch_duration_seconds{feed_name}
├─ Histogram: RSS fetch time
└─ Buckets: [0.5, 1, 2, 5, 10, 30]

publication_queue_size
├─ Gauge: current queue depth
└─ Alert if > 100 (backlog)

telegram_publish_duration_seconds{status}
├─ Histogram: publication latency
└─ Buckets: [0.5, 1, 2, 5, 10]

api_errors_total{endpoint, error_type}
├─ Counter: API errors
└─ Alert if rate > 1% of requests

circuit_breaker_state{service}
├─ Gauge: state (0=closed, 1=open, 0.5=half_open)
└─ Alert if OPEN for > 5min
```

### Structured Logging (JSON):
```json
{
  "timestamp": "2026-01-17T10:30:45.123Z",
  "level": "INFO",
  "logger": "application.use_cases.process_feeds",
  "message": "News processed successfully",
  "correlation_id": "uuid-xxx",
  "context": {
    "feed_name": "ign.com",
    "news_count": 15,
    "duration_ms": 2340,
    "score_distribution": {"high": 5, "medium": 7, "low": 3}
  },
  "user_id": "admin" [optional]
}
```

---

## 9. Развертывание

### Docker:
```
Multi-stage Dockerfile:
├─ Builder: Python 3.11-slim + build tools
│  └─ Install dependencies
├─ Runtime: Python 3.11-slim
│  ├─ Copy wheels from builder
│  ├─ Create non-root user
│  ├─ HEALTHCHECK инструкции
│  └─ Expose ports: 8000 (HTTP), 9090 (Metrics)
└─ Image size: ~200MB

.dockerignore:
├─ .git, .github
├─ __pycache__, *.pyc
├─ .venv, venv
├─ tests (optional)
└─ docs (optional)
```

### Kubernetes (Production):
```
Deployment:
├─ 3 replicas (for redundancy)
├─ Resource limits: CPU 500m, Memory 512Mi
├─ livenessProbe: /health (30s interval)
├─ readinessProbe: /ready (10s interval)
├─ Graceful shutdown: terminationGracePeriodSeconds: 30

Service:
├─ Type: ClusterIP
├─ Port: 8000
└─ TargetPort: 8000

ConfigMap:
├─ Non-sensitive settings
├─ Feature flags
└─ Logging level

Secrets:
├─ telegram_token
├─ yandex_api_key
├─ database_url
└─ redis_url

HorizontalPodAutoscaler:
├─ Min replicas: 2
├─ Max replicas: 5
├─ Target CPU: 70%
└─ Target memory: 80%

Ingress:
├─ TLS (cert-manager)
├─ health.example.com → /health
└─ metrics.example.com → /metrics
```

---

## 10. Безопасность

### Требования:
- ✅ Все секреты в переменных окружения (.env)
- ✅ Валидация всех входных данных (Pydantic)
- ✅ Rate limiting для API endpoints
- ✅ HTTPS в production (TLS)
- ✅ Non-root контейнер
- ✅ Network policies (если K8s)
- ✅ Логирование без sensitive data
- ✅ Регулярные обновления зависимостей

---

## 11. Тестовая стратегия

### Test pyramid:
```
         /\
        /  \  E2E (5%)
       /────\
      /      \
     / Integr \  Integration (20%)
    /──────────\
   /            \
  /              \  Unit (75%)
 /────────────────\
├─────────────────┤
  Base fixtures
```

### Тесты:
- **Unit**: Mocking external dependencies (redis, http, db)
- **Integration**: Real PostgreSQL + Redis (via testcontainers)
- **E2E**: Full pipeline with mock Telegram API
- **Coverage**: > 80% (enforced in CI)

---

## 12. CI/CD Pipeline

### GitHub Actions:
```yaml
on: [push, pull_request, schedule(daily)]

Lint:
├─ black --check
├─ isort --check-only
├─ flake8 --max-line-length=120
└─ mypy --strict

Test:
├─ pytest tests/unit --cov=src --cov-report=xml
├─ pytest tests/integration
└─ Upload coverage to Codecov

Build:
├─ Build Docker image
├─ Push to DockerHub/GitHub Container Registry
└─ Tag: latest, git-sha, semver

Security:
├─ Trivy scan Docker image
├─ Dependabot checks
└─ SAST (bandit)

Deploy (on main):
├─ kubectl apply -f kubernetes/
├─ Wait for rollout
└─ Run smoke tests
```

---

## 13. Roadmap бонусных фич

1. **ML для кликбейта**: Transformer-based classifier (tiny BERT)
2. **Auto-категоризация**: Game genres/platforms extraction
3. **Web Dashboard**: React + FastAPI для мониторинга
4. **A/B тестирование**: Заголовков и время публикации
5. **Multi-language**: Поддержка 5+ языков перевода
6. **S3 backup**: Медиа архивирование в облако
7. **RSS auto-discovery**: Автоматическое добавление лент

---

## Документы-спутники

- [DEPLOYMENT.md](docs/DEPLOYMENT.md) — Инструкция по развертыванию
- [MONITORING.md](docs/MONITORING.md) — Настройка мониторинга
- [API.md](docs/API.md) — REST API документация
- [DEVELOPMENT.md](docs/DEVELOPMENT.md) — Гайд для разработчиков
