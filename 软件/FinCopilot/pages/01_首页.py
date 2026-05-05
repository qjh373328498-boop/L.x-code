"""
FinCopilot - 首页
"""
import streamlit as st

st.set_page_config(page_title="首页", page_icon="🏠", layout="wide")

st.title("🏠 首页")

st.markdown("""
### 欢迎使用 FinCopilot 财务实习生副驾驶

**FinCopilot** 是一款纯本地、零 API 的财务辅助工具，专为财务实习生设计。

#### 核心功能

| 功能 | 说明 |
|------|------|
| 📄 文档解析 | 上传 PDF/图片，自动提取金额、公司名、日期 |
| 🧮 金融测算 | 直线折旧、双倍余额递减法、IRR/NPV 计算 |
| 🧹 数据治理 | 文本聚类清洗，相似供应商名称合并 |
| 🛡️ 合规风控 | 报销预审、数据脱敏 |
| 🔗 关联匹配 | 银行回单与发票智能匹配 |
| 📊 报表美化 | 生成 PDF 格式报告 |

#### 技术特性

- 🔒 **纯本地运行**：所有数据不离本地
- 🚫 **零 API 依赖**：不依赖任何 AI 接口
- 💪 **硬核算法**：正则 + FuzzyWuzzy + numpy-financial
- 📊 **Streamlit 架构**：与财务工具箱、一键财报分析保持一致

#### 快速开始

1. 在左侧菜单选择功能模块
2. 上传文件或输入数据
3. 系统自动处理并显示结果

#### 默认账户

| 角色 | 用户名 | 密码 |
|------|--------|------|
| 管理员 | admin | 703102 |
| 实习生 | intern | intern123 |
""")

st.markdown("---")

st.markdown("### ⚡ 快捷入口")

col1, col2, col3 = st.columns(3)

with col1:
    st.markdown("""
    **📄 文档解析**
    
    快速提取 PDF/图片中的关键信息
    
    支持格式：PDF, PNG, JPG
    """)

with col2:
    st.markdown("""
    **🧮 金融测算**
    
    折旧计算、IRR、NPV、年金
    
    基于 numpy-financial
    """)

with col3:
    st.markdown("""
    **🔗 关联匹配**
    
    银行回单与发票勾稽
    
    智能匹配未勾稽项
    """)
