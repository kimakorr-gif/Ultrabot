# Development guide for Ultrabot

## Project Structure

```
src/
├── core/              # Framework & infrastructure setup
├── domain/            # Business logic (domain models, services)
├── application/       # Use cases & orchestration
├── infrastructure/    # External integrations
└── presentation/      # User interfaces (Telegram, Web)

tests/
├── unit/              # Unit tests (no external deps)
├── integration/       # Integration tests
└── e2e/               # End-to-end tests

docs/                  # Documentation
kubernetes/            # Kubernetes manifests
docker/                # Docker configuration
```

## Development Workflow

### 1. Create Feature Branch

```bash
git checkout -b feature/your-feature
```

### 2. Write Tests First

```bash
# Unit tests
pytest tests/unit/ -v

# Integration tests (requires services)
docker-compose up -d
pytest tests/integration/ -v
docker-compose down
```

### 3. Implement Feature

- Add domain entities/services (domain/)
- Add application logic (application/)
- Add infrastructure adapters (infrastructure/)
- Add presentation layer if needed

### 4. Code Quality Checks

```bash
# Format code
black src/ tests/
isort src/ tests/

# Type checking
mypy src/

# Linting
flake8 src/ --max-line-length=120
ruff check src/

# Coverage
pytest tests/ --cov=src --cov-report=html
```

### 5. Commit & Push

```bash
git add .
git commit -m "Feature: add xyz functionality"
git push origin feature/your-feature
```

### 6. Create Pull Request

- Write clear PR description
- Link related issues
- Ensure CI/CD passes
- Request code review

## Running Locally

### Start Services

```bash
docker-compose up -d postgres redis prometheus grafana
```

### Install Dependencies

```bash
python -m venv venv
source venv/bin/activate
pip install -e ".[dev]"
```

### Run Application

```bash
python -m src.main
```

### Run Tests

```bash
# All tests
pytest tests/ -v

# Specific test file
pytest tests/unit/test_scoring_service.py -v

# With coverage
pytest tests/ --cov=src --cov-report=html
```

### Check Code Quality

```bash
# All checks
black src/ tests/ && isort src/ tests/ && mypy src/ && flake8 src/

# Or use pre-commit hooks (optional)
pip install pre-commit
pre-commit install
```

## Common Tasks

### Add New Entity

1. Create entity in `domain/entities/`
2. Add repository interface in `domain/repositories/`
3. Add SQLAlchemy model in `infrastructure/database/models.py`
4. Implement repository in `infrastructure/database/repositories.py`
5. Add tests in `tests/unit/`

### Add New Service

1. Create service in `domain/services/`
2. Write unit tests in `tests/unit/`
3. Use in appropriate use case

### Add New Use Case

1. Create use case in `application/use_cases/`
2. Define ports (interfaces) in `application/ports/`
3. Implement infrastructure adapters
4. Add integration tests

### Add Prometheus Metric

1. Define in `src/core/metrics.py`
2. Use in relevant service
3. Test in unit tests
4. Add to Grafana dashboard

## Debugging

### Print Debugging

```python
from src.core.logger import get_logger

logger = get_logger(__name__)
logger.debug(f"Variable value: {variable}")
```

### Breakpoints

```python
import pdb; pdb.set_trace()  # Will drop into debugger
```

### VS Code Debugging

Create `.vscode/launch.json`:

```json
{
  "version": "0.2.0",
  "configurations": [
    {
      "name": "Python: Main",
      "type": "python",
      "request": "launch",
      "module": "src.main",
      "console": "integratedTerminal"
    }
  ]
}
```

## Database

### Create Migration

```bash
# Auto-generate from model changes
alembic revision --autogenerate -m "Add new column"

# Apply migration
alembic upgrade head

# Rollback
alembic downgrade -1
```

### Query Database

```bash
# Interactive
docker-compose exec postgres psql -U ultrabot -d ultrabot

# Or use Python
from src.infrastructure.database.models import SessionLocal
session = SessionLocal()
# Run queries...
```

## Documentation

### Update Architecture

Edit [ARCHITECTURE.md](ARCHITECTURE.md)

### Update API Docs

Edit [docs/API.md](docs/API.md)

### Update Deployment Guide

Edit [docs/DEPLOYMENT.md](docs/DEPLOYMENT.md)

## Performance Optimization

### Profile Code

```python
import cProfile
import pstats

profiler = cProfile.Profile()
profiler.enable()

# Your code here

profiler.disable()
stats = pstats.Stats(profiler)
stats.sort_stats('cumulative').print_stats(10)
```

### Monitor Memory

```bash
# In Docker
docker stats ultrabot-postgres

# With Python
import tracemalloc
tracemalloc.start()
# Your code
current, peak = tracemalloc.get_traced_memory()
print(f"Current: {current / 1e6}MB; Peak: {peak / 1e6}MB")
```

## Useful Commands

```bash
# Restart all services
docker-compose restart

# View logs
docker-compose logs -f ultrabot-postgres
docker-compose logs -f ultrabot-redis

# Clean up
docker-compose down -v
rm -rf __pycache__ .pytest_cache .mypy_cache

# Get shell in container
docker-compose exec postgres bash
docker-compose exec redis redis-cli

# Database dump
docker-compose exec postgres pg_dump -U ultrabot ultrabot > backup.sql
```

## Resources

- [Python 3.11 Docs](https://docs.python.org/3.11/)
- [SQLAlchemy 2.0](https://docs.sqlalchemy.org/20/)
- [FastAPI](https://fastapi.tiangolo.com/)
- [Pytest](https://docs.pytest.org/)
- [Clean Architecture](https://blog.cleancoder.com/uncle-bob/2012/08/13/the-clean-architecture.html)
- [Domain-Driven Design](https://martinfowler.com/bliki/DomainDrivenDesign.html)
