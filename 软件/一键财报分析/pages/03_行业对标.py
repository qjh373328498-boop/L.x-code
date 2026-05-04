"""
🏠 行业对标分析 - 页面 03
"""
import streamlit as st
import plotly.graph_objects as go

st.set_page_config(page_title="行业对标", page_icon="🏭", layout="wide")

st.title("🏭 行业对标分析")

if st.session_state.financial_data:
    from utils.industry import INDUSTRY_STANDARDS, detect_industry, evaluate_ratio
    from utils.ratios import calculate_profitability_ratios, calculate_solvency_ratios
    
    # 行业选择/确认
    if not st.session_state.industry:
        st.subheader("选择行业")
        industry_options = list(INDUSTRY_STANDARDS.keys())
        st.session_state.industry = st.selectbox("所属行业", industry_options)
    else:
        col1, col2 = st.columns([3, 1])
        with col1:
            st.info(f"🏭 当前行业：{st.session_state.industry}")
        with col2:
            if st.button("切换行业"):
                st.session_state.industry = None
                st.rerun()
    
    industry = st.session_state.industry
    
    # 获取财务数据
    data = st.session_state.financial_data
    income_stmt = data.get("income_stmt", {})
    balance_sheet = data.get("balance_sheet", {})
    
    # 计算各项指标
    profit_ratios = calculate_profitability_ratios({**income_stmt, **balance_sheet})
    solvency_ratios = calculate_solvency_ratios(balance_sheet)
    
    all_ratios = {**profit_ratios, **solvency_ratios}
    
    # 行业标准
    standards = INDUSTRY_STANDARDS.get(industry, {})
    
    st.markdown("---")
    st.subheader("📊 综合对比雷达图")
    
    # 构建雷达图数据
    categories = []
    company_values = []
    industry_avg = []
    industry_max = []
    
    for ratio_name, std in standards.items():
        if ratio_name in all_ratios:
            categories.append(ratio_name)
            company_values.append(all_ratios[ratio_name])
            industry_avg.append(std["avg"])
            industry_max.append(std["max"])
    
    fig = go.Figure()
    
    # 公司值
    fig.add_trace(go.Scatterpolar(
        r=company_values + [company_values[0]],
        theta=categories + [categories[0]],
        fill='toself',
        name='公司',
        line_color='#1f77b4'
    ))
    
    # 行业平均
    fig.add_trace(go.Scatterpolar(
        r=industry_avg + [industry_avg[0]],
        theta=categories + [categories[0]],
        fill='toself',
        name='行业平均',
        line_color='#ff7f0e'
    ))
    
    fig.update_layout(
        polar=dict(radialaxis=dict(visible=True, range=[0, max(industry_max)])),
        showlegend=True,
        height=600,
        title=f"{industry}财务指标雷达图"
    )
    
    st.plotly_chart(fig, use_container_width=True)
    
    st.markdown("---")
    st.subheader("📋 详细对比")
    
    # 详细对比表格
    comparison_data = []
    for ratio_name in categories:
        company_val = all_ratios.get(ratio_name, 0)
        std = standards.get(ratio_name, {})
        
        level, comment = evaluate_ratio(industry, ratio_name, company_val)
        
        comparison_data.append({
            "指标": ratio_name,
            "公司值": f"{company_val:.2f}",
            "行业最低": f"{std.get('min', 0):.2f}",
            "行业平均": f"{std.get('avg', 0):.2f}",
            "行业优秀": f"{std.get('max', 100):.2f}",
            "评价": f"{level} - {comment}",
        })
    
    st.dataframe(comparison_data, use_container_width=True, hide_index=True)
    
    st.markdown("---")
    st.subheader("💡 分析建议")
    
    # 找出劣势指标
    weak_ratios = [d for d in comparison_data if "较差" in d["评价"]]
    strong_ratios = [d for d in comparison_data if "优秀" in d["评价"]]
    
    if weak_ratios:
        st.error(f"⚠️ 需要关注的指标 ({len(weak_ratios)}项):")
        for item in weak_ratios:
            st.markdown(f"  - **{item['指标']}**: {item['公司值']} (行业平均：{item['行业平均']})")
    
    if strong_ratios:
        st.success(f"✅ 优势指标 ({len(strong_ratios)}项):")
        for item in strong_ratios:
            st.markdown(f"  - **{item['指标']}**: {item['公司值']} (优于行业平均)")
    
    if not weak_ratios and not strong_ratios:
        st.info("公司各项指标基本处于行业平均水平")

else:
    st.warning("⚠️ 请先在首页上传财报文件")
