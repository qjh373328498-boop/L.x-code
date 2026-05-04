"""
🏠 首页
"""
import streamlit as st

st.set_page_config(page_title="首页", page_icon="🏠", layout="wide")

st.title("🏠 首页")

if st.session_state.financial_data:
    st.success(f"✅ 已加载：{st.session_state.uploaded_file.name}")
    
    if st.session_state.company_info.get('name'):
        st.markdown(f"**公司名称**: {st.session_state.company_info['name']}")
    
    if st.session_state.industry:
        st.markdown(f"**所属行业**: {st.session_state.industry}")
    
    data = st.session_state.financial_data
    
    # 快速数据总览
    st.markdown("---")
    st.subheader("📊 数据总览")
    
    col1, col2, col3, col4 = st.columns(4)
    
    balance_sheet = data.get("balance_sheet", {})
    income_stmt = data.get("income_stmt", {})
    cash_flow = data.get("cash_flow", {})
    
    with col1:
        st.metric("总资产", f"{balance_sheet.get('总资产', 0):,.0f}")
    
    with col2:
        st.metric("营业收入", f"{income_stmt.get('营业收入', 0):,.0f}")
    
    with col3:
        st.metric("净利润", f"{income_stmt.get('净利润', 0):,.0f}")
    
    with col4:
        st.metric("经营现金流", f"{cash_flow.get('经营活动现金流净额', 0):,.0f}")
    
    st.markdown("---")
    st.info("👈 请在左侧菜单选择分析维度")
    
else:
    st.warning("⚠️ 尚未上传财报文件")
    
    st.markdown("""
    ### 快速开始
    
    1. 点击左侧菜单的 **「📁 财报上传」**
    2. 上传 Excel 或 PDF 格式的财报文件
    3. 系统将自动解析并生成分析报告
    
    ### 支持的分析维度
    
    - 🏭 **行业对标**：与行业标准值对比
    - 📈 **盈利能力**：毛利率、净利率、ROE 等
    - 💰 **偿债能力**：流动比率、资产负债率等
    - ⚡ **运营效率**：存货周转率、应收账款周转率等
    - 📊 **现金流分析**：三大活动现金流、盈利质量
    - 📉 **成长性分析**：营收增长率、利润增长率
    - ⚠️ **风险预警**：自动识别财务风险
    - 📋 **诊断报告**：一键生成完整分析报告
    """)
