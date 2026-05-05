"""
📊 财务比率分析 - 偿债、盈利、营运能力分析
"""
import streamlit as st
import pandas as pd

# ========== 性能优化 ==========
# Session State: 保存用户输入
if '_session_init' not in st.session_state:
    st.session_state._session_init = True

from utils.database import get_connection, init_db
from utils.formatters import format_currency

st.set_page_config(page_title="财务比率分析", page_icon="📊", layout="wide")
init_db()

st.title("📊 财务比率分析")

tab1, tab2, tab3 = st.tabs(["数据录入", "比率分析", "行业对比"])

with tab1:
    st.subheader("录入财务数据")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        period = st.text_input("期间", placeholder="2024-12")
        current_assets = st.number_input("流动资产", value=0.0)
        non_current_assets = st.number_input("非流动资产", value=0.0)
        total_assets = st.number_input("资产总计", value=0.0)
    
    with col2:
        current_liabilities = st.number_input("流动负债", value=0.0)
        non_current_liabilities = st.number_input("非流动负债", value=0.0)
        total_liabilities = st.number_input("负债总计", value=0.0)
        equity = st.number_input("所有者权益", value=0.0)
    
    with col3:
        revenue = st.number_input("营业收入", value=0.0)
        net_profit = st.number_input("净利润", value=0.0)
        cogs = st.number_input("营业成本", value=0.0)
        inventory = st.number_input("存货", value=0.0)
        receivables = st.number_input("应收账款", value=0.0)
    
    if st.button("保存数据", type="primary"):
        if period and total_assets > 0:
            conn = get_connection()
            metrics = [
                (period, '流动资产', current_assets, '元'),
                (period, '非流动资产', non_current_assets, '元'),
                (period, '资产总计', total_assets, '元'),
                (period, '流动负债', current_liabilities, '元'),
                (period, '非流动负债', non_current_liabilities, '元'),
                (period, '负债总计', total_liabilities, '元'),
                (period, '所有者权益', equity, '元'),
                (period, '营业收入', revenue, '元'),
                (period, '净利润', net_profit, '元'),
                (period, '营业成本', cogs, '元'),
                (period, '存货', inventory, '元'),
                (period, '应收账款', receivables, '元'),
            ]
            for m in metrics:
                conn.execute(
                    """INSERT OR REPLACE INTO financial_metrics (period, metric_name, value, unit)
                       VALUES (?, ?, ?, ?)""", m
                )
            conn.commit()
            conn.close()
            st.success("数据保存成功")

with tab2:
    st.subheader("财务比率计算")
    
    conn = get_connection()
    df_all = pd.read_sql_query("SELECT * FROM financial_metrics ORDER BY period DESC", conn)
    conn.close()
    
    if df_all.empty:
        st.info("暂无数据")
        st.stop()
    
    latest_period = df_all['period'].max()
    df = df_all[df_all['period'] == latest_period]
    
    m = dict(zip(df['metric_name'], df['value']))
    
    current_assets = m.get('流动资产', 0)
    current_liabilities = m.get('流动负债', 0)
    total_assets = m.get('资产总计', 0)
    total_liabilities = m.get('负债总计', 0)
    equity = m.get('所有者权益', 0)
    revenue = m.get('营业收入', 0)
    net_profit = m.get('净利润', 0)
    cogs = m.get('营业成本', 0)
    inventory = m.get('存货', 0)
    receivables = m.get('应收账款', 0)
    
    # 偿债能力
    current_ratio = current_assets / current_liabilities if current_liabilities > 0 else 0
    quick_ratio = (current_assets - inventory) / current_liabilities if current_liabilities > 0 else 0
    debt_ratio = total_liabilities / total_assets * 100 if total_assets > 0 else 0
    equity_ratio = equity / total_assets * 100 if total_assets > 0 else 0
    
    # 盈利能力
    gross_margin = (revenue - cogs) / revenue * 100 if revenue > 0 else 0
    net_margin = net_profit / revenue * 100 if revenue > 0 else 0
    roa = net_profit / total_assets * 100 if total_assets > 0 else 0
    roe = net_profit / equity * 100 if equity > 0 else 0
    
    # 营运能力
    inventory_turnover = cogs / inventory if inventory > 0 else 0
    receivables_turnover = revenue / receivables if receivables > 0 else 0
    asset_turnover = revenue / total_assets if total_assets > 0 else 0
    
    st.subheader("💧 偿债能力")
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("流动比率", f"{current_ratio:.2f}", "标准值：2.0")
    col2.metric("速动比率", f"{quick_ratio:.2f}", "标准值：1.0")
    col3.metric("资产负债率", f"{debt_ratio:.1f}%", "标准值：<60%")
    col4.metric("权益比率", f"{equity_ratio:.1f}%", "标准值：>40%")
    
    st.divider()
    
    st.subheader("💰 盈利能力")
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("毛利率", f"{gross_margin:.1f}%")
    col2.metric("净利率", f"{net_margin:.1f}%")
    col3.metric("ROA", f"{roa:.1f}%")
    col4.metric("ROE", f"{roe:.1f}%")
    
    st.divider()
    
    st.subheader("🔄 营运能力")
    col1, col2, col3 = st.columns(3)
    col1.metric("存货周转率", f"{inventory_turnover:.2f}次")
    col2.metric("应收账款周转率", f"{receivables_turnover:.2f}次")
    col3.metric("总资产周转率", f"{asset_turnover:.2f}次")

with tab3:
    st.subheader("行业对比分析")
    
    st.info("行业平均数据（参考制造业）")
    
    industry_avg = {
        '流动比率': 1.8,
        '速动比率': 1.0,
        '资产负债率': 50.0,
        '毛利率': 25.0,
        '净利率': 8.0,
        'ROE': 12.0,
        '存货周转率': 4.0,
        '应收账款周转率': 8.0,
    }
    
    company_values = {
        '流动比率': current_ratio,
        '速动比率': quick_ratio,
        '资产负债率': debt_ratio,
        '毛利率': gross_margin,
        '净利率': net_margin,
        'ROE': roe,
        '存货周转率': inventory_turnover,
        '应收账款周转率': receivables_turnover,
    }
    
    import plotly.graph_objects as go
    
    metrics = list(industry_avg.keys())
    
    fig = go.Figure()
    fig.add_trace(go.Bar(name='行业平均', x=metrics, y=list(industry_avg.values())))
    fig.add_trace(go.Bar(name='本公司', x=metrics, y=list(company_values.values())))
    
    fig.update_layout(
        barmode='group',
        height=500,
        xaxis_title="指标",
        yaxis_title="数值",
        showlegend=True
    )
    st.plotly_chart(fig, use_container_width=True)
