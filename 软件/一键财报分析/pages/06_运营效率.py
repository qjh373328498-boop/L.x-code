"""
⚡ 运营效率分析 - 页面 06
"""
import streamlit as st
import plotly.graph_objects as go

st.set_page_config(page_title="运营效率", page_icon="⚡", layout="wide")

st.title("⚡ 运营效率分析")

if st.session_state.financial_data:
    from utils.ratios import calculate_efficiency_ratios
    from utils.industry import evaluate_ratio
    
    data = st.session_state.financial_data
    income_stmt = data.get("income_stmt", {})
    balance_sheet = data.get("balance_sheet", {})
    
    ratios = calculate_efficiency_ratios(income_stmt, balance_sheet)
    
    # 核心指标
    st.subheader("核心指标")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("存货周转率", f"{ratios.get('存货周转率', 0):.2f}次")
    
    with col2:
        st.metric("应收账款周转率", f"{ratios.get('应收账款周转率', 0):.2f}次")
    
    with col3:
        st.metric("总资产周转率", f"{ratios.get('总资产周转率', 0):.2f}次")
    
    st.markdown("---")
    
    # 指标解读
    st.subheader("📊 指标解读")
    
    inventory_turnover = ratios.get('存货周转率', 0)
    if inventory_turnover > 10:
        st.success(f"✅ 存货周转率 {inventory_turnover:.2f}次：库存管理高效")
    elif inventory_turnover > 5:
        st.info(f"ℹ️ 存货周转率 {inventory_turnover:.2f}次：正常水平")
    else:
        st.warning(f"⚠️ 存货周转率 {inventory_turnover:.2f}次：需关注存货积压风险")
    
    receivables_turnover = ratios.get('应收账款周转率', 0)
    if receivables_turnover > 8:
        st.success(f"✅ 应收账款周转率 {receivables_turnover:.2f}次：回款速度快")
    elif receivables_turnover > 4:
        st.info(f"ℹ️ 应收账款周转率 {receivables_turnover:.2f}次：正常水平")
    else:
        st.warning(f"⚠️ 应收账款周转率 {receivables_turnover:.2f}次：需加强应收账款管理")
    
    asset_turnover = ratios.get('总资产周转率', 0)
    if asset_turnover > 1:
        st.success(f"✅ 总资产周转率 {asset_turnover:.2f}次：资产利用效率高")
    elif asset_turnover > 0.5:
        st.info(f"ℹ️ 总资产周转率 {asset_turnover:.2f}次：正常水平")
    else:
        st.warning(f"⚠️ 总资产周转率 {asset_turnover:.2f}次：资产利用效率偏低")
    
    st.markdown("---")
    
    # 可视化
    st.subheader("📈 周转率对比")
    
    if st.session_state.industry:
        from utils.industry import get_industry_standard
        
        indicators = ["存货周转率", "应收账款周转率", "总资产周转率"]
        
        company_values = [ratios.get(ind, 0) for ind in indicators]
        industry_avg = [get_industry_standard(st.session_state.industry, ind)["avg"] for ind in indicators]
        
        fig = go.Figure()
        fig.add_trace(go.Bar(
            x=indicators,
            y=company_values,
            name="公司",
            marker_color="#1f77b4"
        ))
        fig.add_trace(go.Bar(
            x=indicators,
            y=industry_avg,
            name="行业平均",
            marker_color="#ff7f0e"
        ))
        
        fig.update_layout(
            title="运营效率指标对比",
            height=400,
            barmode='group'
        )
        st.plotly_chart(fig, use_container_width=True)
    
    # 详细分析
    st.markdown("---")
    st.subheader("💡 管理建议")
    
    if st.session_state.industry:
        for ratio_name in indicators:
            value = ratios.get(ratio_name, 0)
            level, comment = evaluate_ratio(st.session_state.industry, ratio_name, value)
            if level in ["较差", "一般"]:
                st.markdown(f"**{ratio_name}** - {comment}")

else:
    st.warning("⚠️ 请先在首页上传财报文件")
