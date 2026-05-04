@echo off
chcp 65001 >nul
title 一键财报分析

echo ========================================
echo     📊 一键财报分析 - 启动器
echo ========================================
echo.

cd /d "%~dp0"

REM 检查虚拟环境
if not exist "venv\Scripts\activate.bat" (
    echo [1/3] 创建虚拟环境...
    python -m venv venv
    if errorlevel 1 (
        echo ❌ 创建虚拟环境失败，请检查 Python 是否安装
        pause
        exit /b 1
    )
)

echo [1/3] 激活虚拟环境...
call venv\Scripts\activate.bat

echo [2/3] 检查并安装依赖...
pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple -q

echo [3/3] 启动应用...
echo.
echo ✅ 应用启动后，浏览器将自动打开
echo 地址：http://localhost:8501
echo.
echo 按 Ctrl+C 可停止服务
echo.

streamlit run app.py --server.port 8501 --server.address 0.0.0.0

pause
