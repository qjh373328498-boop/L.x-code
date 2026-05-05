"""
📊 预算分析 - 预算执行差异分析
"""
import streamlit as st
import pandas as pd

# ========== 性能优化：Session State ==========
if '_loaded' not in st.session_state:
    st.session_state._loaded = True

import plotly.graph_objects as go
from utils.database import get_connection, init_db
from utils.formatters import format_currency

st.set_page_config(page_title="预算分析", page_icon="📊", layout="wide")
init_db()

st.title("📊 预算分析")

tab1, tab2, tab3 = st.tabs(["预算录入", "执行分析", "差异分析"])

with tab1:
    st.subheader("录入预算数据")
    
    col1, col2 = st.columns(2)
    
    with col1:
        period = st.text_input("期间", placeholder="2024-01")
        budget_revenue = st.number_input("预算收入", value=0.0)
        budget_cost = st.number_input("预算成本", value=0.0)
        budget_expense = st.number_input("预算费用", value=0.0)
    
    with col2:
        actual_revenue = st.number_input("实际收入", value=0.0)
        actual_cost = st.number_input("实际成本", value=0.0)
        actual_expense = st.number_input("实际费用", value=0.0)
    
    if st.button("保存预算数据", type="primary"):
        if period:
            conn = get_connection()
            metrics = [
                (period, '预算收入', budget_revenue, '元'),
                (period, '预算成本', budget_cost, '元'),
                (period, '预算费用', budget_expense, '元'),
                (period, '实际收入', actual_revenue, '元'),
                (period, '实际成本', actual_cost, '元'),
                (period, '实际费用', actual_expense, '元'),
            ]
            for m in metrics:
                conn.execute(
                    """INSERT OR REPLACE INTO financial_metrics (period, metric_name, value, unit)
                       VALUES (?, ?, ?, ?)""", m
                )
            conn.commit()
            conn.close()
            st.success("预算数据保存成功")

with tab2:
    st.subheader("预算执行分析")
    
    conn = get_connection()
    df_all = pd.read_sql_query("SELECT * FROM financial_metrics ORDER BY period DESC", conn)
    conn.close()
    
    if df_all.empty:
        st.info("暂无数据")
        st.stop()
    
    latest_period = df_all['period'].max()
    df = df_all[df_all['period'] == latest_period]
    
    metrics_dict = dict(zip(df['metric_name'], df['value']))
    
    budget_revenue = metrics_dict.get('预算收入', 0)
    actual_revenue = metrics_dict.get('实际收入', 0)
    budget_cost = metrics_dict.get('预算成本', 0)
    actual_cost = metrics_dict.get('实际成本', 0)
    budget_expense = metrics_dict.get('预算费用', 0)
    actual_expense = metrics_dict.get('实际费用', 0)
    
    revenue_variance = actual_revenue - budget_revenue
    revenue_variance_rate = revenue_variance / budget_revenue * 100 if budget_revenue > 0 else 0
    
    cost_variance = actual_cost - budget_cost
    cost_variance_rate = cost_variance / budget_cost * 100 if budget_cost > 0 else 0
    
    expense_variance = actual_expense - budget_expense
    expense_variance_rate = expense_variance / budget_expense * 100 if budget_expense > 0 else 0
    
    st.subheader("📊 执行概况")
    col1, col2, col3 = st.columns(3)
    
    col1.metric(
        "收入差异",
        f"{revenue_variance_rate:+.1f}%",
        f"{format_currency(revenue_variance)}",
        delta_color="normal" if revenue_variance >= 0 else "inverse"
    )
    
    col2.metric(
        "成本差异",
        f"{cost_variance_rate:+.1f}%",
        f"{format_currency(cost_variance)}",
        delta_color="inverse" if cost_variance >= 0 else "normal"
    )
    
    col3.metric(
        "费用差异",
        f"{expense_variance_rate:+.1f}%",
        f"{format_currency(expense_variance)}",
        delta_color="inverse" if expense_variance >= 0 else "normal"
    )
    
    st.divider()
    
    st.subheader("预算 vs 实际对比")
    
    categories = ['收入', '成本', '费用']
    budget_values = [budget_revenue, budget_cost, budget_expense]
    actual_values = [actual_revenue, actual_cost, actual_expense]
    
    fig = go.Figure()
    fig.add_trace(go.Bar(name='预算', x=categories, y=budget_values))
    fig.add_trace(go.Bar(name='实际', x=categories, y=actual_values))
    
    fig.update_layout(
        barmode='group',
        height=400,
        showlegend=True
    )
    st.plotly_chart(fig, use_container_width=True)

with tab3:
    st.subheader("差异原因分析")
    
    conn = get_connection()
    df = pd.read_sql_query(
        """SELECT period, metric_name, value FROM financial_metrics 
           WHERE metric_name IN ('预算收入', '实际收入', '预算成本', '实际成本', '预算费用', '实际费用')
           ORDER BY period""",
        conn
    )
    conn.close()
    
    if df.empty:
        st.info("暂无数据")
        st.stop()
    
    periods = df['period'].unique()
    
    data = []
    for period in periods:
        period_data = df[df['period'] == period]
        metrics = dict(zip(period_data['metric_name'], period_data['value']))
        
        rev_var = metrics.get('实际收入', 0) - metrics.get('预算收入', 0)
        cost_var = metrics.get('实际成本', 0) - metrics.get('预算成本', 0)
        exp_var = metrics.get('实际费用', 0) - metrics.get('预算费用', 0)
        
        budget_profit = metrics.get('预算收入', 0) - metrics.get('预算成本', 0) - metrics.get('预算费用', 0)
        actual_profit = metrics.get('实际收入', 0) - metrics.get('实际成本', 0) - metrics.get('实际费用', 0)
        profit_var = actual_profit - budget_profit
        
        data.append({
            '期间': period,
            '收入差异': rev_var,
            '成本差异': cost_var,
            '费用差异': exp_var,
            '利润差异': profit_var,
            '预算利润': budget_profit,
            '实际利润': actual_profit,
        })
    
    df_variance = pd.DataFrame(data)
    
    st.dataframe(df_variance, use_container_width=True, hide_index=True)
    
    fig = go.Figure()
    fig.add_trace(go.Bar(name='收入差异', x=df_variance['期间'], y=df_variance['收入差异']))
    fig.add_trace(go.Bar(name='成本差异', x=df_variance['期间'], y=df_variance['成本差异']))
    fig.add_trace(go.Bar(name='费用差异', x=df_variance['期间'], y=df_variance['费用差异']))
    
    fig.update_layout(
        barmode='relative',
        height=400,
        showlegend=True
    )
    st.plotly_chart(fig, use_container_width=True)
