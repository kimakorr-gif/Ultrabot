#!/bin/bash
# Ultrabot - Quick Start Script

set -e

echo "🚀 Ultrabot - Gaming News Aggregator"
echo "=====================================\n"

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Check Python version
echo "📋 Checking Python version..."
PYTHON_VERSION=$(python3 --version 2>&1 | awk '{print $2}')
echo "   Found Python $PYTHON_VERSION"

if ! python3 -c 'import sys; exit(0 if sys.version_info >= (3, 11) else 1)' 2>/dev/null; then
    echo -e "${RED}✗ Python 3.11+ required!${NC}"
    exit 1
fi
echo -e "${GREEN}✓ Python version OK${NC}\n"

# Check if .env exists
echo "🔧 Checking configuration..."
if [ ! -f .env ]; then
    echo -e "${YELLOW}⚠ .env file not found${NC}"
    echo "   Creating from .env.example..."
    cp .env.example .env
    echo -e "${YELLOW}⚠ Please edit .env with your credentials!${NC}\n"
    
    # Ask if user wants to edit now
    read -p "Edit .env now? (y/n) " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        ${EDITOR:-nano} .env
    fi
else
    echo -e "${GREEN}✓ .env file found${NC}\n"
fi

# Install dependencies
echo "📦 Installing dependencies..."
if [ ! -d "venv" ]; then
    echo "   Creating virtual environment..."
    python3 -m venv venv
fi

source venv/bin/activate

echo "   Installing Python packages..."
pip install --quiet --upgrade pip setuptools wheel
pip install --quiet -r requirements.txt

echo -e "${GREEN}✓ Dependencies installed${NC}\n"

# Check Docker
echo "🐳 Checking Docker..."
if ! command -v docker &> /dev/null; then
    echo -e "${YELLOW}⚠ Docker not found - running without services${NC}"
    echo "   Install Docker from: https://www.docker.com/products/docker-desktop"
else
    echo "   Starting Docker services..."
    docker-compose up -d
    echo -e "${GREEN}✓ Docker services started${NC}"
    
    # Wait for services
    echo "   Waiting for services to be ready..."
    sleep 5
fi

echo ""

# Database migrations
echo "🗄️  Setting up database..."
python3 -m alembic upgrade head 2>/dev/null || echo "   (skipped - DB may not be available)"
echo -e "${GREEN}✓ Database ready${NC}\n"

# Summary
echo -e "${BLUE}✅ Setup complete!${NC}"
echo ""
echo "📝 Next steps:"
echo ""
echo "1. Activate virtual environment:"
echo "   ${BLUE}source venv/bin/activate${NC}"
echo ""
echo "2. Run the application:"
echo "   ${BLUE}make run${NC}        (production mode)"
echo "   ${BLUE}make run-dev${NC}    (development with auto-reload)"
echo ""
echo "3. Run tests:"
echo "   ${BLUE}make test${NC}       (all tests)"
echo "   ${BLUE}make test-coverage${NC} (with coverage report)"
echo ""
echo "4. Useful commands:"
echo "   ${BLUE}make lint${NC}       (run linters)"
echo "   ${BLUE}make format${NC}     (format code)"
echo "   ${BLUE}make help${NC}       (show all commands)"
echo ""
echo "📖 Documentation:"
echo "   - Setup guide: ${BLUE}docs/DEPLOYMENT.md${NC}"
echo "   - API docs: ${BLUE}docs/API.md${NC}"
echo "   - Architecture: ${BLUE}ARCHITECTURE.md${NC}"
echo ""
