"""
💳 应收应付管理 - 往来款项管理
"""
import streamlit as st
import pandas as pd

# ========== 性能优化 ==========
# Session State: 保存用户输入
if '_session_init' not in st.session_state:
    st.session_state._session_init = True

from datetime import datetime, timedelta
from utils.database import get_connection, init_db
from utils.formatters import format_currency

st.set_page_config(page_title="应收应付管理", page_icon="💳", layout="wide")
init_db()

st.title("💳 应收应付管理")

tab1, tab2, tab3, tab4 = st.tabs(["应收账款", "应付账款", "账龄分析", "到期提醒"])

with tab1:
    st.subheader("应收账款管理")
    
    col1, col2 = st.columns(2)
    with col1:
        ar_customer = st.text_input("客户名称", key="ar_customer")
        ar_amount = st.number_input("应收金额", min_value=0.01, key="ar_amount")
        ar_date = st.date_input("应收日期", value=datetime.now(), key="ar_date")
    with col2:
        ar_due_date = st.date_input("到期日期", value=datetime.now() + timedelta(days=30), key="ar_due_date")
        ar_summary = st.text_input("摘要", key="ar_summary")
    
    if st.button("添加应收账款", type="primary", key="btn_add_ar"):
        if ar_customer and ar_amount:
            conn = get_connection()
            conn.execute(
                """INSERT INTO ar_ap (type, counterparty, amount, date, due_date, summary, status)
                   VALUES (?, ?, ?, ?, ?, ?, 'pending')""",
                ('AR', ar_customer, ar_amount, ar_date.strftime('%Y-%m-%d'),
                 ar_due_date.strftime('%Y-%m-%d'), ar_summary)
            )
            conn.commit()
            conn.close()
            st.success("添加成功")
            st.rerun()
    
    conn = get_connection()
    ar_df = pd.read_sql_query(
        "SELECT * FROM ar_ap WHERE type='AR' ORDER BY date DESC", conn
    )
    conn.close()
    
    if not ar_df.empty:
        st.dataframe(ar_df, use_container_width=True)
        st.metric("应收账款总额", format_currency(ar_df['amount'].sum()))

with tab2:
    st.subheader("应付账款管理")
    
    col1, col2 = st.columns(2)
    with col1:
        ap_supplier = st.text_input("供应商名称", key="ap_supplier")
        ap_amount = st.number_input("应付金额", min_value=0.01, key="ap_amount")
        ap_date = st.date_input("应付日期", value=datetime.now(), key="ap_date")
    with col2:
        ap_due_date = st.date_input("到期日期", value=datetime.now() + timedelta(days=30), key="ap_due_date")
        ap_summary = st.text_input("摘要", key="ap_summary")
    
    if st.button("添加应付账款", type="primary", key="btn_add_ap"):
        if ap_supplier and ap_amount:
            conn = get_connection()
            conn.execute(
                """INSERT INTO ar_ap (type, counterparty, amount, date, due_date, summary, status)
                   VALUES (?, ?, ?, ?, ?, ?, 'pending')""",
                ('AP', ap_supplier, ap_amount, ap_date.strftime('%Y-%m-%d'),
                 ap_due_date.strftime('%Y-%m-%d'), ap_summary)
            )
            conn.commit()
            conn.close()
            st.success("添加成功")
            st.rerun()
    
    conn = get_connection()
    ap_df = pd.read_sql_query(
        "SELECT * FROM ar_ap WHERE type='AP' ORDER BY date DESC", conn
    )
    conn.close()
    
    if not ap_df.empty:
        st.dataframe(ap_df, use_container_width=True)
        st.metric("应付账款总额", format_currency(ap_df['amount'].sum()))

with tab3:
    st.subheader("账龄分析")
    
    conn = get_connection()
    ar_df = pd.read_sql_query("SELECT * FROM ar_ap WHERE type='AR'", conn)
    conn.close()
    
    if not ar_df.empty:
        today = datetime.now()
        
        def age_category(due_date_str):
            due_date = datetime.strptime(due_date_str, '%Y-%m-%d')
            days_overdue = (today - due_date).days
            if days_overdue < 0:
                return '未到期'
            elif days_overdue <= 30:
                return '1-30 天'
            elif days_overdue <= 60:
                return '31-60 天'
            elif days_overdue <= 90:
                return '61-90 天'
            else:
                return '90 天以上'
        
        ar_df['账龄'] = ar_df['due_date'].apply(age_category)
        
        age_summary = ar_df.groupby('账龄')['amount'].sum().reindex(
            ['未到期', '1-30 天', '31-60 天', '61-90 天', '90 天以上'], fill_value=0
        )
        
        col1, col2 = st.columns(2)
        col1.write("### 应收账款账龄")
        col1.dataframe(age_summary)
        
        import plotly.express as px
        fig = px.pie(values=age_summary.values, names=age_summary.index, title="应收账款账龄分布")
        col2.plotly_chart(fig, use_container_width=True)

with tab4:
    st.subheader("到期提醒")
    
    days_lookahead = st.slider("查看未来多少天到期的款项", 7, 90, 30)
    
    today = datetime.now()
    end_date = today + timedelta(days=days_lookahead)
    
    conn = get_connection()
    upcoming = pd.read_sql_query(
        """SELECT * FROM ar_ap 
           WHERE due_date BETWEEN ? AND ? AND status='pending'
           ORDER BY due_date""",
        conn, params=[today.strftime('%Y-%m-%d'), end_date.strftime('%Y-%m-%d')]
    )
    conn.close()
    
    if not upcoming.empty:
        for _, row in upcoming.iterrows():
            due_date = datetime.strptime(row['due_date'], '%Y-%m-%d')
            days_left = (due_date - today).days
            
            if days_left <= 3:
                status = "🔴 紧急"
            elif days_left <= 7:
                status = "🟠 即将到期"
            else:
                status = "🟡"
            
            type_label = "应收" if row['type'] == 'AR' else "应付"
            st.write(f"**{status}** {type_label} - {row['counterparty']}: {format_currency(row['amount'])} (到期：{row['due_date']})")
            st.divider()
    else:
        st.success(f"未来{days_lookahead}天内没有到期款项")
