@echo off
chcp 65001 >nul
title 软件启动器

echo ========================================
echo     🚀 软件启动器 v2.0
echo ========================================
echo.

cd /d "%~dp0"

REM 检查 Python 是否安装
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ 未检测到 Python，请先安装 Python 3.8+
    echo 下载地址：https://www.python.org/downloads/
    pause
    exit /b 1
)

echo ✅ Python 已安装
echo.

REM 运行交互式启动器
python start.py

pause
