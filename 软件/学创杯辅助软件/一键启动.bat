@echo off
chcp 65001 >nul
cd /d "%~dp0"

if not exist ".initialized" (
    echo 首次运行，正在初始化...
    python 配置文件.py
    if errorlevel 1 (
        pause
        exit /b 1
    )
)

python 启动.py
pause
