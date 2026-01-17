# 📥 Ultrabot - Installation & Setup Guide

**Version**: 1.0.0  
**Last Updated**: January 2026  
**Status**: ✅ Production Ready

---

## 🚀 Quick Start (5 minutes)

### Option A: Automated Installation (Recommended)

#### Linux/macOS
```bash
chmod +x install.sh
./install.sh
```

#### Windows
```bash
install.bat
```

That's it! The script will:
- ✅ Check Python version (3.11+)
- ✅ Create virtual environment
- ✅ Install all dependencies
- ✅ Create `.env` file
- ✅ Start Docker services
- ✅ Setup database

### Option B: Manual Installation

#### 1. Prerequisites
- **Python**: 3.11 or higher ([Download](https://www.python.org/downloads/))
- **Git**: For cloning repository
- **Docker Desktop** (optional): For services

#### 2. Clone Repository
```bash
git clone https://github.com/kimakorr-gif/Ultrabot.git
cd Ultrabot
```

#### 3. Create Virtual Environment

**Linux/macOS**:
```bash
python3 -m venv venv
source venv/bin/activate
```

**Windows**:
```bash
python -m venv venv
venv\Scripts\activate
```

#### 4. Install Dependencies
```bash
pip install --upgrade pip
pip install -r requirements.txt
```

#### 5. Create Configuration File
```bash
cp .env.example .env
```

Edit `.env` with your credentials:
```env
# Telegram
TELEGRAM_TOKEN=your_bot_token_here
TELEGRAM_CHANNEL_ID=-1001234567890

# Yandex Translate
YANDEX_API_KEY=your_api_key_here
YANDEX_FOLDER_ID=your_folder_id

# Database
DATABASE_URL=postgresql://user:password@localhost/ultrabot

# Redis
REDIS_URL=redis://localhost:6379/0
```

#### 6. Start Services (Docker Compose)
```bash
docker-compose up -d
```

This starts:
- PostgreSQL database
- Redis cache
- Prometheus monitoring
- Grafana dashboard

Check status:
```bash
docker-compose ps
```

#### 7. Run Database Migrations
```bash
python -m alembic upgrade head
```

#### 8. Run Application

**Production Mode**:
```bash
make run
# or
python -m src.main
```

**Development Mode** (with auto-reload):
```bash
make run-dev
# or
python -m uvicorn src.main:app --reload --host 0.0.0.0 --port 8000
```

---

## 📋 System Requirements

### Minimum
- **CPU**: 2 cores
- **RAM**: 2 GB
- **Storage**: 500 MB
- **Python**: 3.11+
- **OS**: Linux, macOS, or Windows 10+

### Recommended
- **CPU**: 4 cores
- **RAM**: 4 GB
- **Storage**: 5 GB
- **Python**: 3.12
- **OS**: Ubuntu 22.04 LTS / macOS 12+ / Windows 11

---

## 🐍 Python Version Check

```bash
# Check installed version
python3 --version

# Should output something like:
# Python 3.11.7
# Python 3.12.1
```

**If you have Python 3.10 or earlier**:
```bash
# Install Python 3.11+ from https://www.python.org/downloads/
# Then create virtual environment with specific version:
python3.11 -m venv venv
```

---

## ⚙️ Environment Variables

### Required (No defaults)
```env
TELEGRAM_TOKEN=your_bot_token
TELEGRAM_CHANNEL_ID=-1001234567890
YANDEX_API_KEY=your_api_key
```

### Database (with defaults)
```env
# PostgreSQL
DATABASE_URL=postgresql://ultrabot:password@localhost/ultrabot
DB_TIMEOUT=30
SQL_ECHO=false

# Redis
REDIS_URL=redis://localhost:6379/0
REDIS_DEFAULT_TTL=3600
```

### Application
```env
ENVIRONMENT=development  # or production
LOG_LEVEL=INFO
API_HOST=0.0.0.0
API_PORT=8000

# Processing
RSS_CHECK_INTERVAL=300
MIN_SCORE_THRESHOLD=8
PUBLISH_DELAY=600
```

See `.env.example` for all options.

---

## 🐳 Docker Services

### Start All Services
```bash
docker-compose up -d
```

### Check Status
```bash
docker-compose ps
```

### View Logs
```bash
# All services
docker-compose logs -f

# Specific service
docker-compose logs -f postgres
docker-compose logs -f redis
docker-compose logs -f prometheus
```

### Stop Services
```bash
docker-compose down
```

### Stop & Remove Data
```bash
docker-compose down -v
```

### Service URLs
- **PostgreSQL**: `localhost:5432`
- **Redis**: `localhost:6379`
- **Prometheus**: `http://localhost:9090`
- **Grafana**: `http://localhost:3000`

Grafana login:
- Username: `admin`
- Password: `admin`

---

## 🧪 Testing

### Run All Tests
```bash
make test
```

### Run Tests with Coverage
```bash
make test-coverage
```

Opens HTML report in `htmlcov/index.html`

### Run Specific Test Type
```bash
make test-unit        # Unit tests only
make test-integration # Integration tests
make test-e2e         # End-to-end tests
```

### Run Single Test
```bash
python -m pytest tests/unit/test_scoring_service.py::TestScoringService::test_score_keywords -v
```

---

## 🔍 Code Quality

### Lint Code
```bash
make lint
```

Checks:
- Black (formatting)
- isort (imports)
- Flake8 (style)
- MyPy (types)
- Ruff (performance)

### Format Code
```bash
make format
```

Auto-fixes:
- Code formatting
- Import ordering
- Minor style issues

### Type Check
```bash
make type-check
```

---

## 🗄️ Database

### Create Database (if not using Docker)

**PostgreSQL**:
```bash
createdb ultrabot
createuser ultrabot -P  # Will prompt for password
psql ultrabot -c "GRANT ALL PRIVILEGES ON DATABASE ultrabot TO ultrabot;"
```

### Run Migrations
```bash
python -m alembic upgrade head
```

### Create New Migration
```bash
python -m alembic revision --autogenerate -m "Your migration name"
```

### Rollback Last Migration
```bash
python -m alembic downgrade -1
```

### View Migration History
```bash
python -m alembic history
```

---

## 🌐 API Endpoints

### Health Checks
```bash
# Liveness probe
curl http://localhost:8000/health

# Readiness probe
curl http://localhost:8000/ready

# Application stats
curl http://localhost:8000/stats

# Prometheus metrics
curl http://localhost:8000/metrics
```

### Telegram Bot
- Start bot: `/start`
- Help: `/help`
- Status: `/status`

---

## 🚀 Running Application

### Development Mode
Best for local development with auto-reload:
```bash
make run-dev
```

Features:
- Auto-reload on code changes
- Detailed error messages
- Debug logging
- Interactive traceback

### Production Mode
For local testing or deployment:
```bash
make run
```

Features:
- Optimized performance
- Graceful error handling
- Production logging
- Signal handling (SIGTERM, SIGINT)

---

## 📦 Useful Commands

```bash
# Setup & Installation
make setup              # Full setup (venv + dependencies + .env)
make setup-dev         # Setup with dev dependencies
make install           # Install dependencies
make install-dev       # Install with dev tools

# Running
make run              # Run application
make run-dev          # Run with auto-reload

# Testing
make test             # Run all tests
make test-coverage    # Run with coverage report
make test-unit        # Unit tests only
make test-integration # Integration tests
make test-e2e         # E2E tests

# Code Quality
make lint             # Run all linters
make format           # Format code
make check            # Lint + test
make type-check       # MyPy type checking

# Database
make db-migrate       # Run migrations
make db-rollback      # Rollback migration
make db-new           # Create new migration

# Docker
make docker-build     # Build Docker image
make docker-run       # Start Docker Compose
make docker-stop      # Stop services
make docker-logs      # View logs
make docker-clean     # Clean all Docker data

# Cleanup
make clean            # Remove generated files

# Help
make help             # Show all commands
```

---

## 🐛 Troubleshooting

### Issue: "Python 3.11+ required"
**Solution**:
```bash
# Install from https://www.python.org/downloads/
# On macOS with Homebrew:
brew install python@3.11

# On Ubuntu:
sudo apt update && sudo apt install python3.11 python3.11-venv
```

### Issue: "ModuleNotFoundError: No module named 'src'"
**Solution**:
```bash
# Make sure you're in the right directory:
cd /path/to/Ultrabot

# Reinstall in editable mode:
pip install -e .
```

### Issue: "PostgreSQL connection refused"
**Solutions**:
1. Start Docker services:
   ```bash
   docker-compose up -d
   ```

2. Or install PostgreSQL locally:
   - macOS: `brew install postgresql`
   - Ubuntu: `sudo apt install postgresql`
   - Windows: Download from https://www.postgresql.org/download/

3. Check connection string in `.env`:
   ```env
   DATABASE_URL=postgresql://user:password@localhost/ultrabot
   ```

### Issue: "Redis connection refused"
**Solutions**:
1. Start Docker services:
   ```bash
   docker-compose up -d redis
   ```

2. Or install Redis locally:
   - macOS: `brew install redis`
   - Ubuntu: `sudo apt install redis-server`
   - Windows: Use Docker (easiest option)

### Issue: "TELEGRAM_TOKEN not found"
**Solution**:
1. Create `.env` file:
   ```bash
   cp .env.example .env
   ```

2. Get token from BotFather:
   - Open Telegram
   - Message @BotFather
   - Create new bot
   - Copy token to `.env`

### Issue: "Port 8000 already in use"
**Solution**:
```bash
# Use different port:
make run-dev PORT=8001

# Or kill process using port 8000:
# macOS/Linux:
lsof -ti:8000 | xargs kill -9

# Windows:
netstat -ano | findstr :8000
taskkill /PID <PID> /F
```

### Issue: Tests failing with "no attribute 'call'"
**Solution**:
```bash
# Update pytest-mock:
pip install --upgrade pytest-mock
```

---

## 📝 Next Steps

### After Installation:
1. ✅ Application running and accessible at `http://localhost:8000`
2. ✅ Database initialized with migrations
3. ✅ Redis cache connected
4. ✅ Telegram bot ready to use

### Before Production:
1. Update `.env` with real credentials
2. Run full test suite: `make test`
3. Check code quality: `make lint`
4. Review logs: `docker-compose logs`
5. Test with real feeds and Telegram channel

### Monitoring:
- Prometheus: `http://localhost:9090`
- Grafana: `http://localhost:3000`
- Logs: `docker-compose logs -f`
- Health: `curl http://localhost:8000/health`

---

## 📖 Documentation

- **[ARCHITECTURE.md](ARCHITECTURE.md)** - System design and architecture
- **[docs/DEPLOYMENT.md](docs/DEPLOYMENT.md)** - Production deployment
- **[docs/MONITORING.md](docs/MONITORING.md)** - Monitoring setup
- **[docs/API.md](docs/API.md)** - API documentation
- **[docs/DEVELOPMENT.md](docs/DEVELOPMENT.md)** - Developer guide
- **[COMPLETION_REPORT.md](COMPLETION_REPORT.md)** - Project completion details

---

## ❓ Need Help?

### Check Logs
```bash
# Application logs
docker-compose logs app

# Database logs
docker-compose logs postgres

# Redis logs
docker-compose logs redis

# All logs
docker-compose logs -f
```

### Run Tests
```bash
# Verify installation
make test

# With detailed output
make test -v
```

### Health Check
```bash
# API health
curl -v http://localhost:8000/health

# Database connectivity
curl http://localhost:8000/ready

# Application stats
curl http://localhost:8000/stats
```

---

## ✅ Installation Checklist

- [ ] Python 3.11+ installed
- [ ] Repository cloned
- [ ] Virtual environment created and activated
- [ ] Dependencies installed (`pip install -r requirements.txt`)
- [ ] `.env` file created and configured
- [ ] Docker services running (`docker-compose ps`)
- [ ] Database migrated (`alembic upgrade head`)
- [ ] Application running (`make run`)
- [ ] Tests passing (`make test`)
- [ ] Code quality checks passing (`make lint`)

---

## 🎉 You're Ready!

The application is now ready for:
- ✅ Local development
- ✅ Testing
- ✅ Production deployment

Start the bot and happy coding! 🚀

---

**For issues or questions**, check [docs/DEVELOPMENT.md](docs/DEVELOPMENT.md) or review error logs.
