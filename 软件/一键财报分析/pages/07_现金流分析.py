"""
📊 现金流分析 - 页面 07
"""
import streamlit as st
import plotly.graph_objects as go

st.set_page_config(page_title="现金流分析", page_icon="📊", layout="wide")

st.title("📊 现金流分析")

if st.session_state.financial_data:
    from utils.ratios import calculate_cash_flow_ratios
    from utils.industry import evaluate_ratio
    
    data = st.session_state.financial_data
    cash_flow = data.get("cash_flow", {})
    income_stmt = data.get("income_stmt", {})
    
    ratios = calculate_cash_flow_ratios(cash_flow, income_stmt)
    
    # 核心指标
    st.subheader("核心指标")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("经营现金流净额", f"{cash_flow.get('经营活动现金流净额', 0):,.0f}")
    
    with col2:
        st.metric("盈利现金比率", f"{ratios.get('盈利现金比率', 0):.2f}")
    
    with col3:
        st.metric("销售收入现金率", f"{ratios.get('销售收入现金率', 0):.2f}")
    
    st.markdown("---")
    
    # 现金流结构
    st.subheader("💰 现金流结构")
    
    operating = cash_flow.get('经营活动现金流净额', 0)
    investing = cash_flow.get('投资活动现金流净额', 0)
    financing = cash_flow.get('筹资活动现金流净额', 0)
    
    fig = go.Figure()
    fig.add_trace(go.Bar(
        x=['经营活动', '投资活动', '筹资活动'],
        y=[operating, investing, financing],
        marker_color=['#1f77b4', '#ff7f0e', '#2ca02c']
    ))
    fig.update_layout(
        title="三大活动现金流",
        height=400,
        yaxis_title="金额"
    )
    st.plotly_chart(fig, use_container_width=True)
    
    st.markdown("---")
    
    # 指标解读
    st.subheader("📊 现金流健康度分析")
    
    # 经营现金流
    if operating > 0:
        st.success(f"✅ 经营活动现金流为正 ({operating:,.0f})：主营业务造血能力强")
    else:
        st.error(f"❌ 经营活动现金流为负 ({operating:,.0f})：主营业务现金流出")
    
    # 盈利现金比率
    profit_cash_ratio = ratios.get('盈利现金比率', 0)
    if profit_cash_ratio >= 1:
        st.success(f"✅ 盈利现金比率 {profit_cash_ratio:.2f}：利润质量高，有现金支撑")
    elif profit_cash_ratio >= 0.8:
        st.warning(f"⚠️ 盈利现金比率 {profit_cash_ratio:.2f}：利润质量一般")
    else:
        st.error(f"❌ 盈利现金比率 {profit_cash_ratio:.2f}：利润质量较差，可能存在纸面富贵")
    
    # 现金流类型判断
    st.markdown("---")
    st.subheader("📋 现金流类型诊断")
    
    if operating > 0 and investing < 0 and financing > 0:
        st.info("📊 **扩张型**：经营良好，正在扩大投资，同时需要外部融资支持")
    elif operating > 0 and investing < 0 and financing < 0:
        st.success("💪 **稳健型**：经营现金流充足，靠自有资金扩张，并回报股东")
    elif operating < 0 and investing < 0 and financing > 0:
        st.warning("⚠️ **初创型**：经营尚未造血，依赖外部融资扩张，风险较高")
    elif operating < 0 and investing > 0 and financing < 0:
        st.error("🚨 **衰退型**：经营失血，处置资产，偿还债务，需警惕")
    else:
        st.info("📊 **混合型**：现金流模式较为复杂，需结合具体情况分析")
    
    # 行业对比
    if st.session_state.industry:
        st.markdown("---")
        st.subheader(f"🏭 {st.session_state.industry}行业对比")
        
        for ratio_name in ["盈利现金比率", "销售收入现金率"]:
            value = ratios.get(ratio_name, 0)
            level, comment = evaluate_ratio(st.session_state.industry, ratio_name, value)
            st.markdown(f"{ratio_name}: {level} - {comment}")

else:
    st.warning("⚠️ 请先在首页上传财报文件")
