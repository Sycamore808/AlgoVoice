@echo off
cd /d "%~dp0"
title FinLoom Server

setlocal enabledelayedexpansion

cls
echo.
echo =========================================
echo   FinLoom Starting...
echo =========================================
echo.

echo [Progress] Step 1/5: Environment Check
echo [========                    ] 20%%
echo.

python --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python not found!
    echo Please install Python 3.8+ and add to PATH
    pause
    exit /b 1
)
echo [OK] Python found
echo.

echo [Progress] Step 2/5: Activating Environment
echo [============                ] 40%%
echo.

if exist ".venv\Scripts\activate.bat" (
    call .venv\Scripts\activate.bat >nul 2>&1
    echo [OK] Virtual environment activated
) else (
    echo [INFO] No virtual environment, using global Python
)
echo.

echo [Progress] Step 3/5: Initializing Data
echo [================            ] 60%%
echo.

if exist "scripts\init_sycamore_strategy.py" (
    python scripts\init_sycamore_strategy.py >nul 2>&1
    echo [OK] Strategy data ready
) else (
    echo [INFO] Strategy data already initialized
)
echo.

echo [Progress] Step 4/5: Checking Port
echo [====================        ] 80%%
echo.

REM Check if port 8000 is in use
netstat -ano | findstr :8000 | findstr LISTENING >nul 2>&1
if not errorlevel 1 (
    echo [WARN] Port 8000 is in use
    echo [INFO] Attempting to free port...
    for /f "tokens=5" %%a in ('netstat -ano ^| findstr :8000 ^| findstr LISTENING') do (
        taskkill /F /PID %%a >nul 2>&1
    )
    timeout /t 2 /nobreak >nul
)

echo [OK] Port 8000 available
echo.

echo [Progress] Step 5/5: Opening Browser
echo [========================    ] 95%%
echo.

echo =========================================
echo   Server: http://localhost:8000
echo   Account: Sycamore1024
echo   Password: admin123
echo =========================================
echo.
echo Browser will open in 8 seconds...
echo Press Ctrl+C to stop server
echo.

REM Open browser after delay
start /min cmd /c "timeout /t 8 /nobreak >nul && start http://localhost:8000"

echo [Progress] Complete!
echo [============================] 100%%
echo.
echo =========================================
echo   Server is starting...
echo =========================================
echo.

REM Start the server
python main.py

echo.
echo =========================================
echo   Server stopped
echo =========================================
echo.
pause

endlocal
