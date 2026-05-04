"""
📉 成长性分析 - 页面 08
"""
import streamlit as st
import plotly.graph_objects as go

st.set_page_config(page_title="成长性分析", page_icon="📉", layout="wide")

st.title("📉 成长性分析")

if st.session_state.financial_data:
    from utils.industry import evaluate_ratio
    
    data = st.session_state.financial_data
    income_stmt = data.get("income_stmt", {})
    balance_sheet = data.get("balance_sheet", {})
    
    # 简化版增长指标（实际应用中需要多年数据）
    st.info("💡 注：完整的增长分析需要多年财报数据，当前基于单期数据提供基础指标")
    
    # 核心规模指标
    st.subheader("核心规模指标")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("营业收入", f"{income_stmt.get('营业收入', 0):,.0f}")
    
    with col2:
        st.metric("净利润", f"{income_stmt.get('净利润', 0):,.0f}")
    
    with col3:
        st.metric("总资产", f"{balance_sheet.get('总资产', 0):,.0f}")
    
    st.markdown("---")
    
    # 利润质量分析
    st.subheader("💰 利润质量分析")
    
    net_profit = income_stmt.get('净利润', 0)
    revenue = income_stmt.get('营业收入', 0)
    
    if revenue > 0:
        net_margin = net_profit / revenue * 100
        
        if net_margin > 20:
            st.success(f"✅ 净利润率 {net_margin:.1f}%：盈利能力优秀")
        elif net_margin > 10:
            st.info(f"ℹ️ 净利润率 {net_margin:.1f}%：盈利能力良好")
        elif net_margin > 5:
            st.warning(f"⚠️ 净利润率 {net_margin:.1f}%：盈利能力一般")
        else:
            st.error(f"❌ 净利润率 {net_margin:.1f}%：盈利能力较弱")
    
    # 资产规模分析
    st.markdown("---")
    st.subheader("📊 资产结构")
    
    total_assets = balance_sheet.get('总资产', 0)
    total_liabilities = balance_sheet.get('总负债', 0)
    equity = total_assets - total_liabilities
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.metric("总资产", f"{total_assets:,.0f}")
        st.metric("总负债", f"{total_liabilities:,.0f}")
    
    with col2:
        st.metric("股东权益", f"{equity:,.0f}")
        debt_ratio = (total_liabilities / total_assets * 100) if total_assets > 0 else 0
        st.metric("资产负债率", f"{debt_ratio:.1f}%")
    
    st.markdown("---")
    
    # 可视化
    st.subheader("📈 财务结构图")
    
    fig = go.Figure(data=[
        go.Pie(
            labels=['流动资产' if balance_sheet.get('流动资产', 0) > 0 else '总资产', 
                   '非流动资产' if balance_sheet.get('固定资产', 0) > 0 else ''],
            values=[
                balance_sheet.get('流动资产', total_assets),
                balance_sheet.get('固定资产', 0)
            ],
            hole=0.4
        )
    ])
    fig.update_layout(title="资产结构", height=400)
    st.plotly_chart(fig, use_container_width=True)
    
    # 成长建议
    st.markdown("---")
    st.subheader("💡 成长建议")
    
    if st.session_state.industry:
        st.markdown(f"**{st.session_state.industry}行业成长建议**:")
        
        if st.session_state.industry == "制造业":
            st.markdown("""
            - 关注产能利用率和固定资产周转率
            - 优化存货管理，提升周转效率
            - 控制成本，提升毛利率
            """)
        elif st.session_state.industry == "科技/互联网":
            st.markdown("""
            - 保持高研发投入，维持技术领先
            - 关注用户增长和留存指标
            - 提升商业化能力，改善盈利质量
            """)
        elif st.session_state.industry == "零售业":
            st.markdown("""
            - 提升存货周转率，降低滞销风险
            - 优化门店坪效和人效
            - 发展线上渠道，提升全渠道能力
            """)
        else:
            st.markdown("""
            - 持续提升核心竞争力
            - 优化成本结构
            - 关注现金流健康度
            """)
    
    # 如需完整增长分析，提示用户上传多年数据
    st.markdown("---")
    st.info("""
    **💡 如需完整的增长分析**：
    
    请上传连续 3-5 年的财报数据，系统将自动计算：
    - 营业收入复合增长率 (CAGR)
    - 净利润复合增长率
    - 总资产增长率趋势
    - 行业增长对比分析
    """)

else:
    st.warning("⚠️ 请先在首页上传财报文件")
