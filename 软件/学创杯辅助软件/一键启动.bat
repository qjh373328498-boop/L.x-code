@echo off
chcp 65001 >nul
title 学创杯辅助软件

echo ========================================
echo     🏆 学创杯辅助软件 v2.2
echo ========================================
echo.

cd /d "%~dp0"

if not exist "venv\Scripts\activate.bat" (
    echo [1/3] 创建虚拟环境...
    python -m venv venv
)

echo [1/3] 激活虚拟环境...
call venv\Scripts\activate.bat

echo [2/3] 检查依赖...
pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple -q

echo [3/3] 启动应用...
echo.
echo ✅ 地址：http://localhost:8501
echo 按 Ctrl+C 停止
echo.

streamlit run app.py --server.port 8501 --server.address 0.0.0.0

pause
