@echo off
chcp 65001 >nul
cd /d "%~dp0"

echo.
echo ╔════════════════════════════════════════╗
echo ║           财务工具箱 v1.5              ║
echo ╚════════════════════════════════════════╝
echo.

REM 检查虚拟环境
if not exist "venv" (
    echo [首次运行] 正在创建虚拟环境...
    python -m venv venv
    echo [安装依赖] 正在安装依赖包...
    venv\Scripts\pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple
)

echo [启动服务] 正在启动 Streamlit 服务器...
start /min cmd /c "venv\Scripts\streamlit run app.py --server.headless true"
echo.
echo 等待服务器启动...
timeout /t 5 /nobreak >nul
echo.
echo ═══ 请选择访问方式 ═══
echo   [1] 本机访问      （仅限当前电脑使用）
echo   [2] 局域网访问    （同一 WiFi 下的手机/平板可访问）
echo   [3] 公网访问      （任何地方都能访问）
echo ════════════════════════
echo.
set /p choice="请输入选项 (1-3，默认 1): "
if "%choice%"=="" set choice=1
if "%choice%"=="1" (
    echo 正在打开本机访问地址...
    start http://localhost:8501
) else if "%choice%"=="2" (
    echo 正在获取本机 IP 地址...
    for /f "tokens=2 delims=:" %%a in ('ipconfig ^| findstr /c:"IPv4"') do (
        set "ip=%%a"
        goto :found_ip
    )
    :found_ip
    echo 您的 IP 地址：%ip%
    start http://192.168.1.11:8501
) else if "%choice%"=="3" (
    echo 正在打开公网访问地址...
    start http://123.88.241.90:8501
) else (
    echo 无效选项，默认使用本机访问
    start http://localhost:8501
)
echo.
echo ✓ 已打开浏览器
echo   按 Ctrl+C 停止服务
echo ═══════════════════════════════════
echo.

pause
