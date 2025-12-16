@echo off
chcp 65001 >nul 2>&1
cd /d "%~dp0\.."
title 运行回测（Baostock）

cls
echo.
echo =========================================
echo   运行Sycamore1024策略回测
echo   使用Baostock数据
echo =========================================
echo.
echo 将要执行：
echo   - 从baostock_data/加载数据
echo   - 运行25年回测
echo   - 生成图表
echo   - 创建报告
echo.
echo 预计时间：30分钟 - 2小时
echo.
echo =========================================
echo.

pause

echo.
echo 开始回测...
echo.

python backtest_baostock\scripts\run_backtest_baostock.py

echo.
echo =========================================
echo   结果已保存到：backtest_baostock/backtest_results/
echo =========================================
echo.
pause

