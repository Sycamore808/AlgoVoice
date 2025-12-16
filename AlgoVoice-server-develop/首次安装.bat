@echo off
chcp 65001 >nul
cd /d "%~dp0"
title FinLoom Install

cls
echo.
echo ========================================
echo   FinLoom Installation Wizard
echo ========================================
echo.
echo This will:
echo 1. Check Python and Node.js
echo 2. Install Python dependencies
echo 3. Install frontend dependencies
echo 4. Build frontend
echo 5. Initialize strategy data
echo 6. Ready to launch
echo.
echo Estimated time: 5-10 minutes
echo.
pause

REM Check Python
echo.
echo [Step 1/6] Checking Python...
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python not found
    echo Please install Python 3.8+ from https://www.python.org/
    pause
    exit /b 1
)
for /f "tokens=*" %%i in ('python --version 2^>^&1') do echo [OK] %%i

REM Check Node.js
echo.
echo [Step 2/6] Checking Node.js...
node --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Node.js not found
    echo Please install Node.js from https://nodejs.org/
    pause
    exit /b 1
)
for /f "tokens=*" %%i in ('node --version 2^>^&1') do echo [OK] Node.js %%i

REM Install Python dependencies
echo.
echo [Step 3/6] Installing Python dependencies...
pip install -r requirements.txt --quiet
if errorlevel 1 (
    echo [WARN] Some Python dependencies may have issues
) else (
    echo [OK] Python dependencies installed
)

REM Install frontend dependencies
echo.
echo [Step 4/6] Installing frontend dependencies...
cd web-vue
call npm.cmd install --legacy-peer-deps
if errorlevel 1 (
    echo [ERROR] npm install failed
    cd ..
    pause
    exit /b 1
)
echo [OK] Frontend dependencies installed
cd ..

REM Build frontend
echo.
echo [Step 5/6] Building frontend (this may take a few minutes)...
cd web-vue
call npm.cmd run build
if errorlevel 1 (
    echo [ERROR] Frontend build failed
    cd ..
    pause
    exit /b 1
)
echo [OK] Frontend built successfully
cd ..

REM Initialize strategy
echo.
echo [Step 6/6] Initializing strategy data...
python scripts\init_sycamore_strategy.py
echo [OK] Strategy data initialized

echo.
echo ========================================
echo   Installation Complete!
echo ========================================
echo.
echo Next step:
echo   Double-click "启动.bat" to start server
echo.
pause
