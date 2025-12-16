@echo off
chcp 65001 >nul 2>&1
cd /d "%~dp0\.."
title Run Backtest

cls
echo.
echo =========================================
echo   Run Sycamore1024 Backtest
echo =========================================
echo.
echo This will:
echo   - Load data from: wind_data/
echo   - Run 25-year backtest
echo   - Generate 4 charts
echo   - Create detailed report
echo.
echo Time needed: 30 minutes - 2 hours
echo.
echo =========================================
echo.

pause

echo.
echo Starting backtest...
echo Using system Python (F:\Conda)
echo.

python backtest_standalone\scripts\run_backtest_main.py

echo.
echo =========================================
echo   Results saved to: backtest_standalone/backtest_results/
echo =========================================
echo.
pause

