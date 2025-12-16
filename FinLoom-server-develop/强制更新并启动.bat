@echo off
cd /d "%~dp0"
title Force Update and Start

cls
echo ========================================
echo   Force Update - Clean Everything
echo ========================================
echo.
echo This will:
echo 1. Stop all servers
echo 2. Clear browser cache folder
echo 3. Rebuild frontend with latest code
echo 4. Initialize database
echo 5. Start server
echo.
pause

echo [Step 1/5] Stopping servers...
taskkill /F /IM python.exe >nul 2>&1
timeout /t 2 /nobreak >nul
echo [OK] Servers stopped
echo.

echo [Step 2/5] Clearing old builds...
if exist "web\dist" (
    rmdir /s /q "web\dist"
    echo [OK] Old build cleared
)
echo.

echo [Step 3/5] Rebuilding frontend...
cd web-vue
call npm.cmd run build
if errorlevel 1 (
    echo [ERROR] Build failed
    cd ..
    pause
    exit /b 1
)
cd ..
echo [OK] Frontend rebuilt
echo.

echo [Step 4/5] Initializing database...
python scripts\init_sycamore_strategy.py
echo [OK] Database ready
echo.

echo [Step 5/5] Starting server...
echo ========================================
echo   IMPORTANT
echo ========================================
echo.
echo After browser opens:
echo 1. Press Ctrl+Shift+Delete
echo 2. Select "Cached images and files"
echo 3. Click "Clear data"
echo 4. Close browser
echo 5. Click this window and press Enter
echo.
pause

echo Starting server...
start http://localhost:8000
timeout /t 2 /nobreak >nul

python main.py

pause








