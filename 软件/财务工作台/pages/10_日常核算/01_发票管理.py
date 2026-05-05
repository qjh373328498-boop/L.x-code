"""
📄 发票管家 - 发票录入、查询、认证管理（性能优化版）
"""
import streamlit as st
import pandas as pd
import sqlite3

# ========== 性能优化 ==========
# Session State: 保存用户输入
if '_session_init' not in st.session_state:
    st.session_state._session_init = True

from datetime import datetime
from utils.database import get_connection, init_db
from utils.query_optimizer import get_paginated_data, render_pagination

st.set_page_config(page_title="发票管家", page_icon="📄", layout="wide")
init_db()

st.title("📄 发票管家")

# ========== 性能优化：缓存发票数据查询 ==========
@st.cache_data(ttl=300)  # 5 分钟缓存
def get_invoices_cached(where_clause: str = "", params: tuple = ()):
    """获取发票数据（带缓存）"""
    conn = get_connection()
    query = f"SELECT * FROM invoice {where_clause} ORDER BY date DESC"
    df = pd.read_sql_query(query, conn, params=params)
    conn.close()
    return df

tab1, tab2, tab3 = st.tabs(["录入发票", "发票查询", "批量导入"])

with tab1:
    st.subheader("录入新发票")
    
    col1, col2 = st.columns(2)
    with col1:
        code = st.text_input("发票代码", placeholder="10 位或 12 位数字", key="invoice_code")
        number = st.text_input("发票号码", placeholder="8 位数字", key="invoice_number")
        date = st.date_input("开票日期", value=datetime.now(), key="invoice_date")
        amount = st.number_input("金额", min_value=0.0, step=0.01, key="invoice_amount")
    
    with col2:
        inv_type = st.selectbox("发票类型", ["专用发票", "普通发票", "电子发票"], key="invoice_type")
        supplier = st.text_input("销售方", key="invoice_supplier")
        buyer = st.text_input("购买方", key="invoice_buyer")
        status = st.selectbox("认证状态", ["未认证", "已认证", "已退票"], key="invoice_status")
    
    if st.button("保存发票", type="primary", key="save_invoice"):
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
                # 清除缓存，强制刷新
                if 'invoice_page_cache' in st.session_state:
                    del st.session_state.invoice_page_cache
            except sqlite3.IntegrityError:
                st.error("该发票已存在！")
            finally:
                conn.close()
        else:
            st.error("请填写必填项：发票代码、发票号码、金额")

with tab2:
    st.subheader("发票查询")
    
    # ========== 性能优化：懒加载 + 分页 ==========
    col1, col2 = st.columns([3, 1])
    with col1:
        search_code = st.text_input("搜索发票代码或号码", key="invoice_search")
    with col2:
        page_size = st.selectbox("每页显示", [20, 50, 100], index=1, key="invoice_page_size")
    
    # 分页参数
    if 'invoice_page' not in st.session_state:
        st.session_state.invoice_page = 1
    
    # 构建查询条件
    where_clause = ""
    params = ()
    if search_code:
        where_clause = "WHERE (code LIKE ? OR number LIKE ?)"
        params = (f'%{search_code}%', f'%{search_code}%')
    
    # 性能优化：使用缓存查询数据
    try:
        # 先获取总记录数
        conn = get_connection()
        count_query = f"SELECT COUNT(*) FROM invoice {where_clause}"
        total_records = conn.execute(count_query, params).fetchone()[0]
        
        # 获取完整数据集（使用缓存）
        if where_clause:
            invoice_df = get_invoices_cached(where_clause, params)
        else:
            invoice_df = get_invoices_cached()
        
        conn.close()
        
        # 在内存中进行分页
        if not invoice_df.empty:
            start_idx = (st.session_state.invoice_page - 1) * page_size
            end_idx = start_idx + page_size
            invoice_data = invoice_df.iloc[start_idx:end_idx].to_dict('records')
            df = pd.DataFrame(invoice_data)
            st.dataframe(df, use_container_width=True, hide_index=True)
            
            # 分页控件
            render_pagination(total_records, st.session_state.invoice_page, page_size)
            
            # 页码切换
            page_key = f"page_select_{page_size}"
            if page_key in st.session_state:
                new_page = st.session_state[page_key]
                if new_page != st.session_state.invoice_page:
                    st.session_state.invoice_page = new_page
                    st.rerun()
            
            st.metric("发票总数", total_records)
        else:
            st.info("暂无发票数据")
    
    except Exception as e:
        st.error(f"查询失败：{e}")
        # 降级：直接查询（不推荐）
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
            st.warning("数据量较大，已自动限制显示前 100 条")
            st.dataframe(df.head(100), use_container_width=True)

with tab3:
    st.subheader("批量导入发票")
    
    uploaded_file = st.file_uploader("上传 Excel 文件", type=['xlsx', 'xls'], key="invoice_upload")
    
    if uploaded_file:
        from utils.query_optimizer import batch_insert
        
        try:
            df_upload = pd.read_excel(uploaded_file)
            st.write(f"预览数据：{len(df_upload)} 行")
            st.dataframe(df_upload.head(), use_container_width=True)
            
            if st.button("确认导入", key="confirm_import"):
                # 准备批量插入数据
                columns = ['code', 'number', 'date', 'amount', 'type', 'supplier', 'buyer', 'status']
                data = []
                for _, row in df_upload.iterrows():
                    data.append((
                        str(row.get('code', '')),
                        str(row.get('number', '')),
                        row.get('date', datetime.now().strftime('%Y-%m-%d')),
                        float(row.get('amount', 0)),
                        row.get('type', '普通发票'),
                        row.get('supplier', ''),
                        row.get('buyer', ''),
                        row.get('status', '未认证')
                    ))
                
                with st.spinner("正在导入数据..."):
                    count = batch_insert('invoice', columns, data, batch_size=500)
                
                st.success(f"成功导入 {count} 条发票记录")
                # 清除缓存
                if 'invoice_page_cache' in st.session_state:
                    del st.session_state.invoice_page_cache
        except Exception as e:
            st.error(f"导入失败：{e}")
