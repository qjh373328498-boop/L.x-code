"""
一键财报分析 - 主应用
"""
import streamlit as st
import pandas as pd
import os

# 页面配置
st.set_page_config(
    page_title="一键财报分析",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 缓存优化，减少警告
@st.cache_data
def get_placeholder():
    return None

get_placeholder()

# 自定义 CSS
st.markdown("""
<style>
.metric-card {
    background-color: #f0f2f6;
    border-radius: 10px;
    padding: 20px;
    margin: 10px 0;
}
.metric-label {
    font-size: 14px;
    color: #666;
}
.metric-value {
    font-size: 28px;
    font-weight: bold;
    color: #1f77b4;
}
</style>
""", unsafe_allow_html=True)

# Session State 初始化
if 'uploaded_file' not in st.session_state:
    st.session_state.uploaded_file = None
if 'financial_data' not in st.session_state:
    st.session_state.financial_data = None
if 'company_info' not in st.session_state:
    st.session_state.company_info = {}
if 'industry' not in st.session_state:
    st.session_state.industry = None

# 侧边栏
st.sidebar.title("📊 一键财报分析")
st.sidebar.markdown("---")

# 检查是否有上传文件
has_file = st.session_state.uploaded_file is not None

menu = st.sidebar.radio(
    "导航",
    [
        "🏠 首页",
        "📁 财报上传",
        "🏭 行业对标",
        "📈 盈利能力",
        "💰 偿债能力",
        "⚡ 运营效率",
        "📊 现金流分析",
        "📉 成长性分析",
        "⚠️ 风险预警",
        "📋 诊断报告",
    ] if has_file else ["🏠 首页", "📁 财报上传"],
    index=0
)

st.sidebar.markdown("---")
st.sidebar.info("""
**支持格式**：
- Excel (.xlsx, .xls)
- PDF (.pdf)

**行业标准**：
内置 8 大行业标准值
""")

# 主内容区
if menu == "🏠 首页":
    st.title("📊 一键财报分析系统")
    
    st.markdown("""
    ### 功能亮点
    - ✅ **智能解析**：自动提取财报关键数据
    - ✅ **行业对标**：8 大行业标准值对比
    - ✅ **六大维度**：全面分析企业财务状况
    - ✅ **风险预警**：自动识别财务异常信号
    - ✅ **一键报告**：生成专业分析报告
    
    ### 支持行业
    | 制造业 | 科技/互联网 | 零售业 | 房地产 |
    |--------|-------------|--------|--------|
    | 金融业 | 服务业 | 医药行业 | 消费品 |
    
    ### 快速开始
    1. 在左侧菜单选择「📁 财报上传」
    2. 上传 Excel 或 PDF 格式的财报
    3. 系统自动解析并生成分析报告
    """)
    
    st.markdown("---")
    
    # 显示上传状态
    if st.session_state.uploaded_file:
        st.success(f"✅ 已加载：{st.session_state.uploaded_file.name}")
        if st.session_state.industry:
            st.info(f"🏭 识别行业：{st.session_state.industry}")
    else:
        st.warning("⚠️ 请先上传财报文件")

elif menu == "📁 财报上传":
    from utils.parser import parse_financial_report
    from utils.industry import detect_industry
    
    st.title("📁 财报上传与解析")
    
    uploaded_file = st.file_uploader(
        "上传财报文件",
        type=["xlsx", "xls", "pdf"],
        help="支持 Excel 和 PDF 格式"
    )
    
    company_name = st.text_input("公司名称（可选）", placeholder="用于行业识别")
    
    if uploaded_file and st.button("开始解析", type="primary"):
        with st.spinner("正在解析财报..."):
            try:
                # 保存到临时文件
                import tempfile
                temp_dir = tempfile.gettempdir()
                filepath = os.path.join(temp_dir, uploaded_file.name)
                with open(filepath, "wb") as f:
                    f.write(uploaded_file.getbuffer())
                
                # 解析财报
                data = parse_financial_report(filepath)
                
                st.session_state.uploaded_file = uploaded_file
                st.session_state.financial_data = data
                st.session_state.company_info["name"] = company_name
                
                # 行业识别
                if company_name:
                    st.session_state.industry = detect_industry(company_name)
                
                st.success("✅ 解析成功！")
                st.rerun()
                
            except Exception as e:
                st.error(f"❌ 解析失败：{str(e)}")
    
    # 显示解析结果预览
    if st.session_state.financial_data:
        st.markdown("### 📊 数据预览")
        col1, col2, col3 = st.columns(3)
        
        if "balance_sheet" in st.session_state.financial_data:
            with col1:
                st.metric("总资产", f"{st.session_state.financial_data['balance_sheet'].get('总资产', 0):,.0f}")
        
        if "income_stmt" in st.session_state.financial_data:
            with col2:
                st.metric("营业收入", f"{st.session_state.financial_data['income_stmt'].get('营业收入', 0):,.0f}")
            
            with col3:
                st.metric("净利润", f"{st.session_state.financial_data['income_stmt'].get('净利润', 0):,.0f}")

# 其他页面将在后续文件中实现
st.sidebar.markdown("### 关于")
st.sidebar.markdown("""
版本：v1.0
开发日期：2026-05
""")
