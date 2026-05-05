"""
📅 财务日历 - 重要日期提醒与管理
"""
import streamlit as st
import pandas as pd

# ========== 性能优化 ==========
# Session State: 保存用户输入
if '_session_init' not in st.session_state:
    st.session_state._session_init = True

from datetime import datetime, timedelta
from utils.database import get_connection, init_db

st.set_page_config(page_title="财务日历", page_icon="📅", layout="wide")
init_db()

st.title("📅 财务日历")

tab1, tab2, tab3 = st.tabs(["添加事件", "日历视图", "即将到期"])

with tab1:
    st.subheader("添加新事件")
    
    col1, col2 = st.columns(2)
    
    with col1:
        title = st.text_input("事件标题")
        event_date = st.date_input("事件日期", value=datetime.now(), key="event_date")
        event_type = st.selectbox("事件类型", [
            "纳税申报", "财务报表", "审计", "付款", "收款",
            "会议", "年检", "其他"
        ])
    
    with col2:
        description = st.text_area("描述")
        is_recurring = st.checkbox("每年重复", value=False)
    
    if st.button("保存事件", type="primary"):
        if title:
            conn = get_connection()
            conn.execute(
                """INSERT INTO calendar_event (title, event_date, event_type, description, is_recurring)
                   VALUES (?, ?, ?, ?, ?)""",
                (title, event_date.strftime('%Y-%m-%d'), event_type, description, is_recurring)
            )
            conn.commit()
            conn.close()
            st.success("事件保存成功")
            st.rerun()

with tab2:
    st.subheader("日历视图")
    
    col1, col2 = st.columns(2)
    with col1:
        filter_month = st.selectbox(
            "筛选月份",
            [(datetime.now() + timedelta(days=30*i)).strftime('%Y-%m') for i in range(-3, 6)]
        )
    with col2:
        filter_type = st.multiselect(
            "筛选类型",
            ["纳税申报", "财务报表", "审计", "付款", "收款", "会议", "年检", "其他"],
            default=[]
        )
    
    conn = get_connection()
    
    query = "SELECT * FROM calendar_event WHERE event_date LIKE ?"
    params = [f"{filter_month}%"]
    
    if filter_type:
        query += " AND event_type IN (" + ','.join(['?'] * len(filter_type)) + ")"
        params.extend(filter_type)
    
    query += " ORDER BY event_date"
    
    df = pd.read_sql_query(query, conn, params=params)
    conn.close()
    
    if not df.empty:
        df['日期'] = pd.to_datetime(df['event_date']).dt.strftime('%Y-%m-%d %a')
        df['类型'] = df['event_type']
        df['标题'] = df['title']
        df['重复'] = df['is_recurring'].apply(lambda x: '🔄' if x else '')
        
        st.dataframe(
            df[['日期', '标题', '类型', '重复', 'description']],
            use_container_width=True,
            column_config={
                '日期': '日期',
                '标题': '标题',
                '类型': '类型',
                '重复': '重复',
                'description': '描述'
            }
        )
    else:
        st.info("该月份暂无事件")

with tab3:
    st.subheader("即将到期提醒")
    
    days_limit = st.slider("查看未来多少天的事件", 7, 90, 30, key="lookahead_days")
    
    today = datetime.now()
    end_date = today + timedelta(days=days_limit)
    
    conn = get_connection()
    df = pd.read_sql_query(
        """SELECT * FROM calendar_event 
           WHERE event_date BETWEEN ? AND ?
           ORDER BY event_date""",
        conn,
        params=[today.strftime('%Y-%m-%d'), end_date.strftime('%Y-%m-%d')]
    )
    conn.close()
    
    if not df.empty:
        for _, row in df.iterrows():
            event_date = datetime.strptime(row['event_date'], '%Y-%m-%d')
            days_remaining = (event_date - today).days
            
            if days_remaining == 0:
                status = "🔴 今天"
            elif days_remaining <= 3:
                status = "🟠 即将到期"
            elif days_remaining <= 7:
                status = "🟡 本周内"
            else:
                status = "🟢"
            
            with st.container():
                col1, col2, col3 = st.columns([1, 3, 1])
                col1.write(f"**{event_date.strftime('%m-%d')}**")
                col2.write(f"{row['title']} ({row['event_type']})")
                col3.write(status)
                st.divider()
    else:
        st.success(f"未来{days_limit}天内没有待办事件")
