"""
FinCopilot - 杜邦分析页面
完整的杜邦分析法可视化
"""
import streamlit as st
import plotly.graph_objects as go
import pandas as pd

st.set_page_config(page_title="杜邦分析", page_icon="📊", layout="wide")

st.title("📊 杜邦分析")

st.markdown("""
**杜邦分析法**：通过分解 ROE（净资产收益率）来分析企业的盈利能力、运营效率和财务杠杆
""")

# 数据输入
st.subheader("📝 输入财务数据")

col1, col2, col3 = st.columns(3)

with col1:
    st.markdown("**利润表数据**")
    revenue = st.number_input("营业收入", min_value=0.0, value=1000000.0)
    net_profit = st.number_input("净利润", min_value=0.0, value=150000.0)

with col2:
    st.markdown("**资产负债表数据**")
    total_assets = st.number_input("总资产", min_value=0.0, value=2000000.0)
    total_equity = st.number_input("股东权益", min_value=0.0, value=800000.0)

with col3:
    st.markdown("**其他数据**")
    total_debt = st.number_input("总负债", min_value=0.0, value=1200000.0)

# 计算
if st.button("开始分析", type="primary"):
    # 1. ROE（净资产收益率）
    roe = net_profit / total_equity if total_equity > 0 else 0
    
    # 2. 净利率
    net_margin = net_profit / revenue if revenue > 0 else 0
    
    # 3. 总资产周转率
    asset_turnover = revenue / total_assets if total_assets > 0 else 0
    
    # 4. 权益乘数
    equity_multiplier = total_assets / total_equity if total_equity > 0 else 0
    
    # 验证：ROE = 净利率 × 总资产周转率 × 权益乘数
    roe_check = net_margin * asset_turnover * equity_multiplier
    
    st.markdown("---")
    
    # 显示结果
    st.subheader("📊 分析结果")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("ROE (净资产收益率)", f"{roe*100:.2f}%")
    with col2:
        st.metric("净利率", f"{net_margin*100:.2f}%")
    with col3:
        st.metric("总资产周转率", f"{asset_turnover:.2f}")
    
    col4, col5 = st.columns(2)
    
    with col4:
        st.metric("权益乘数", f"{equity_multiplier:.2f}")
    with col5:
        st.metric("验证 ROE", f"{roe_check*100:.2f}%")
    
    # 杜邦分析树状图
    st.markdown("### 🌳 杜邦分析结构图")
    
    fig = go.Figure()
    
    # ROE
    fig.add_trace(go.Scatter(
        x=[0.5], y=[1],
        mode='markers+text',
        marker=dict(size=50, color='#1f77b4'),
        text=[f'ROE: {roe*100:.2f}%'],
        textposition='top center',
        name='ROE'
    ))
    
    # 净利率
    fig.add_trace(go.Scatter(
        x=[0.2], y=[0.7],
        mode='markers+text',
        marker=dict(size=30, color='#ff7f0e'),
        text=[f'净利率：{net_margin*100:.2f}%'],
        textposition='top center',
        name='净利率'
    ))
    
    # 总资产周转率
    fig.add_trace(go.Scatter(
        x=[0.5], y=[0.7],
        mode='markers+text',
        marker=dict(size=30, color='#2ca02c'),
        text=[f'总资产周转率：{asset_turnover:.2f}'],
        textposition='top center',
        name='总资产周转率'
    ))
    
    # 权益乘数
    fig.add_trace(go.Scatter(
        x=[0.8], y=[0.7],
        mode='markers+text',
        marker=dict(size=30, color='#d62728'),
        text=[f'权益乘数：{equity_multiplier:.2f}'],
        textposition='top center',
        name='权益乘数'
    ))
    
    fig.update_layout(
        title='杜邦分析结构图',
        xaxis=dict(showgrid=False, zeroline=False, showticklabels=False, range=[0, 1]),
        yaxis=dict(showgrid=False, zeroline=False, showticklabels=False, range=[0, 1.2]),
        showlegend=False,
        height=400
    )
    
    st.plotly_chart(fig, use_container_width=True)
    
    # 分析总结
    st.markdown("### 📋 分析总结")
    
    analysis = []
    
    # ROE 分析
    if roe > 0.15:
        analysis.append("✅ ROE 高于 15%，盈利能力优秀")
    elif roe > 0.08:
        analysis.append("✅ ROE 处于合理水平")
    else:
        analysis.append("⚠️ ROE 较低，需提升盈利能力")
    
    # 净利率分析
    if net_margin > 0.2:
        analysis.append("✅ 净利率高，产品竞争力强")
    elif net_margin > 0.1:
        analysis.append("✅ 净利率处于行业平均水平")
    else:
        analysis.append("⚠️ 净利率较低，建议控制成本")
    
    # 周转率分析
    if asset_turnover > 1.0:
        analysis.append("✅ 资产周转快，运营效率高")
    elif asset_turnover > 0.5:
        analysis.append("✅ 资产周转正常")
    else:
        analysis.append("⚠️ 资产周转慢，可能存在闲置资产")
    
    # 权益乘数分析
    if equity_multiplier > 3:
        analysis.append("⚠️ 财务杠杆较高，注意偿债风险")
    elif equity_multiplier > 2:
        analysis.append("✅ 财务杠杆合理")
    else:
        analysis.append("💡 财务杠杆较低，可适当增加负债")
    
    for item in analysis:
        st.markdown(item)

st.markdown("---")

st.info("""
💡 **杜邦分析公式**

ROE = 净利率 × 总资产周转率 × 权益乘数

其中：
- **净利率** = 净利润 ÷ 营业收入（反映盈利能力）
- **总资产周转率** = 营业收入 ÷ 总资产（反映运营效率）
- **权益乘数** = 总资产 ÷ 股东权益（反映财务杠杆）

**分析要点**：
1. ROE 是核心指标，反映股东回报
2. 净利率高说明产品竞争力强
3. 周转率快说明运营效率高
4. 权益乘数适当可以提升 ROE，但过高会增加风险
""")
