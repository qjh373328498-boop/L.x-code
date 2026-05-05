@echo off
chcp 65001 >nul
title 财务工作台 v2.0

echo ======================================
echo   财务工作台 v2.0
echo   整合自：财务工具箱 + FinCopilot
echo ======================================
echo.

REM 检查 Python
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ 错误：未找到 Python
    echo 请先安装 Python 3.8+
    pause
    exit /b 1
)

for /f "tokens=*" %%i in ('python --version') do set PYTHON_VERSION=%%i
echo ✅ %PYTHON_VERSION%

REM 检查依赖
echo.
echo 📦 检查依赖...
python -c "import streamlit" 2>nul
if errorlevel 1 (
    echo ⚠️  检测到缺少依赖，正在安装...
    pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple
) else (
    echo ✅ 依赖已安装
)

REM 创建数据目录
if not exist "data" (
    echo.
    echo 📁 创建数据目录...
    mkdir data
)

REM 启动应用
echo.
echo 🚀 启动财务工作台...
echo 访问地址：http://localhost:8502
echo 按 Ctrl+C 停止服务
echo.

python -m streamlit run app.py --server.port 8502 --server.address 0.0.0.0

pause
