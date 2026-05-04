"""
📊 快速分析视图 - 仪表盘
"""
import streamlit as st
import plotly.graph_objects as go

st.set_page_config(page_title="快速分析", page_icon="📊", layout="wide")

st.title("📊 快速分析视图")

if st.session_state.financial_data:
    from utils.ratios import (
        calculate_profitability_ratios, calculate_solvency_ratios,
        calculate_efficiency_ratios, calculate_cash_flow_ratios
    )
    
    data = st.session_state.financial_data
    income_stmt = data.get("income_stmt", {})
    balance_sheet = data.get("balance_sheet", {})
    cash_flow = data.get("cash_flow", {})
    
    # 计算所有指标
    profit_ratios = calculate_profitability_ratios({**income_stmt, **balance_sheet})
    solvency_ratios = calculate_solvency_ratios(balance_sheet)
    efficiency_ratios = calculate_efficiency_ratios(income_stmt, balance_sheet)
    cashflow_ratios = calculate_cash_flow_ratios(cash_flow, income_stmt)
    
    # 综合评分
    def calculate_score():
        score = 0
        if profit_ratios.get('ROE', 0) > 15: score += 30
        elif profit_ratios.get('ROE', 0) > 10: score += 20
        elif profit_ratios.get('ROE', 0) > 5: score += 10
        
        current_ratio = profit_ratios.get('流动比率', 0)
        if 1.5 <= current_ratio <= 2.5: score += 15
        elif current_ratio > 1: score += 8
        
        debt_ratio = solvency_ratios.get('资产负债率', 0)
        if 30 <= debt_ratio <= 60: score += 10
        elif debt_ratio <= 70: score += 5
        
        if efficiency_ratios.get('总资产周转率', 0) > 1: score += 20
        elif efficiency_ratios.get('总资产周转率', 0) > 0.5: score += 10
        
        if cashflow_ratios.get('盈利现金比率', 0) >= 1: score += 25
        elif cashflow_ratios.get('盈利现金比率', 0) >= 0.8: score += 15
        elif cashflow_ratios.get('盈利现金比率', 0) >= 0.5: score += 8
        
        return min(score, 100)
    
    score = calculate_score()
    
    # 第一行：综合评分和关键指标
    st.subheader("💯 综合评分")
    col1, col2, col3, col4, col5 = st.columns([1, 1, 1, 1, 2])
    
    with col1:
        st.metric("综合评分", f"{score}/100")
    
    with col2:
        st.metric("毛利率", f"{profit_ratios.get('毛利率', 0):.1f}%")
    
    with col3:
        st.metric("净利率", f"{profit_ratios.get('净利润率', 0):.1f}%")
    
    with col4:
        st.metric("ROE", f"{profit_ratios.get('ROE', 0):.1f}%")
    
    with col5:
        rating = "优秀" if score >= 80 else "良好" if score >= 60 else "一般" if score >= 40 else "较差"
        st.markdown(f"**评级**: {rating}")
    
    st.markdown("---")
    
    # 第二行：雷达图
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("🎯 能力雷达图")
        
        categories = ['盈利能力', '偿债能力', '运营效率', '现金流']
        values = [
            profit_ratios.get('ROE', 0),
            (1 - abs(solvency_ratios.get('流动比率', 2) - 2) / 2) * 30,  # 越接近 2 越好
            efficiency_ratios.get('总资产周转率', 0) * 30,
            cashflow_ratios.get('盈利现金比率', 0) * 25
        ]
        
        fig = go.Figure()
        fig.add_trace(go.Scatterpolar(
            r=values + [values[0]],
            theta=categories + [categories[0]],
            fill='toself',
            name='综合能力'
        ))
        fig.update_layout(
            polar=dict(radialaxis=dict(visible=True, range=[0, 30])),
            height=350,
            showlegend=False
        )
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.subheader("📊 财务结构")
        
        assets = balance_sheet.get('总资产', 0)
        liabilities = balance_sheet.get('总负债', 0)
        equity = assets - liabilities
        
        fig = go.Figure(data=[
            go.Pie(labels=['负债', '股东权益'], 
                   values=[liabilities, equity],
                   hole=0.4,
                   marker_colors=['#ff6b6b', '#1f77b4'])
        ])
        fig.update_layout(height=350, showlegend=True)
        st.plotly_chart(fig, use_container_width=True)
    
    st.markdown("---")
    
    # 第三行：现金流和关键警示
    st.subheader("💰 现金流分析")
    
    operating = cash_flow.get('经营活动现金流净额', 0)
    investing = cash_flow.get('投资活动现金流净额', 0)
    financing = cash_flow.get('筹资活动现金流净额', 0)
    
    fig = go.Figure()
    fig.add_trace(go.Bar(
        x=['经营活动', '投资活动', '筹资活动'],
        y=[operating, investing, financing],
        marker_color=['#1f77b4' if operating > 0 else '#ff6b6b', 
                      '#ff7f0e' if investing > 0 else '#ff6b6b',
                      '#2ca02c' if financing > 0 else '#ff6b6b']
    ))
    fig.update_layout(title="三大活动现金流", height=350)
    st.plotly_chart(fig, use_container_width=True)
    
    st.markdown("---")
    
    # 快速诊断
    st.subheader("⚡ 快速诊断")
    
    cols = st.columns(3)
    
    with cols[0]:
        st.markdown("### ✅ 优势")
        if profit_ratios.get('毛利率', 0) > 30:
            st.success("毛利率高于 30%")
        if profit_ratios.get('ROE', 0) > 15:
            st.success("ROE 高于 15%")
        if cashflow_ratios.get('盈利现金比率', 0) > 1:
            st.success("利润质量高")
    
    with cols[1]:
        st.markdown("### ⚠️ 关注")
        if solvency_ratios.get('流动比率', 0) < 1.5:
            st.warning("流动比率偏低")
        if solvency_ratios.get('资产负债率', 0) > 70:
            st.warning("负债率偏高")
        if efficiency_ratios.get('存货周转率', 0) < 5:
            st.warning("存货周转变慢")
    
    with cols[2]:
        st.markdown("### 🚨 风险")
        if operating < 0 and profit_ratios.get('净利润', 0) > 0:
            st.error("经营现金流为负")
        if solvency_ratios.get('流动比率', 0) < 1:
            st.error("短期偿债风险")
        if profit_ratios.get('ROE', 0) < 0:
            st.error("亏损状态")
    
else:
    st.warning("⚠️ 请先上传财报文件")
