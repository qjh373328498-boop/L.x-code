"""
📄 发票管家 - 发票录入、查询、认证管理
"""
import streamlit as st
import pandas as pd

# ========== 性能优化 ==========
# Session State: 保存用户输入
if '_session_init' not in st.session_state:
    st.session_state._session_init = True

from datetime import datetime
from utils.database import get_connection, init_db

st.set_page_config(page_title="发票管家", page_icon="📄", layout="wide")
init_db()

st.title("📄 发票管家")

tab1, tab2, tab3 = st.tabs(["录入发票", "发票查询", "批量导入"])

with tab1:
    st.subheader("录入新发票")
    
    col1, col2 = st.columns(2)
    with col1:
        code = st.text_input("发票代码", placeholder="10 位或 12 位数字")
        number = st.text_input("发票号码", placeholder="8 位数字")
        date = st.date_input("开票日期", value=datetime.now(), key="invoice_date")
        amount = st.number_input("金额", min_value=0.0, step=0.01)
    
    with col2:
        inv_type = st.selectbox("发票类型", ["专用发票", "普通发票", "电子发票"])
        supplier = st.text_input("销售方")
        buyer = st.text_input("购买方")
        status = st.selectbox("认证状态", ["未认证", "已认证", "已退票"])
    
    if st.button("保存发票", type="primary"):
        if code and number and amount:
            conn = get_connection()
            cursor = conn.cursor()
            try:
                cursor.execute(
                    """INSERT INTO invoice (code, number, date, amount, type, supplier, buyer, status)
                       VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
                    (code, number, date.strftime('%Y-%m-%d'), amount, inv_type, supplier, buyer, status)
                )
                conn.commit()
                st.success("发票保存成功！")
            except sqlite3.IntegrityError:
                st.error("该发票已存在！")
            finally:
                conn.close()
        else:
            st.error("请填写必填项：发票代码、发票号码、金额")

with tab2:
    st.subheader("发票查询")
    
    search_code = st.text_input("搜索发票代码或号码")
    
    conn = get_connection()
    if search_code:
        df = pd.read_sql_query(
            """SELECT * FROM invoice WHERE code LIKE ? OR number LIKE ? ORDER BY date DESC""",
            conn,
            params=(f'%{search_code}%', f'%{search_code}%')
        )
    else:
        df = pd.read_sql_query("SELECT * FROM invoice ORDER BY date DESC", conn)
    conn.close()
    
    if not df.empty:
        st.dataframe(df, use_container_width=True)
        st.metric("发票总数", len(df))
    else:
        st.info("暂无发票数据")

with tab3:
    st.subheader("批量导入发票")
    
    uploaded_file = st.file_uploader("上传 Excel 文件", type=['xlsx', 'xls'])
    
    if uploaded_file:
        df_upload = pd.read_excel(uploaded_file)
        st.write(f"预览数据：{len(df_upload)} 行")
        st.dataframe(df_upload.head())
        
        if st.button("确认导入"):
            conn = get_connection()
            cursor = conn.cursor()
            count = 0
            for _, row in df_upload.iterrows():
                try:
                    cursor.execute(
                        """INSERT OR IGNORE INTO invoice (code, number, date, amount, type, supplier, buyer, status)
                           VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
                        (str(row.get('code', '')), str(row.get('number', '')),
                         row.get('date', datetime.now().strftime('%Y-%m-%d')),
                         float(row.get('amount', 0)), row.get('type', '普通发票'),
                         row.get('supplier', ''), row.get('buyer', ''), row.get('status', '未认证'))
                    )
                    count += 1
                except:
                    pass
            conn.commit()
            conn.close()
            st.success(f"成功导入 {count} 条发票记录")
