@echo off
chcp 65001 >nul 2>&1
cd /d "%~dp0\.."
title 安装Baostock

cls
echo.
echo =========================================
echo   安装Baostock（免费数据源）
echo =========================================
echo.
echo 将要安装：
echo   - baostock（免费A股数据API）
echo   - pandas, numpy
echo   - matplotlib, seaborn
echo.
echo 特点：
echo   √ 完全免费
echo   √ 无需登录
echo   √ 无API限制
echo.
echo =========================================
echo.

pause

echo.
echo 正在安装依赖包...
echo.

pip install baostock pandas numpy matplotlib seaborn -i https://pypi.tuna.tsinghua.edu.cn/simple

if errorlevel 1 (
    echo.
    echo [警告] 镜像源失败，尝试官方源...
    pip install baostock pandas numpy matplotlib seaborn
)

echo.
echo =========================================
echo   安装完成！
echo =========================================
echo.
echo Baostock特点：
echo   - 免费A股数据
echo   - 无需登录
echo   - 无API限制
echo   - 简单易用
echo.
echo 下一步：运行 download_data.bat
echo.
pause

