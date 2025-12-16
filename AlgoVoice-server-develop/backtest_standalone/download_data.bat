@echo off
chcp 65001 >nul 2>&1
cd /d "%~dp0\.."
title Download Wind Data

cls
echo.
echo =========================================
echo   Download Wind Data
echo =========================================
echo.
echo This will download:
echo   - 5000+ A-share stocks
echo   - 25 years history (2000-2025)
echo   - Index data
echo   - Industry classification
echo.
echo Time needed: 2-5 hours
echo Data size: 500MB - 2GB
echo.
echo =========================================
echo.
echo IMPORTANT:
echo   1. Wind Terminal must be OPEN
echo   2. Wind Terminal must be LOGGED IN
echo   3. Stable network connection
echo   4. Can resume if interrupted
echo.
echo =========================================
echo.

pause

echo.
echo Starting data download...
echo Using system Python (F:\Conda)
echo.

python backtest_standalone\scripts\download_wind_data.py

echo.
echo =========================================
echo.
pause

