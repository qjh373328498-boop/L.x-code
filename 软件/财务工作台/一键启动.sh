#!/bin/bash
# 财务工作台 v2.0 - 一键启动脚本 (Linux/Mac)

echo "======================================"
echo "  财务工作台 v2.0"
echo "  整合自：财务工具箱 + FinCopilot"
echo "======================================"
echo ""

# 检查 Python
if ! command -v python3 &> /dev/null; then
    echo "❌ 错误：未找到 Python3"
    echo "请先安装 Python 3.8+"
    exit 1
fi

echo "✅ Python 版本：$(python3 --version)"

# 检查依赖
echo ""
echo "📦 检查依赖..."
if ! python3 -c "import streamlit" 2>/dev/null; then
    echo "⚠️  检测到缺少依赖，正在安装..."
    pip3 install -r requirements.txt
else
    echo "✅ 依赖已安装"
fi

# 创建数据目录
if [ ! -d "data" ]; then
    echo ""
    echo "📁 创建数据目录..."
    mkdir -p data
fi

# 启动应用
echo ""
echo "🚀 启动财务工作台..."
echo "访问地址：http://localhost:8502"
echo "按 Ctrl+C 停止服务"
echo ""

python3 -m streamlit run app.py --server.port 8502 --server.address 0.0.0.0
