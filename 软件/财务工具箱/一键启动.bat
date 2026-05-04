@echo off
chcp 65001 >nul
title 财务工具箱 - 启动器

cd /d "%~dp0"

REM 检查 Python 是否可用
where python >nul 2>&1
if errorlevel 1 (
    where py >nul 2>&1
    if errorlevel 1 (
        echo ❌ 未找到 Python，请先安装 Python 3.8+
        echo.
        echo 下载地址：https://www.python.org/downloads/
        echo.
        echo 安装时请勾选 "Add Python to PATH"
        pause
        exit /b 1
    )
    set PYTHON_CMD=py
) else (
    set PYTHON_CMD=python
)

REM 检查虚拟环境
if not exist "venv\Scripts\python.exe" (
    echo ⚠️ 虚拟环境不存在，正在初始化...
    echo.
    %PYTHON_CMD% ..\配置文件.py
    if errorlevel 1 (
        echo.
        echo 初始化失败
        pause
        exit /b 1
    )
)

REM 启动应用
%PYTHON_CMD% ..\启动.py

pause
