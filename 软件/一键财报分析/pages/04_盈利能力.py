"""
📈 盈利能力分析 - 页面 04
"""
import streamlit as st
import plotly.graph_objects as go

st.set_page_config(page_title="盈利能力分析", page_icon="📈", layout="wide")

st.title("📈 盈利能力分析")

if st.session_state.financial_data:
    from utils.ratios import calculate_profitability_ratios
    from utils.industry import evaluate_ratio, get_industry_standard
    
    data = st.session_state.financial_data
    income_stmt = data.get("income_stmt", {})
    balance_sheet = data.get("balance_sheet", {})
    
    # 计算指标
    ratios = calculate_profitability_ratios({**income_stmt, **balance_sheet})
    
    # 核心指标展示
    st.subheader("核心指标")
    col1, col2, col3, col4, col5 = st.columns(5)
    
    with col1:
        delta = "—"
        st.metric("毛利率", f"{ratios.get('毛利率', 0):.1f}%", delta)
    
    with col2:
        st.metric("营业利润率", f"{ratios.get('营业利润率', 0):.1f}%")
    
    with col3:
        st.metric("净利润率", f"{ratios.get('净利润率', 0):.1f}%")
    
    with col4:
        st.metric("ROA", f"{ratios.get('ROA', 0):.1f}%")
    
    with col5:
        st.metric("ROE", f"{ratios.get('ROE', 0):.1f}%")
    
    st.markdown("---")
    
    # 行业对比
    if st.session_state.industry:
        st.subheader(f"🏭 {st.session_state.industry}行业对比")
        
        industry = st.session_state.industry
        indicators = ["毛利率", "净利润率", "ROE", "ROA"]
        
        chart_data = []
        for ind in indicators:
            value = ratios.get(ind, 0)
            standard = get_industry_standard(industry, ind)
            chart_data.append({
                "指标": ind,
                "公司值": value,
                "行业平均": standard["avg"],
                "行业优秀": standard["max"],
            })
        
        df = st.dataframe(chart_data, use_container_width=True, hide_index=True)
        
        # 可视化
        fig = go.Figure()
        fig.add_trace(go.Bar(
            x=[d["指标"] for d in chart_data],
            y=[d["公司值"] for d in chart_data],
            name="公司值",
            marker_color="#1f77b4"
        ))
        fig.add_trace(go.Scatter(
            x=[d["指标"] for d in chart_data],
            y=[d["行业平均"] for d in chart_data],
            name="行业平均",
            mode="lines+markers",
            line=dict(color="#ff7f0e", width=3)
        ))
        
        fig.update_layout(
            title="盈利能力指标 vs 行业平均",
            height=400,
            legend=dict(orientation="h", y=1.1)
        )
        st.plotly_chart(fig, use_container_width=True)
    
    # 指标解读
    st.subheader("📊 指标解读")
    
    for ratio_name, value in ratios.items():
        if st.session_state.industry:
            level, comment = evaluate_ratio(st.session_state.industry, ratio_name, value)
            color = {"优秀": "🟢", "良好": "🔵", "一般": "🟡", "较差": "🔴"}.get(level, "⚪")
            st.markdown(f"{color} **{ratio_name}**: {value:.1f}% - {comment}")
        else:
            st.markdown(f"⚪ **{ratio_name}**: {value:.1f}%")

else:
    st.warning("⚠️ 请先在首页上传财报文件")
