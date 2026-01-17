#!/bin/bash
# run.sh - Quick run script for Ultrabot

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "${BLUE}🤖 Ultrabot - Gaming News Aggregator${NC}"
echo "========================================"
echo ""

# Check if venv exists
if [ ! -d "venv" ]; then
    echo -e "${RED}✗ Virtual environment not found!${NC}"
    echo ""
    echo "Please run setup first:"
    echo "  ./install.sh (automatic setup)"
    echo "  or"
    echo "  make setup (manual setup)"
    echo ""
    exit 1
fi

# Activate venv
source venv/bin/activate

# Check if .env exists
if [ ! -f ".env" ]; then
    echo -e "${RED}✗ .env file not found!${NC}"
    echo ""
    echo "Please create .env file:"
    echo "  cp .env.example .env"
    echo "  nano .env  # edit with your credentials"
    echo ""
    exit 1
fi

# Check Docker
echo "Checking Docker services..."
if ! command -v docker &> /dev/null; then
    echo -e "${RED}⚠ Docker not installed${NC}"
    echo "  Services not started (continue anyway? y/n)"
else
    # Check if containers are running
    if ! docker ps | grep -q "postgres"; then
        echo "Starting Docker services..."
        docker-compose up -d 2>/dev/null || echo "  (could not start Docker)"
        sleep 3
    fi
fi

echo ""

# Run app
MODE="${1:-production}"

if [ "$MODE" = "dev" ] || [ "$MODE" = "development" ] || [ "$MODE" = "watch" ]; then
    echo -e "${GREEN}▶ Starting in DEVELOPMENT mode (auto-reload)${NC}"
    echo ""
    echo "Endpoints:"
    echo "  🌐 API: http://localhost:8000"
    echo "  📊 Metrics: http://localhost:8000/metrics"
    echo "  ❤️  Health: http://localhost:8000/health"
    echo ""
    echo "Press Ctrl+C to stop"
    echo ""
    python -m uvicorn src.main:app --reload --host 0.0.0.0 --port 8000 --log-level info
else
    echo -e "${GREEN}▶ Starting in PRODUCTION mode${NC}"
    echo ""
    echo "Endpoints:"
    echo "  🌐 API: http://localhost:8000"
    echo "  📊 Metrics: http://localhost:8000/metrics"
    echo "  ❤️  Health: http://localhost:8000/health"
    echo ""
    echo "Press Ctrl+C to stop"
    echo ""
    python -m src.main
fi
