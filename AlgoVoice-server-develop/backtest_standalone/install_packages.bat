@echo off
chcp 65001 >nul 2>&1
cd /d "%~dp0\.."
title Install Required Packages

cls
echo.
echo =========================================
echo   Install Required Packages
echo =========================================
echo.
echo This will install (if not already installed):
echo   - pandas
echo   - numpy
echo   - matplotlib
echo   - seaborn
echo.
echo Note: WindPy is already installed in your system
echo       (F:\Conda or F:\SOFTWARE\MATLAB)
echo.
echo =========================================
echo.

pause

echo.
echo Installing packages...
echo.

pip install pandas numpy matplotlib seaborn -i https://pypi.tuna.tsinghua.edu.cn/simple

if errorlevel 1 (
    echo.
    echo [WARNING] Installation had some issues
    echo Trying without mirror...
    pip install pandas numpy matplotlib seaborn
)

echo.
echo =========================================
echo   Installation Complete
echo =========================================
echo.
echo Next step: test_wind.bat
echo.
pause








