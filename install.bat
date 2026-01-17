@echo off
REM Ultrabot - Quick Start Script for Windows

setlocal enabledelayedexpansion

echo.
echo ========================================
echo Ultrabot - Gaming News Aggregator
echo ========================================
echo.

REM Check Python version
echo [*] Checking Python version...
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python not found! Please install Python 3.11+
    echo Download from: https://www.python.org/downloads/
    pause
    exit /b 1
)

for /f "tokens=2" %%i in ('python --version 2^>^&1') do set PYTHON_VERSION=%%i
echo [OK] Found Python %PYTHON_VERSION%
echo.

REM Check if .env exists
echo [*] Checking configuration...
if not exist ".env" (
    echo [WARNING] .env file not found
    echo [*] Creating from .env.example...
    copy .env.example .env >nul
    echo [OK] Created .env file
    echo.
    echo [WARNING] Please edit .env with your credentials!
    echo.
    set /p edit="Edit .env now? (y/n): "
    if /i "!edit!"=="y" (
        notepad .env
    )
) else (
    echo [OK] .env file found
    echo.
)

REM Create virtual environment
echo [*] Setting up virtual environment...
if not exist "venv" (
    echo [*] Creating virtual environment...
    python -m venv venv
)

call venv\Scripts\activate.bat

REM Install dependencies
echo [*] Installing dependencies...
echo [*] Upgrading pip...
python -m pip install --quiet --upgrade pip setuptools wheel >nul 2>&1

echo [*] Installing Python packages...
pip install --quiet -r requirements.txt >nul 2>&1

if errorlevel 1 (
    echo [ERROR] Failed to install dependencies
    echo Please run: pip install -r requirements.txt
    pause
    exit /b 1
)

echo [OK] Dependencies installed
echo.

REM Docker check
echo [*] Checking Docker...
docker --version >nul 2>&1
if errorlevel 1 (
    echo [WARNING] Docker not found - running without services
    echo Download from: https://www.docker.com/products/docker-desktop
) else (
    echo [*] Starting Docker services...
    docker-compose up -d >nul 2>&1
    echo [OK] Docker services started
    echo [*] Waiting for services...
    timeout /t 5 /nobreak >nul
)

echo.
echo [OK] Setup complete!
echo.
echo Next steps:
echo.
echo 1. Virtual environment is ready (activated)
echo.
echo 2. Run the application:
echo    make run       (production mode)
echo    make run-dev   (development with auto-reload)
echo.
echo 3. Run tests:
echo    make test      (all tests)
echo    make test-cov  (with coverage report)
echo.
echo 4. Useful commands:
echo    make lint      (run linters)
echo    make format    (format code)
echo    make help      (show all commands)
echo.
echo Documentation:
echo    - Setup guide: docs\DEPLOYMENT.md
echo    - API docs: docs\API.md
echo    - Architecture: ARCHITECTURE.md
echo.

pause
