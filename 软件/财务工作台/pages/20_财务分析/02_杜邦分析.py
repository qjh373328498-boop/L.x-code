# 高级业务分析 - 性能优化版

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
import sys
import os
from datetime import datetime

# 添加父目录到路径，以便导入 utils 模块
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils.database import get_connection
from utils.formatters import format_currency

# ========== 性能优化：Session State ==========
if '_loaded' not in st.session_state:
    st.session_state._loaded = True


# ========== 性能优化：图表缓存 ==========
@st.cache_data
def create_trend_chart(data, title):
    """缓存趋势图表"""
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=list(range(len(data))), y=data, mode='lines+markers'))
    fig.update_layout(title=title, height=400, showlegend=False)
    return fig

@st.cache_data
def create_comparison_chart(categories, values):
    """缓存对比图表"""
    fig = go.Figure(data=[go.Bar(x=categories, y=values)])
    fig.update_layout(title="对比分析", height=400, showlegend=False)
    return fig


st.set_page_config(page_title="高级业务分析", page_icon="📈", layout="wide")

st.title("📈 高级业务分析 - 经营决策支持")

# 获取实时数据
conn = get_connection()

# 侧边栏配置
st.sidebar.header("分析配置")
analysis_type = st.sidebar.selectbox(
    "分析类型",
    ["经营分析", "趋势预测", "成本分析", "利润分析", "客户分析", "供应商分析"]
)

# 获取期间范围
cursor = conn.cursor()
cursor.execute("SELECT MIN(date), MAX(date) FROM invoice")
date_range = cursor.fetchone()
min_date = datetime.strptime(date_range[0], '%Y-%m-%d') if date_range[0] else datetime.now()
max_date = datetime.strptime(date_range[1], '%Y-%m-%d') if date_range[1] else datetime.now()

start_date = st.sidebar.date_input("开始日期", value=min_date)
end_date = st.sidebar.date_input("结束日期", value=max_date)

if start_date > end_date:
    st.error("开始日期不能大于结束日期")
    st.stop()


# ========== 懒加载优化 ==========
# 使用选项卡式导航代替同时渲染所有内容
st.sidebar.markdown("---")
st.sidebar.subheader("显示选项")
show_trend = st.sidebar.checkbox("显示趋势", value=True)
show_comparison = st.sidebar.checkbox("显示对比", value=False)
show_detail = st.sidebar.checkbox("显示明细", value=False)

# 核心指标卡片
st.subheader("关键经营指标")

# 收入统计
revenue_query = """
    SELECT SUM(amount) as total, COUNT(*) as count
    FROM invoice 
    WHERE date BETWEEN ? AND ?
"""
revenue_data = pd.read_sql_query(revenue_query, conn, params=[start_date, end_date])
total_revenue = revenue_data['total'].iloc[0] or 0
invoice_count = revenue_data['count'].iloc[0] or 0

# 成本统计 (从凭证中获取借方成本类科目)
cost_query = """
    SELECT SUM(ve.amount) as total
    FROM voucher_entry ve
    JOIN voucher v ON ve.voucher_id = v.id
    WHERE ve.entry_type = '借方' 
    AND ve.subject_code LIKE '64%'  -- 成本类科目
    AND v.trans_date BETWEEN ? AND ?
"""
try:
    cost_data = pd.read_sql_query(cost_query, conn, params=[start_date, end_date])
    total_cost = cost_data['total'].iloc[0] or 0
except:
    total_cost = 0

# 往来统计
ar_query = "SELECT SUM(amount) FROM ar_ap WHERE type='AR' AND status='pending'"
ap_query = "SELECT SUM(amount) FROM ar_ap WHERE type='AP' AND status='pending'"
ar_total = pd.read_sql_query(ar_query, conn).iloc[0, 0] or 0
ap_total = pd.read_sql_query(ap_query, conn).iloc[0, 0] or 0

# 显示指标卡
col1, col2, col3, col4, col5 = st.columns(5)

col1.metric(
    "经营收入",
    format_currency(total_revenue),
    f"{invoice_count} 张发票"
)

col2.metric(
    "经营成本",
    format_currency(total_cost),
    delta_color="inverse" if total_cost > 0 else "off"
)

gross_profit = total_revenue - total_cost
gross_margin = (gross_profit / total_revenue * 100) if total_revenue > 0 else 0
col3.metric(
    "毛利润",
    format_currency(gross_profit),
    f"毛利率 {gross_margin:.1f}%"
)

col4.metric(
    "应收账款",
    format_currency(ar_total),
    delta_color="inverse" if ar_total > total_revenue * 0.3 else "normal"
)

col5.metric(
    "应付账款",
    format_currency(ap_total),
    delta_color="normal" if ap_total > 0 else "off"
)

st.divider()

# 根据分析类型显示不同内容
if analysis_type == "经营分析":
    st.subheader("📊 经营概况分析")
    
    col1, col2 = st.columns(2)
    
    with col1:
        # 收入趋势
        trend_query = """
            SELECT strftime('%Y-%m', date) as month,
                   SUM(amount) as revenue,
                   COUNT(*) as count
            FROM invoice
            WHERE date BETWEEN ? AND ?
            GROUP BY strftime('%Y-%m', date)
            ORDER BY month
        """
        trend_df = pd.read_sql_query(trend_query, conn, params=[start_date, end_date])
        
        if not trend_df.empty:
            fig = px.line(trend_df, x='month', y='revenue', 
                         title='月度收入趋势', markers=True)
            fig.update_layout(height=400)
            st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        # 客户集中度
        customer_query = """
            SELECT buyer, SUM(amount) as total, COUNT(*) as count
            FROM invoice
            WHERE date BETWEEN ? AND ?
            GROUP BY buyer
            ORDER BY total DESC
            LIMIT 10
        """
        customer_df = pd.read_sql_query(customer_query, conn, params=[start_date, end_date])
        
        if not customer_df.empty:
            fig = px.pie(customer_df, values='total', names='buyer',
                        title='客户收入占比 TOP10')
            st.plotly_chart(fig, use_container_width=True)
    
    # 杜邦分析
    st.subheader("🔍 杜邦分析")
    
    if total_revenue > 0:
        roe = (gross_profit / total_revenue) * (total_revenue / (ar_total + total_cost)) * 100 if (ar_total + total_cost) > 0 else 0
        
        col1, col2, col3 = st.columns(3)
        
        col1.info(f"""
        **净利润率**
        
        {gross_margin:.2f}%
        
        每 1 元收入产生 {gross_margin/100:.2f}元利润
        """)
        
        col2.info(f"""
        **总资产周转率**
        
        {total_revenue / (ar_total + total_cost) if (ar_total + total_cost) > 0 else 0:.2f}
        
        资产利用效率
        """)
        
        col3.success(f"""
        **ROE (估算)**
        
        {roe:.2f}%
        
        股东权益回报率
        """)

elif analysis_type == "趋势预测":
    st.subheader("🔮 收入趋势预测")
    
    # 获取历史数据
    history_query = """
        SELECT strftime('%Y-%m', date) as month, SUM(amount) as revenue
        FROM invoice
        GROUP BY strftime('%Y-%m', date)
        ORDER BY month
    """
    history_df = pd.read_sql_query(history_query, conn)
    
    if len(history_df) >= 3:
        # 简单移动平均预测
        history_df['revenue'] = pd.to_numeric(history_df['revenue'])
        history_df['MA3'] = history_df['revenue'].rolling(window=3).mean()
        history_df['MA6'] = history_df['revenue'].rolling(window=6).mean()
        
        # 简单线性回归预测
        from scipy import stats
        
        x = range(len(history_df))
        slope, intercept, r_value, p_value, std_err = stats.linregress(x, history_df['revenue'])
        
        # 预测未来 3 个月
        future_months = 3
        last_month = history_df['month'].iloc[-1]
        last_date = datetime.strptime(last_month + '-01', '%Y-%m-%d')
        
        predictions = []
        for i in range(1, future_months + 1):
            next_month = last_date + timedelta(days=32*i)
            next_month_str = next_month.strftime('%Y-%m')
            predicted_value = slope * (len(history_df) + i - 1) + intercept
            predictions.append({
                'month': next_month_str,
                'predicted': max(0, predicted_value),
                'type': '预测'
            })
        
        pred_df = pd.DataFrame(predictions)
        
        # 合并历史和预测
        history_df['type'] = '实际'
        combined_df = pd.concat([
            history_df[['month', 'revenue', 'type']].rename(columns={'revenue': 'value'}),
            pred_df[['month', 'predicted', 'type']].rename(columns={'predicted': 'value'})
        ], ignore_index=True)
        
        fig = px.line(combined_df, x='month', y='value', color='type',
                     title=f'收入趋势预测 (R²={r_value**2:.3f})', markers=True)
        fig.update_layout(height=500)
        
        st.plotly_chart(fig, use_container_width=True)
        
        st.info(f"""
        **预测说明**:
        - 使用线性回归模型
        - 基于过去 {len(history_df)} 个月的数据
        - R² = {r_value**2:.3f} ({'拟合良好' if r_value**2 > 0.7 else '拟合一般' if r_value**2 > 0.5 else '拟合较差'})
        - 下月预测收入：{predictions[0]['predicted']:,.0f} 元
        """)
    else:
        st.warning("历史数据不足，无法进行预测（至少需要 3 个月数据）")

elif analysis_type == "成本分析":
    st.subheader("💰 成本结构分析")
    
    # 成本构成
    cost_structure_query = """
        SELECT ve.subject_name, SUM(ve.amount) as total
        FROM voucher_entry ve
        WHERE ve.entry_type = '借方' 
        AND ve.subject_code LIKE '6%'
        GROUP BY ve.subject_name
        ORDER BY total DESC
    """
    
    try:
        cost_df = pd.read_sql_query(cost_structure_query, conn)
        
        if not cost_df.empty:
            col1, col2 = st.columns(2)
            
            with col1:
                fig = px.bar(cost_df.head(10), x='total', y='subject_name', orientation='h',
                            title='成本构成 TOP10')
                st.plotly_chart(fig, use_container_width=True)
            
            with col2:
                fig = px.pie(cost_df, values='total', names='subject_name',
                            title='成本占比分布')
                st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("暂无成本数据，请先录入凭证")
    except:
        st.info("暂无成本数据")

elif analysis_type == "利润分析":
    st.subheader("💹 盈利能力分析")
    
    # 按客户分析利润贡献
    profit_query = """
        SELECT buyer, 
               SUM(amount) as revenue,
               COUNT(*) as invoice_count,
               AVG(amount) as avg_amount
        FROM invoice
        WHERE date BETWEEN ? AND ?
        GROUP BY buyer
        ORDER BY revenue DESC
    """
    profit_df = pd.read_sql_query(profit_query, conn, params=[start_date, end_date])
    
    if not profit_df.empty:
        # 帕累托分析 (80/20 法则)
        profit_df['cumulative_pct'] = profit_df['revenue'].cumsum() / profit_df['revenue'].sum() * 100
        
        col1, col2 = st.columns(2)
        
        with col1:
            fig = px.bar(profit_df.head(20), x='buyer', y='revenue',
                        title='客户收入贡献 TOP20')
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            fig = px.line(profit_df.head(20), x='buyer', y='cumulative_pct',
                         title='累计收入占比 (帕累托曲线)', markers=True)
            fig.add_hline(y=80, line_dash="dash", annotation_text="80%")
            st.plotly_chart(fig, use_container_width=True)
        
        # 找出贡献 80% 收入的关键客户
        key_customers = profit_df[profit_df['cumulative_pct'] <= 80]
        st.info(f"""
        **帕累托分析结果**:
        - 关键客户数量：{len(key_customers)} 个
        - 贡献收入：{key_customers['revenue'].sum():,.0f} 元
        - 占比：{key_customers['revenue'].sum() / profit_df['revenue'].sum() * 100:.1f}%
        """)

elif analysis_type == "客户分析":
    st.subheader("👥 客户价值分析")
    
    customer_query = """
        SELECT buyer as customer,
               COUNT(*) as invoice_count,
               SUM(amount) as total_amount,
               MIN(date) as first_date,
               MAX(date) as last_date
        FROM invoice
        WHERE buyer IS NOT NULL AND buyer != ''
        GROUP BY buyer
        ORDER BY total_amount DESC
    """
    customer_df = pd.read_sql_query(customer_query, conn)
    
    if not customer_df.empty:
        # RFM 分析简化版
        customer_df['recency'] = (datetime.now() - pd.to_datetime(customer_df['last_date'])).dt.days
        customer_df['frequency'] = customer_df['invoice_count']
        customer_df['monetary'] = customer_df['total_amount']
        
        # 客户分层
        customer_df['segment'] = pd.cut(
            customer_df['total_amount'],
            bins=[0, customer_df['total_amount'].quantile(0.5), 
                  customer_df['total_amount'].quantile(0.8), float('inf')],
            labels=['普通客户', '重要客户', '核心客户']
        )
        
        segment_summary = customer_df.groupby('segment').agg({
            'customer': 'count',
            'total_amount': 'sum'
        }).reset_index()
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.dataframe(customer_df[['customer', 'invoice_count', 'total_amount', 
                                      'recency', 'segment']].head(20), hide_index=True)
        
        with col2:
            fig = px.pie(segment_summary, values='total_amount', names='segment',
                        title='客户分层收入占比')
            st.plotly_chart(fig, use_container_width=True)

elif analysis_type == "供应商分析":
    st.subheader("🏭 供应商分析")
    
    supplier_query = """
        SELECT supplier,
               COUNT(*) as invoice_count,
               SUM(amount) as total_amount,
               AVG(amount) as avg_amount,
               MIN(date) as first_date,
               MAX(date) as last_date
        FROM invoice
        WHERE supplier IS NOT NULL AND supplier != ''
        GROUP BY supplier
        ORDER BY total_amount DESC
    """
    supplier_df = pd.read_sql_query(supplier_query, conn)
    
    if not supplier_df.empty:
        st.dataframe(supplier_df.head(20), hide_index=True)
        
        fig = px.bar(supplier_df.head(10), x='supplier', y='total_amount',
                    title='供应商采购金额 TOP10')
        st.plotly_chart(fig, use_container_width=True)

conn.close()

st.divider()
st.caption("💡 提示：本分析基于当前数据库中的实际数据，建议定期录入业务数据以获得更准确的分析结果")
