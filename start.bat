@echo off

chcp 65001 >nul

:: Enable Python UTF-8 mode (fixes UnicodeEncodeError on Chinese Windows)
set PYTHONUTF8=1
set PYTHONIOENCODING=utf-8

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

    start "NMA Backend" cmd /k "title NMA Backend & set PYTHONUTF8=1 & set PYTHONIOENCODING=utf-8 & cd /d %ROOT%backend && .venv\Scripts\uvicorn app.main:app --host 0.0.0.0 --port 8000 --log-level info"

) else (

    echo Virtual env not found, trying system Python...

    start "NMA Backend" cmd /k "title NMA Backend & cd /d %ROOT%backend && if exist requirements.txt (pip install -r requirements.txt) else (pip install -e .) && uvicorn app.main:app --host 0.0.0.0 --port 8000 --log-level info"

)



timeout /t 3 /nobreak >nul



:: Frontend

echo [2/3] Starting frontend (Next.js)...

start "NMA Frontend" cmd /k "title NMA Frontend & cd /d %ROOT%frontend && npx next dev"



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
