#!/bin/bash
# 一键财报分析 - Linux/Mac 启动脚本

echo "========================================"
echo     📊 一键财报分析 - 启动器
echo "========================================"
echo

cd "$(dirname "$0")"

# 检查 Python
if ! command -v python3 &> /dev/null; then
    echo "❌ 未检测到 Python3，请先安装"
    exit 1
fi

echo "[1/3] 检查虚拟环境..."

if [ ! -d "venv" ]; then
    echo "[1/3] 创建虚拟环境..."
    python3 -m venv venv
    if [ $? -ne 0 ]; then
        echo "❌ 创建虚拟环境失败"
        exit 1
    fi
    echo "✅ 虚拟环境创建成功"
else
    echo "✅ 虚拟环境已存在"
fi

echo
echo "[2/3] 激活虚拟环境..."
source venv/bin/activate

echo
echo "[3/3] 安装依赖..."
pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple -q

echo
echo "========================================"
echo     ✅ 准备启动
echo "========================================"
echo
echo  应用地址：http://localhost:8501
echo  按 Ctrl+C 可停止服务
echo

streamlit run app.py --server.port 8501 --server.address 0.0.0.0
