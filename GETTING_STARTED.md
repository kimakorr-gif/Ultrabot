# 🚀 Getting Started with Ultrabot

**Time needed**: ~5 minutes  
**Difficulty**: Beginner-friendly

---

## ⚡ Super Quick Start (3 steps)

### Step 1: Clone & Setup
```bash
# Clone repository
git clone https://github.com/kimakorr-gif/Ultrabot.git
cd Ultrabot

# Run setup (Linux/macOS)
./install.sh

# Or on Windows:
# install.bat
```

### Step 2: Configure
```bash
# Edit .env with your credentials
nano .env  # or use any text editor

# Required values:
# TELEGRAM_TOKEN=your_bot_token
# TELEGRAM_CHANNEL_ID=-1001234567890
# YANDEX_API_KEY=your_api_key
```

### Step 3: Run
```bash
# Start Docker services
docker-compose up -d

# Run the app
make run

# Or development mode with auto-reload
make run-dev
```

**Done!** 🎉 App is running at `http://localhost:8000`

---

## 🤖 Get Your Telegram Bot Token

1. Open Telegram and find **@BotFather**
2. Send `/start` command
3. Send `/newbot` command
4. Follow instructions (give your bot a name)
5. Copy the token from response
6. Add it to `.env`:
   ```env
   TELEGRAM_TOKEN=123456:ABC-DEF1234ghIkl-zyx57W2v1u123ew11
   ```

---

## 📡 Get Yandex API Key

1. Go to https://cloud.yandex.com/
2. Create account or login
3. Create project
4. Go to "IAM" → "Service Accounts"
5. Create service account
6. Get API key
7. Add to `.env`:
   ```env
   YANDEX_API_KEY=your_api_key_here
   YANDEX_FOLDER_ID=your_folder_id
   ```

---

## 🗄️ PostgreSQL Setup (if not using Docker)

### macOS
```bash
brew install postgresql
brew services start postgresql
createdb ultrabot
```

### Ubuntu/Debian
```bash
sudo apt update && sudo apt install postgresql postgresql-contrib
sudo -u postgres createdb ultrabot
sudo -u postgres createuser ultrabot -P
```

### Windows
Download from https://www.postgresql.org/download/windows/

### Update .env
```env
DATABASE_URL=postgresql://ultrabot:password@localhost/ultrabot
```

---

## 📦 Without Docker (Alternative)

If you don't have Docker:

### 1. Install Redis (optional)
```bash
# macOS
brew install redis
redis-server

# Ubuntu
sudo apt install redis-server
redis-server

# Windows: Use Docker or WSL
```

### 2. Create PostgreSQL Database
See PostgreSQL Setup section above

### 3. Install Python Packages
```bash
pip install -r requirements.txt
```

### 4. Run Migrations
```bash
python -m alembic upgrade head
```

### 5. Start Application
```bash
make run-dev
```

---

## ✅ Verify Installation

### Check API is Running
```bash
curl http://localhost:8000/health
# Should return: {"status":"ok"}
```

### Check Database
```bash
curl http://localhost:8000/ready
```

### Run Tests
```bash
make test
```

### Check Code Quality
```bash
make lint
```

---

## 📖 Common Tasks

### View Logs
```bash
# All Docker services
docker-compose logs -f

# Just the app
docker-compose logs -f app

# Last 100 lines
docker-compose logs --tail 100
```

### Access Databases

#### PostgreSQL
```bash
# From Docker
docker-compose exec postgres psql -U ultrabot -d ultrabot

# From local installation
psql -U ultrabot -d ultrabot
```

#### Redis
```bash
docker-compose exec redis redis-cli
```

#### Prometheus
```bash
# Browse to: http://localhost:9090
```

#### Grafana
```bash
# Browse to: http://localhost:3000
# Login: admin / admin
```

---

## 🧪 Run Tests

```bash
# All tests
make test

# Specific test file
pytest tests/unit/test_scoring_service.py -v

# With coverage
make test-coverage
# Open htmlcov/index.html to view report
```

---

## 🛠️ Development Workflow

### 1. Activate Virtual Environment
```bash
source venv/bin/activate  # Linux/macOS
# or
venv\Scripts\activate     # Windows
```

### 2. Make Changes
Edit your code in `src/` directory

### 3. Format Code
```bash
make format
```

### 4. Run Tests
```bash
make test
```

### 5. Check Quality
```bash
make lint
```

### 6. Commit Changes
```bash
git add .
git commit -m "Your changes"
git push
```

---

## 🚀 Project Structure

```
Ultrabot/
├── src/                  # Application code
│   ├── core/            # Settings, logging, metrics
│   ├── domain/          # Business logic
│   ├── application/     # Use cases
│   ├── infrastructure/  # Adapters, DB, cache
│   └── presentation/    # API, Telegram bot
├── tests/               # Test suite
│   ├── unit/           # Unit tests
│   ├── integration/    # Integration tests
│   └── e2e/            # End-to-end tests
├── docs/                # Documentation
├── kubernetes/          # K8s manifests
├── docker/              # Docker config
├── .env.example         # Configuration template
├── requirements.txt     # Python dependencies
├── docker-compose.yml   # Local dev environment
├── Makefile            # Useful commands
└── setup.py            # Package setup
```

---

## 🎯 What This App Does

**Ultrabot** automatically:

1. 📰 **Fetches** 50+ gaming news RSS feeds
2. 🎮 **Filters** by gaming keywords (RPG, PS5, PC, etc.)
3. 🏆 **Scores** news by source quality and keywords
4. 🌍 **Translates** to Russian (preserves proper nouns)
5. 📤 **Publishes** to Telegram channel
6. 📊 **Monitors** with Prometheus metrics
7. 🔄 **Retries** on failures with exponential backoff
8. 🛡️ **Protects** with circuit breaker pattern

---

## 🔗 Useful Links

- 📖 Full Installation: [INSTALL.md](INSTALL.md)
- 🏗️ Architecture: [ARCHITECTURE.md](ARCHITECTURE.md)
- 📚 Deployment: [docs/DEPLOYMENT.md](docs/DEPLOYMENT.md)
- 📊 Monitoring: [docs/MONITORING.md](docs/MONITORING.md)
- 🔌 API Reference: [docs/API.md](docs/API.md)
- 👨‍💻 Developer Guide: [docs/DEVELOPMENT.md](docs/DEVELOPMENT.md)

---

## ❓ Troubleshooting

### "Python not found"
```bash
# Install from https://www.python.org/downloads/
# Need Python 3.11+
python3 --version
```

### "Port 8000 in use"
```bash
# Use different port
make run-dev PORT=8001

# Or kill process
lsof -ti:8000 | xargs kill -9  # Linux/macOS
```

### "Docker not running"
```bash
# Start Docker Desktop (Mac/Windows) or:
sudo systemctl start docker  # Linux

# Or skip Docker:
# Just need PostgreSQL and Redis running locally
```

### "Connection refused"
```bash
# Check services are running
docker-compose ps

# Or start them
docker-compose up -d
```

---

## 💡 Pro Tips

1. **Use Makefile**: Commands are shorter
   ```bash
   make help           # See all commands
   make test-coverage  # Get coverage report
   make format         # Auto-format code
   ```

2. **Watch logs**: Keep terminal open
   ```bash
   docker-compose logs -f
   ```

3. **Test often**: Catch bugs early
   ```bash
   make test
   ```

4. **Format before commit**: Keep code clean
   ```bash
   make format && make lint
   ```

5. **Check docs**: Most answers are there
   - Architecture: [ARCHITECTURE.md](ARCHITECTURE.md)
   - Deployment: [docs/DEPLOYMENT.md](docs/DEPLOYMENT.md)

---

## 🎓 Next Steps

After successful setup:

1. ✅ Run tests to verify everything works
2. ✅ Read [ARCHITECTURE.md](ARCHITECTURE.md) to understand the system
3. ✅ Configure your RSS feeds in database
4. ✅ Test Telegram integration with your channel
5. ✅ Monitor application at http://localhost:3000 (Grafana)
6. ✅ Deploy to production (see [docs/DEPLOYMENT.md](docs/DEPLOYMENT.md))

---

## 🆘 Need Help?

1. Check [INSTALL.md](INSTALL.md) for detailed setup
2. Review [docs/DEVELOPMENT.md](docs/DEVELOPMENT.md) for dev guide
3. Search [docs/](docs/) for specific topics
4. Check application logs: `docker-compose logs -f`
5. Run diagnostics:
   ```bash
   make check        # Lint + test
   curl http://localhost:8000/health  # API health
   ```

---

**You're all set! Happy coding! 🚀**

Questions? Check the [full documentation](docs/) or review the code comments.
