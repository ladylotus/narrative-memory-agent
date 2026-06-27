@echo off
chcp 65001 >nul
title Narrative Memory Agent

echo ==========================================
echo   Narrative Memory Agent - Yn starts
echo ==========================================
echo.

:: Check dependencies
where python >nul 2>nul
if %errorlevel% neq 0 (
    echo Python not found. Install Python 3.11+ first.
    pause
    exit /b 1
)

where node >nul 2>nul
if %errorlevel% neq 0 (
    echo Node.js not found. Install Node.js 18+ first.
    pause
    exit /b 1
)

set ROOT=%~dp0

:: Backend
echo [1/3] Starting backend (FastAPI)...
if exist "%ROOT%backend\.venv\Scripts\uvicorn.exe" (
    start "NMA Backend" cmd /c "title NMA Backend & cd /d %ROOT%backend && .venv\Scripts\uvicorn app.main:app --host 0.0.0.0 --port 8000 --log-level info"
) else (
    echo Virtual env not found, trying system Python...
    start "NMA Backend" cmd /c "title NMA Backend & cd /d %ROOT%backend && pip install -r requirements.txt 2>nul & uvicorn app.main:app --host 0.0.0.0 --port 8000 --log-level info"
)

timeout /t 3 /nobreak >nul

:: Frontend
echo [2/3] Starting frontend (Next.js)...
start "NMA Frontend" cmd /c "title NMA Frontend & cd /d %ROOT%frontend && npm install 2>nul & npm run dev"

timeout /t 5 /nobreak >nul

:: Open browser
echo [3/3] Opening browser...
start http://localhost:3000

echo.
echo NMA is running!
echo   Backend  - http://localhost:8000
echo   Frontend - http://localhost:3000
echo.
echo Close the terminal windows to stop the services.
echo.
pause
