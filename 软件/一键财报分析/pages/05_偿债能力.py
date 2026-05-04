"""
💰 偿债能力分析 - 页面 05
"""
import streamlit as st
import plotly.graph_objects as go

st.set_page_config(page_title="偿债能力", page_icon="💰", layout="wide")

st.title("💰 偿债能力分析")

if st.session_state.financial_data:
    from utils.ratios import calculate_solvency_ratios
    from utils.industry import evaluate_ratio
    
    data = st.session_state.financial_data
    balance_sheet = data.get("balance_sheet", {})
    
    ratios = calculate_solvency_ratios(balance_sheet)
    
    # 核心指标
    st.subheader("核心指标")
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("流动比率", f"{ratios.get('流动比率', 0):.2f}")
    
    with col2:
        st.metric("速动比率", f"{ratios.get('速动比率', 0):.2f}")
    
    with col3:
        st.metric("资产负债率", f"{ratios.get('资产负债率', 0):.1f}%")
    
    with col4:
        st.metric("权益乘数", f"{ratios.get('权益乘数', 0):.2f}")
    
    st.markdown("---")
    
    # 指标解读
    st.subheader("📊 指标解读")
    
    # 流动比率标准值 2:1
    current_ratio = ratios.get('流动比率', 0)
    if current_ratio >= 2:
        st.success(f"✅ 流动比率 {current_ratio:.2f}：短期偿债能力强")
    elif current_ratio >= 1:
        st.warning(f"⚠️ 流动比率 {current_ratio:.2f}：短期偿债能力一般")
    else:
        st.error(f"❌ 流动比率 {current_ratio:.2f}：存在短期偿债风险")
    
    # 速动比率标准值 1:1
    quick_ratio = ratios.get('速动比率', 0)
    if quick_ratio >= 1:
        st.success(f"✅ 速动比率 {quick_ratio:.2f}：即时偿债能力强")
    elif quick_ratio >= 0.5:
        st.warning(f"⚠️ 速动比率 {quick_ratio:.2f}：需关注存货变现能力")
    else:
        st.error(f"❌ 速动比率 {quick_ratio:.2f}：即时偿债能力较弱")
    
    # 资产负债率
    debt_ratio = ratios.get('资产负债率', 0)
    if debt_ratio <= 50:
        st.success(f"✅ 资产负债率 {debt_ratio:.1f}%：财务结构稳健")
    elif debt_ratio <= 70:
        st.warning(f"⚠️ 资产负债率 {debt_ratio:.1f}%：负债水平较高")
    else:
        st.error(f"❌ 资产负债率 {debt_ratio:.1f}%：财务风险较高")
    
    st.markdown("---")
    
    # 可视化
    st.subheader("📈 负债结构")
    
    total_assets = balance_sheet.get('总资产', 0)
    total_liabilities = balance_sheet.get('总负债', 0)
    equity = total_assets - total_liabilities
    
    fig = go.Figure(data=[
        go.Pie(labels=['负债', '股东权益'], 
               values=[total_liabilities, equity],
               hole=0.4,
               marker_colors=['#ff6b6b', '#1f77b4'])
    ])
    fig.update_layout(title="资产结构（负债 vs 权益）", height=400)
    st.plotly_chart(fig, use_container_width=True)
    
    # 行业对比
    if st.session_state.industry:
        st.markdown("---")
        st.subheader(f"🏭 {st.session_state.industry}行业对比")
        
        for ratio_name in ["流动比率", "速动比率", "资产负债率"]:
            value = ratios.get(ratio_name, 0)
            if st.session_state.industry:
                level, comment = evaluate_ratio(st.session_state.industry, ratio_name, value)
                st.markdown(f"{ratio_name}: {level} - {comment}")

else:
    st.warning("⚠️ 请先在首页上传财报文件")
