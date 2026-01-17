#!/bin/bash
# ==========================================
# Ultrabot Installation Script (Linux/macOS)
# ==========================================

set -e

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${BLUE}═══════════════════════════════════════${NC}"
echo -e "${BLUE}  🚀 ULTRABOT - УСТАНОВКА${NC}"
echo -e "${BLUE}═══════════════════════════════════════${NC}"

# 1. Check Python
echo -e "\n${BLUE}[1/6] Проверяю Python...${NC}"
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}❌ Python3 не найден!${NC}"
    echo -e "${YELLOW}Установи Python 3.11+:${NC}"
    echo -e "  macOS: brew install python@3.12"
    echo -e "  Ubuntu: sudo apt install python3.12"
    exit 1
fi

PYTHON_VERSION=$(python3 --version 2>&1 | awk '{print $2}')
echo -e "${GREEN}✓ Python $PYTHON_VERSION${NC}"

# 2. Create venv
echo -e "\n${BLUE}[2/6] Создаю виртуальное окружение...${NC}"
if [ -d "venv" ]; then
    echo -e "${YELLOW}⚠ venv уже существует, пропускаю${NC}"
else
    python3 -m venv venv
    echo -e "${GREEN}✓ venv создан${NC}"
fi

source venv/bin/activate
echo -e "${GREEN}✓ venv активирован${NC}"

# 3. Install dependencies
echo -e "\n${BLUE}[3/6] Устанавливаю зависимости...${NC}"
pip install -q --upgrade pip setuptools wheel
pip install -q -r requirements.txt
echo -e "${GREEN}✓ Зависимости установлены${NC}"

# 4. Create .env
echo -e "\n${BLUE}[4/6] Настраиваю окружение...${NC}"
if [ -f ".env" ]; then
    echo -e "${YELLOW}⚠ .env уже существует${NC}"
else
    if [ -f ".env.example" ]; then
        cp .env.example .env
        echo -e "${GREEN}✓ .env создан${NC}"
        
        echo -e "\n${YELLOW}⚠ НЕОБХОДИМО ЗАПОЛНИТЬ .env:${NC}"
        echo -e "  - TELEGRAM_TOKEN (из @BotFather)"
        echo -e "  - TELEGRAM_CHANNEL_ID (твой канал)"
        echo -e "  - YANDEX_API_KEY (API Яндекса)"
        echo -e "  - YANDEX_FOLDER_ID (Folder ID Яндекса)"
    else
        echo -e "${RED}❌ .env.example не найден${NC}"
        exit 1
    fi
fi

# 5. Docker services
echo -e "\n${BLUE}[5/6] Запускаю Docker сервисы...${NC}"
if command -v docker-compose &> /dev/null; then
    if docker-compose ps | grep -q "postgres.*Up"; then
        echo -e "${GREEN}✓ PostgreSQL уже запущен${NC}"
    else
        echo -e "${YELLOW}⚠ Запускаю PostgreSQL и Redis...${NC}"
        docker-compose up -d postgres redis
        echo -e "${GREEN}✓ Сервисы запущены${NC}"
        sleep 3
    fi
else
    echo -e "${YELLOW}⚠ Docker не найден${NC}"
    echo -e "  Установи Docker Desktop: https://www.docker.com/products/docker-desktop"
    echo -e "  Или используй локальный PostgreSQL"
fi

# 6. Database migrations
echo -e "\n${BLUE}[6/6] Инициализирую БД...${NC}"
if command -v alembic &> /dev/null; then
    cd alembic
    alembic upgrade head
    cd ..
    echo -e "${GREEN}✓ БД готова${NC}"
else
    echo -e "${YELLOW}⚠ alembic не найден (это нормально)${NC}"
fi

# Success
echo ""
echo -e "${GREEN}═══════════════════════════════════════${NC}"
echo -e "${GREEN}  ✓ УСТАНОВКА ЗАВЕРШЕНА!${NC}"
echo -e "${GREEN}═══════════════════════════════════════${NC}"
echo ""
echo -e "${BLUE}📝 СЛЕДУЮЩИЕ ШАГИ:${NC}"
echo -e "  1. Открой .env и заполни значения:"
echo -e "     nano .env"
echo -e "  2. Запусти приложение:"
echo -e "     ./run.sh       # режим production"
echo -e "     ./run.sh dev   # режим разработки"
echo -e "  3. Проверь здоровье:"
echo -e "     curl http://localhost:8000/health"
echo ""
echo -e "${BLUE}📚 ДОКУМЕНТАЦИЯ:${NC}"
echo -e "  - GETTING_STARTED.md (5 минут)"
echo -e "  - INSTALL_RU.md (подробная инструкция)"
echo -e "  - docs/DEVELOPMENT.md (разработка)"
echo ""
