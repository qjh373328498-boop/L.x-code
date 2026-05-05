"""
💰 资金诊断 - 资金使用效率分析与优化建议
"""
import streamlit as st
import pandas as pd

# ========== 性能优化 ==========
# Session State: 保存用户输入
if '_session_init' not in st.session_state:
    st.session_state._session_init = True

import plotly.graph_objects as go
from datetime import datetime, timedelta
from utils.database import get_connection, init_db
from utils.formatters import format_currency

st.set_page_config(page_title="资金诊断", page_icon="💰", layout="wide")
init_db()

st.title("💰 资金诊断")

tab1, tab2, tab3 = st.tabs(["数据录入", "资金分析", "历史趋势"])

with tab1:
    st.subheader("录入资金数据")
    
    col1, col2 = st.columns(2)
    
    with col1:
        period = st.text_input("期间", placeholder="2024-01")
        opening_cash = st.number_input("期初货币资金", value=0.0)
        closing_cash = st.number_input("期末货币资金", value=0.0)
        avg_receivables = st.number_input("平均应收账款", value=0.0)
        avg_inventory = st.number_input("平均存货", value=0.0)
    
    with col2:
        revenue = st.number_input("营业收入", value=0.0)
        cogs = st.number_input("营业成本", value=0.0)
        operating_expense = st.number_input("期间费用", value=0.0)
        operating_cash_flow = st.number_input("经营活动现金流净额", value=0.0)
    
    if st.button("保存数据", type="primary"):
        if period:
            conn = get_connection()
            metrics = [
                (period, '期初货币资金', opening_cash, '元'),
                (period, '期末货币资金', closing_cash, '元'),
                (period, '平均应收账款', avg_receivables, '元'),
                (period, '平均存货', avg_inventory, '元'),
                (period, '营业收入', revenue, '元'),
                (period, '营业成本', cogs, '元'),
                (period, '期间费用', operating_expense, '元'),
                (period, '经营现金流', operating_cash_flow, '元'),
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
    st.subheader("资金使用效率分析")
    
    conn = get_connection()
    df_all = pd.read_sql_query("SELECT * FROM financial_metrics ORDER BY period DESC", conn)
    conn.close()
    
    if df_all.empty:
        st.info("暂无数据，请先录入")
        st.stop()
    
    latest_period = df_all['period'].max()
    df = df_all[df_all['period'] == latest_period]
    
    metrics_dict = dict(zip(df['metric_name'], df['value']))
    
    opening_cash = metrics_dict.get('期初货币资金', 0)
    closing_cash = metrics_dict.get('期末货币资金', 0)
    avg_receivables = metrics_dict.get('平均应收账款', 0)
    avg_inventory = metrics_dict.get('平均存货', 0)
    revenue = metrics_dict.get('营业收入', 0)
    cogs = metrics_dict.get('营业成本', 0)
    operating_cash_flow = metrics_dict.get('经营现金流', 0)
    
    avg_cash = (opening_cash + closing_cash) / 2
    total_operating_assets = avg_cash + avg_receivables + avg_inventory
    
    cash_turnover = revenue / avg_cash if avg_cash > 0 else 0
    receivables_turnover = revenue / avg_receivables if avg_receivables > 0 else 0
    inventory_turnover = cogs / avg_inventory if avg_inventory > 0 else 0
    
    dso = 365 / receivables_turnover if receivables_turnover > 0 else 0
    dio = 365 / inventory_turnover if inventory_turnover > 0 else 0
    
    ccc = dso + dio - (avg_inventory / (cogs / 365)) if cogs > 0 else 0
    
    st.subheader("📊 周转率指标")
    col1, col2, col3, col4 = st.columns(4)
    
    col1.metric("现金周转率", f"{cash_turnover:.2f} 次")
    col2.metric("应收账款周转率", f"{receivables_turnover:.2f} 次")
    col3.metric("存货周转率", f"{inventory_turnover:.2f} 次")
    col4.metric("现金循环周期", f"{ccc:.1f} 天")
    
    st.divider()
    
    st.subheader("💡 资金使用效率评分")
    
    score = 0
    suggestions = []
    
    if cash_turnover > 5:
        score += 25
        suggestions.append("✅ 现金周转效率高")
    elif cash_turnover > 3:
        score += 15
        suggestions.append("⚠️ 现金周转一般，建议加强现金管理")
    else:
        suggestions.append("❌ 现金周转过慢，存在资金闲置")
    
    if receivables_turnover > 10:
        score += 25
        suggestions.append("✅ 应收账款管理良好")
    elif receivables_turnover > 6:
        score += 15
        suggestions.append("⚠️ 收款周期较长，建议加强催收")
    else:
        suggestions.append("❌ 应收账款周转过慢，坏账风险较高")
    
    if inventory_turnover > 8:
        score += 25
        suggestions.append("✅ 存货管理效率高")
    elif inventory_turnover > 4:
        score += 15
        suggestions.append("⚠️ 存货周转一般，建议优化库存结构")
    else:
        suggestions.append("❌ 存货积压严重，资金占用过多")
    
    if operating_cash_flow > 0:
        score += 25
        suggestions.append("✅ 经营活动现金流为正")
    else:
        suggestions.append("❌ 经营活动现金流为负，需关注")
    
    score_display = score / 100 * 10
    
    col1, col2 = st.columns(2)
    col1.metric("综合评分", f"{score_display:.1f}/10")
    
    st.subheader("优化建议")
    for s in suggestions:
        st.write(s)

with tab3:
    st.subheader("历史趋势分析")
    
    conn = get_connection()
    df = pd.read_sql_query(
        """SELECT period, metric_name, value FROM financial_metrics 
           WHERE metric_name IN ('营业收入', '经营现金流', '平均应收账款', '平均存货')
           ORDER BY period""",
        conn
    )
    conn.close()
    
    if df.empty:
        st.info("暂无历史数据")
        st.stop()
    
    df_pivot = df.pivot(index='period', columns='metric_name', values='value')
    
    fig = go.Figure()
    
    for col in df_pivot.columns:
        fig.add_trace(go.Scatter(x=df_pivot.index, y=df_pivot[col], name=col))
    
    fig.update_layout(
        xaxis_title="期间",
        yaxis_title="金额 (元)",
        height=500,
        hovermode='x unified'
    )
    st.plotly_chart(fig, use_container_width=True)
    
    st.dataframe(df_pivot, use_container_width=True)
