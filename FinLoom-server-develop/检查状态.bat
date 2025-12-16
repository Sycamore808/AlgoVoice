@echo off
chcp 65001 >nul
cd /d "%~dp0"
title Status Check

cls
echo.
echo =========================================
echo   FinLoom Status Check
echo =========================================
echo.

echo [Check 1/5] Python
python --version 2>&1
if errorlevel 1 (
    echo [FAIL] Python not found
    set /a errors+=1
) else (
    echo [PASS]
)
echo.

echo [Check 2/5] Node.js
node --version 2>&1
if errorlevel 1 (
    echo [FAIL] Node.js not found
    set /a errors+=1
) else (
    echo [PASS]
)
echo.

echo [Check 3/5] Frontend Build
if exist "web\dist\index.html" (
    echo [PASS] Frontend built
) else (
    echo [FAIL] Frontend not built
    echo Run "首次安装.bat" first
    set /a errors+=1
)
echo.

echo [Check 4/5] Strategy Data
python -c "import sqlite3; conn = sqlite3.connect('data/finloom.db'); cursor = conn.cursor(); cursor.execute('SELECT COUNT(*) FROM paper_trading_strategies WHERE user_id=\"Sycamore1024\"'); count = cursor.fetchone()[0]; print(f'Found {count} strategy(ies)'); exit(0 if count > 0 else 1)" 2>nul
if errorlevel 1 (
    echo [FAIL] No strategy data
    set /a errors+=1
) else (
    echo [PASS]
)
echo.

echo [Check 5/5] Server Status
netstat -ano | findstr :8000 >nul 2>&1
if errorlevel 1 (
    echo [INFO] Server not running
) else (
    echo [PASS] Server is running on port 8000
)
echo.

echo =========================================
echo   Check Complete
echo =========================================
echo.
echo If all checks pass, you can run "启动.bat"
echo.
pause








