@echo off
chcp 65001 >nul
cd /d "%~dp0"

REM 检查虚拟环境
if not exist "venv" (
    echo 首次运行，正在初始化...
    python "%~dp0配置文件.py"
    if errorlevel 1 (
        pause
        exit /b 1
    )
)

REM 直接启动
python "%~dp0启动.py"
pause
