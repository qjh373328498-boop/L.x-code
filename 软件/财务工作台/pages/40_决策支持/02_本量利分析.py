# 本量利分析 - 性能优化版

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import sys
import os

# 添加父目录到路径，以便导入 utils 模块
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils.formatters import format_currency

# ========== 性能优化：Session State ==========
if '_loaded' not in st.session_state:
    st.session_state._loaded = True


# ========== 性能优化：图表缓存 ==========
@st.cache_data
def create_breakeven_chart(fixed_cost, unit_price, unit_cost, volume):
    """缓存盈亏平衡图表"""
    revenue = [unit_price * v for v in range(0, volume*2, volume//10)]
    total_cost = [fixed_cost + unit_cost * v for v in range(0, volume*2, volume//10)]
    
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=list(range(0, volume*2, volume//10)), y=revenue, name='收入'))
    fig.add_trace(go.Scatter(x=list(range(0, volume*2, volume//10)), y=total_cost, name='成本'))
    fig.update_layout(title="盈亏平衡分析", height=450)
    return fig


st.set_page_config(page_title="本量利分析", page_icon="📈", layout="wide")

st.title("📈 本量利 (CVP) 分析")

st.sidebar.header("输入参数")

fixed_cost = st.sidebar.number_input("固定成本 (元)", value=100000.0, step=1000.0)
unit_price = st.sidebar.number_input("单价 (元)", value=100.0, step=1.0)
unit_variable_cost = st.sidebar.number_input("单位变动成本 (元)", value=60.0, step=1.0)
sales_volume = st.sidebar.number_input("预计销量 (件)", value=5000, step=100)

contribution_margin = unit_price - unit_variable_cost
contribution_margin_ratio = contribution_margin / unit_price if unit_price > 0 else 0
break_even_volume = fixed_cost / contribution_margin if contribution_margin > 0 else 0
break_even_revenue = break_even_volume * unit_price

st.subheader("📊 核心指标")
col1, col2, col3, col4 = st.columns(4)

col1.metric("单位边际贡献", format_currency(contribution_margin))
col2.metric("边际贡献率", f"{contribution_margin_ratio * 100:.1f}%")
col3.metric("盈亏平衡点 (销量)", f"{break_even_volume:.0f} 件")
col4.metric("盈亏平衡点 (金额)", format_currency(break_even_revenue))


# ========== 懒加载选项 ==========
with st.sidebar.expander("📊 显示设置"):
    show_charts = st.checkbox("显示图表", value=True)
    show_details = st.checkbox("显示明细", value=False)

st.divider()

tab1, tab2 = st.tabs(["盈亏平衡图", "敏感性分析"])

with tab1:
    st.subheader("盈亏平衡分析图")
    
    volumes = list(range(0, int(sales_volume * 1.5), max(100, int(sales_volume // 10))))
    revenue = [v * unit_price for v in volumes]
    total_cost = [fixed_cost + v * unit_variable_cost for v in volumes]
    fixed_cost_line = [fixed_cost] * len(volumes)
    
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=volumes, y=revenue, name='销售收入', line=dict(width=3)))
    fig.add_trace(go.Scatter(x=volumes, y=total_cost, name='总成本', line=dict(width=3)))
    fig.add_trace(go.Scatter(x=volumes, y=fixed_cost_line, name='固定成本', line=dict(dash='dash')))
    
    fig.add_vline(x=break_even_volume, line_dash="dash", annotation_text="盈亏平衡点")
    
    fig.update_layout(
        xaxis_title="销量 (件)",
        yaxis_title="金额 (元)",
        height=500,
        hovermode='x unified'
    )
    st.plotly_chart(fig, use_container_width=True)

with tab2:
    st.subheader("敏感性分析")
    
    factor = st.slider("变动幅度", -50, 50, 20)
    
    scenarios = []
    
    base_profit = sales_volume * contribution_margin - fixed_cost
    
    scenarios.append({
        '因素': '基准方案',
        '利润': base_profit,
        '变动率': '0.0%'
    })
    
    new_price = unit_price * (1 + factor / 100)
    new_profit = sales_volume * (new_price - unit_variable_cost) - fixed_cost
    change = (new_profit - base_profit) / base_profit * 100 if base_profit != 0 else 0
    scenarios.append({
        '因素': f'价格 {factor:+d}%',
        '利润': new_profit,
        '变动率': f'{change:+.1f}%'
    })
    
    new_vc = unit_variable_cost * (1 + factor / 100)
    new_profit = sales_volume * (unit_price - new_vc) - fixed_cost
    change = (new_profit - base_profit) / base_profit * 100 if base_profit != 0 else 0
    scenarios.append({
        '因素': f'变动成本 {factor:+d}%',
        '利润': new_profit,
        '变动率': f'{change:+.1f}%'
    })
    
    new_fc = fixed_cost * (1 + factor / 100)
    new_profit = sales_volume * contribution_margin - new_fc
    change = (new_profit - base_profit) / base_profit * 100 if base_profit != 0 else 0
    scenarios.append({
        '因素': f'固定成本 {factor:+d}%',
        '利润': new_profit,
        '变动率': f'{change:+.1f}%'
    })
    
    new_volume = sales_volume * (1 + factor / 100)
    new_profit = new_volume * contribution_margin - fixed_cost
    change = (new_profit - base_profit) / base_profit * 100 if base_profit != 0 else 0
    scenarios.append({
        '因素': f'销量 {factor:+d}%',
        '利润': new_profit,
        '变动率': f'{change:+.1f}%'
    })
    
    df_scenarios = pd.DataFrame(scenarios)
    df_scenarios['利润'] = df_scenarios['利润'].apply(lambda x: f"¥{x:,.0f}")
    st.dataframe(df_scenarios, use_container_width=True, hide_index=True)

st.divider()

current_profit = sales_volume * contribution_margin - fixed_cost
margin_of_safety = (sales_volume - break_even_volume) / sales_volume * 100 if sales_volume > 0 else 0

st.subheader("💡 经营安全分析")
col1, col2 = st.columns(2)

col1.info(f"""
**当前利润**: {format_currency(current_profit)}

**安全边际率**: {margin_of_safety:.1f}%

{'✅ 经营很安全' if margin_of_safety > 30 else '⚠️ 需要注意风险' if margin_of_safety > 10 else '❌ 经营风险较高'}
""")

col2.success(f"""
**经营杠杆系数**: {sales_volume * contribution_margin / current_profit if current_profit > 0 else 0:.2f}

销量每增长 1%,利润将增长 {sales_volume * contribution_margin / current_profit if current_profit > 0 else 0:.1f}%
""")
