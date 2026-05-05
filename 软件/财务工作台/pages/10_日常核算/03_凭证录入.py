"""
📝 凭证录入 - 会计凭证录入与管理
"""
import streamlit as st
import pandas as pd

# ========== 性能优化 ==========
# Session State: 保存用户输入
if '_session_init' not in st.session_state:
    st.session_state._session_init = True

from datetime import datetime
from utils.database import get_connection, init_db

st.set_page_config(page_title="凭证录入", page_icon="📝", layout="wide")
init_db()

st.title("📝 凭证录入")

tab1, tab2 = st.tabs(["录入凭证", "凭证查询"])

SUBJECTS = {
    '1001': '库存现金',
    '1002': '银行存款',
    '1122': '应收账款',
    '1221': '其他应收款',
    '1405': '库存商品',
    '1601': '固定资产',
    '2001': '短期借款',
    '2202': '应付账款',
    '2211': '应付职工薪酬',
    '2221': '应交税费',
    '6001': '主营业务收入',
    '6401': '主营业务成本',
    '6601': '销售费用',
    '6602': '管理费用',
    '6603': '财务费用',
}

with tab1:
    st.subheader("新增凭证")
    
    col1, col2 = st.columns(2)
    with col1:
        voucher_no = st.text_input("凭证号", placeholder="记 -001")
        trans_date = st.date_input("日期", value=datetime.now(), key="voucher_date")
        attachment_count = st.number_input("附件数", min_value=0, value=0)
    
    with col2:
        summary = st.text_input("摘要")
        created_by = st.text_input("制单人", value="admin")
    
    st.divider()
    
    st.subheader("分录明细")
    
    if 'entries' not in st.session_state:
        st.session_state.entries = []
    
    entry_col1, entry_col2, entry_col3, entry_col4 = st.columns(4)
    with entry_col1:
        entry_type = st.selectbox("方向", ["借方", "贷方"], key="entry_type")
    with entry_col2:
        subject_code = st.selectbox("科目代码", list(SUBJECTS.keys()), key="entry_code")
    with entry_col3:
        entry_amount = st.number_input("金额", min_value=0.01, step=0.01, key="entry_amount")
    with entry_col4:
        if st.button("添加分录", key="add_entry"):
            st.session_state.entries.append({
                'type': entry_type,
                'code': subject_code,
                'name': SUBJECTS[subject_code],
                'amount': entry_amount
            })
    
    if st.session_state.entries:
        st.dataframe(pd.DataFrame(st.session_state.entries), use_container_width=True)
        
        debit_total = sum(e['amount'] for e in st.session_state.entries if e['type'] == '借方')
        credit_total = sum(e['amount'] for e in st.session_state.entries if e['type'] == '贷方')
        
        col1, col2, col3 = st.columns(3)
        col1.metric("借方合计", f"¥{debit_total:,.2f}")
        col2.metric("贷方合计", f"¥{credit_total:,.2f}")
        
        if debit_total == credit_total and debit_total > 0:
            col3.success("✅ 借贷平衡")
        else:
            col3.error(f"❌ 不平衡 (差异：¥{debit_total - credit_total:,.2f})")
        
        if st.button("保存凭证", type="primary"):
            if voucher_no and st.session_state.entries and debit_total == credit_total:
                conn = get_connection()
                cursor = conn.cursor()
                cursor.execute(
                    """INSERT INTO voucher (voucher_no, trans_date, attachment_count, summary, created_by)
                       VALUES (?, ?, ?, ?, ?)""",
                    (voucher_no, trans_date.strftime('%Y-%m-%d'), attachment_count, summary, created_by)
                )
                voucher_id = cursor.lastrowid
                
                for entry in st.session_state.entries:
                    cursor.execute(
                        """INSERT INTO voucher_entry (voucher_id, entry_type, subject_code, subject_name, amount)
                           VALUES (?, ?, ?, ?, ?)""",
                        (voucher_id, entry['type'], entry['code'], entry['name'], entry['amount'])
                    )
                
                conn.commit()
                conn.close()
                st.success("凭证保存成功！")
                st.session_state.entries = []
                st.rerun()
    
    if st.button("清空分录"):
        st.session_state.entries = []
        st.rerun()

with tab2:
    st.subheader("凭证查询")
    
    search = st.text_input("搜索凭证号或摘要")
    
    conn = get_connection()
    
    if search:
        vouchers = pd.read_sql_query(
            """SELECT DISTINCT v.* FROM voucher v
               JOIN voucher_entry ve ON v.id = ve.voucher_id
               WHERE v.voucher_no LIKE ? OR v.summary LIKE ? OR ve.subject_name LIKE ?
               ORDER BY v.trans_date DESC""",
            conn, params=(f'%{search}%', f'%{search}%', f'%{search}%')
        )
    else:
        vouchers = pd.read_sql_query("SELECT * FROM voucher ORDER BY trans_date DESC", conn)
    
    conn.close()
    
    if not vouchers.empty:
        st.dataframe(vouchers, use_container_width=True)
        
        selected_voucher = st.selectbox("查看凭证详情", vouchers['voucher_no'].tolist())
        
        if selected_voucher:
            conn = get_connection()
            entries = pd.read_sql_query(
                """SELECT entry_type, subject_code, subject_name, amount FROM voucher_entry
                   WHERE voucher_id = (SELECT id FROM voucher WHERE voucher_no = ?)""",
                conn, params=(selected_voucher,)
            )
            conn.close()
            
            if not entries.empty:
                st.dataframe(entries, use_container_width=True)
