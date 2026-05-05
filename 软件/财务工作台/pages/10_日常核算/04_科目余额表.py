"""
📊 科目余额表 - 科目汇总与余额查询
"""
import streamlit as st
import pandas as pd

# ========== 性能优化 ==========
# Session State: 保存用户输入
if '_session_init' not in st.session_state:
    st.session_state._session_init = True

from utils.database import get_connection, init_db
from utils.formatters import format_currency

st.set_page_config(page_title="科目余额表", page_icon="📊", layout="wide")
init_db()

st.title("📊 科目余额表")

tab1, tab2 = st.tabs(["余额查询", "科目设置"])

with tab1:
    st.subheader("科目余额查询")
    
    col1, col2 = st.columns(2)
    with col1:
        period = st.text_input("期间", placeholder="2024-12")
    with col2:
        subject_filter = st.text_input("科目筛选")
    
    conn = get_connection()
    
    query = "SELECT * FROM balance_sheet WHERE period = ?"
    params = [period]
    
    if subject_filter:
        query += " AND (subject_code LIKE ? OR subject_name LIKE ?)"
        params.extend([f'%{subject_filter}%', f'%{subject_filter}%'])
    
    query += " ORDER BY subject_code"
    
    df = pd.read_sql_query(query, conn, params=params)
    conn.close()
    
    if not df.empty:
        st.dataframe(df, use_container_width=True)
        
        total_debit = df[df['direction'] == 'debit']['closing_balance'].sum()
        total_credit = df[df['direction'] == 'credit']['closing_balance'].sum()
        
        col1, col2, col3 = st.columns(3)
        col1.metric("借方余额合计", format_currency(total_debit))
        col2.metric("贷方余额合计", format_currency(total_credit))
        col3.success("✅ 借贷平衡" if abs(total_debit - total_credit) < 0.01 else "❌ 不平衡")
        
        import plotly.express as px
        
        top_subjects = df.nlargest(10, 'closing_balance')
        fig = px.bar(top_subjects, x='subject_name', y='closing_balance', 
                     title="余额前 10 大科目", labels={'closing_balance': '余额', 'subject_name': '科目'})
        fig.update_layout(height=500)
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("该期间暂无数据")

with tab2:
    st.subheader("科目设置")
    
    st.write("预设会计科目：")
    
    subjects = [
        {'code': '1001', 'name': '库存现金', 'type': '资产'},
        {'code': '1002', 'name': '银行存款', 'type': '资产'},
        {'code': '1122', 'name': '应收账款', 'type': '资产'},
        {'code': '1221', 'name': '其他应收款', 'type': '资产'},
        {'code': '1405', 'name': '库存商品', 'type': '资产'},
        {'code': '1601', 'name': '固定资产', 'type': '资产'},
        {'code': '2001', 'name': '短期借款', 'type': '负债'},
        {'code': '2202', 'name': '应付账款', 'type': '负债'},
        {'code': '2211', 'name': '应付职工薪酬', 'type': '负债'},
        {'code': '2221', 'name': '应交税费', 'type': '负债'},
        {'code': '3001', 'name': '实收资本', 'type': '权益'},
        {'code': '4001', 'name': '生产成本', 'type': '成本'},
        {'code': '5001', 'name': '制造费用', 'type': '成本'},
        {'code': '6001', 'name': '主营业务收入', 'type': '损益'},
        {'code': '6401', 'name': '主营业务成本', 'type': '损益'},
        {'code': '6601', 'name': '销售费用', 'type': '损益'},
        {'code': '6602', 'name': '管理费用', 'type': '损益'},
        {'code': '6603', 'name': '财务费用', 'type': '损益'},
    ]
    
    st.dataframe(pd.DataFrame(subjects), use_container_width=True, hide_index=True)
