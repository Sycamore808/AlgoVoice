@echo off
chcp 65001 >nul 2>&1
cd /d "%~dp0\.."
title Test Wind Connection

cls
echo.
echo =========================================
echo   Test Wind Connection
echo =========================================
echo.
echo Using system Python with WindPy
echo WindPy location: F:\Conda or F:\SOFTWARE\MATLAB
echo.
echo Please ensure:
echo   1. Wind Terminal is OPEN
echo   2. Wind Terminal is LOGGED IN
echo.
echo =========================================
echo.

pause

echo.
echo Testing Wind connection...
echo.

python backtest_standalone\scripts\test_wind.py

echo.
pause

