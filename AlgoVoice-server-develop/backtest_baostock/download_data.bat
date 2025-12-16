@echo off
chcp 65001 >nul 2>&1
cd /d "%~dp0\.."
title 下载Baostock数据

cls
echo.
echo =========================================
echo   下载Baostock数据（免费！）
echo =========================================
echo.
echo 特点：
echo   √ 完全免费
echo   √ 无需登录
echo   √ 无API限制
echo   √ 随时可下载
echo.
echo 将要下载：
echo   - 5000+只A股股票
echo   - 25年历史数据（2000-2025）
echo   - 指数数据
echo.
echo 预计时间：3-6小时
echo 数据大小：500MB - 2GB
echo.
echo =========================================
echo.

pause

echo.
echo 开始下载...
echo.

python backtest_baostock\scripts\download_baostock_data.py

echo.
echo =========================================
echo.
pause

