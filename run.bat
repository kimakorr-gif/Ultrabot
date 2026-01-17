@echo off
REM run.bat - Quick run script for Ultrabot on Windows

setlocal enabledelayedexpansion

cls
echo.
echo ========================================
echo Ultrabot - Gaming News Aggregator
echo ========================================
echo.

REM Check if venv exists
if not exist "venv" (
    echo [ERROR] Virtual environment not found!
    echo.
    echo Please run setup first:
    echo   install.bat  (automatic setup)
    echo   or
    echo   make setup   (with Makefile)
    echo.
    pause
    exit /b 1
)

REM Activate venv
call venv\Scripts\activate.bat

REM Check if .env exists
if not exist ".env" (
    echo [ERROR] .env file not found!
    echo.
    echo Please create .env file:
    echo   copy .env.example .env
    echo   notepad .env  (edit with your credentials)
    echo.
    pause
    exit /b 1
)

REM Check Docker
echo Checking Docker services...
docker --version >nul 2>&1
if errorlevel 1 (
    echo [WARNING] Docker not installed
    echo   Services not started (continue anyway)
) else (
    REM Check if containers are running
    docker ps | find "postgres" >nul
    if errorlevel 1 (
        echo Starting Docker services...
        docker-compose up -d >nul 2>&1
        timeout /t 3 /nobreak >nul
    )
)

echo.

REM Determine mode
set MODE=%1
if "%MODE%"=="" set MODE=production
if "%MODE%"=="dev" goto dev
if "%MODE%"=="development" goto dev
if "%MODE%"=="watch" goto dev

REM Production mode
echo [OK] Starting in PRODUCTION mode
echo.
echo Endpoints:
echo   API: http://localhost:8000
echo   Metrics: http://localhost:8000/metrics
echo   Health: http://localhost:8000/health
echo.
echo Press Ctrl+C to stop
echo.
python -m src.main
goto end

:dev
REM Development mode
echo [OK] Starting in DEVELOPMENT mode (auto-reload)
echo.
echo Endpoints:
echo   API: http://localhost:8000
echo   Metrics: http://localhost:8000/metrics
echo   Health: http://localhost:8000/health
echo.
echo Press Ctrl+C to stop
echo.
python -m uvicorn src.main:app --reload --host 0.0.0.0 --port 8000 --log-level info

:end
pause
