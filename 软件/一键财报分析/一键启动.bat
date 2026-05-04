@echo off
chcp 65001 >nul
title 一键财报分析

echo ========================================
echo     📊 一键财报分析 - 启动器
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

echo [1/3] 检查虚拟环境...

REM 检查虚拟环境
if not exist "venv\Scripts\activate.bat" (
    echo [1/3] 创建虚拟环境...
    python -m venv venv
    if errorlevel 1 (
        echo ❌ 创建虚拟环境失败
        pause
        exit /b 1
    )
    echo ✅ 虚拟环境创建成功
) else (
    echo ✅ 虚拟环境已存在
)

echo.
echo [2/3] 激活虚拟环境...
call venv\Scripts\activate.bat

echo.
echo [3/3] 安装依赖（使用清华镜像源）...
pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple -q
if errorlevel 1 (
    echo ⚠️  依赖安装可能有警告，继续启动...
)

echo.
echo ========================================
echo     ✅ 准备启动
echo ========================================
echo.
echo  应用地址：http://localhost:8501
echo  按 Ctrl+C 可停止服务
echo.

streamlit run app.py --server.port 8501 --server.address 0.0.0.0

pause
