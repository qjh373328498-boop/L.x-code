#!/bin/bash
# 财务工作台启动脚本

echo "🚀 启动财务工作台 v2.0..."

# 检查依赖
echo "📦 检查依赖..."
pip install -q -r requirements.txt 2>/dev/null

# 启动应用
echo "✨ 启动 Streamlit 应用..."
streamlit run app.py
