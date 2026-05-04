@echo off
chcp 65001 >nul
title 软件启动器

echo ========================================
echo     🚀 软件启动器
echo ========================================
echo.

cd /d "%~dp0"

REM 检查是否已初始化
if not exist ".initialized" (
    echo 首次运行，正在初始化...
    echo.
    python 配置文件.py
    if errorlevel 1 (
        echo.
        echo ❌ 初始化失败
        pause
        exit /b 1
    )
)

REM 启动应用
python 启动.py

pause
