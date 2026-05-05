"""
🏦 银行对账 - 自动匹配银行流水与企业账务
"""
import streamlit as st
from utils.page_helper import init_page
import pandas as pd

# ========== 性能优化 ==========
# Session State: 保存用户输入
if '_session_init' not in st.session_state:
    st.session_state._session_init = True

from datetime import datetime, timedelta
from utils.database import get_connection, init_db
from utils.constants import Tolerance, DateTolerance, CacheTTL
from difflib import SequenceMatcher

init_db()
init_page("02_银行对账")

st.title("🏦 银行对账")

# ========== 性能优化：缓存对账结果 ==========
@st.cache_data(ttl=CacheTTL.BANK_RECONCILIATION)  # 30 分钟缓存
def get_reconciliation_cached(tolerance: float, date_tol: int):
    """执行银行对账匹配（带缓存）"""
    conn = get_connection()
    bank_df = pd.read_sql_query("SELECT * FROM bank_statement", conn)
    company_df = pd.read_sql_query("SELECT * FROM company_statement", conn)
    conn.close()
    
    if bank_df.empty or company_df.empty:
        return [], [], []
    
    matches = []
    unmatched_bank = []
    unmatched_company = []
    matched_bank_ids = set()
    matched_company_ids = set()
    
    for _, bank in bank_df.iterrows():
        matched = False
        for _, company in company_df.iterrows():
            if company['id'] in matched_company_ids:
                continue
            
            amount_match = abs(bank['amount'] - company['amount']) <= tolerance
            bank_date = datetime.strptime(bank['trans_date'], '%Y-%m-%d')
            comp_date = datetime.strptime(company['trans_date'], '%Y-%m-%d')
            date_match = abs((bank_date - comp_date).days) <= date_tol
            
            similarity = SequenceMatcher(None, bank['summary'], company['summary']).ratio()
            name_similarity = SequenceMatcher(None, bank['counterparty'], company['counterparty']).ratio()
            
            if amount_match and date_match and (similarity > 0.6 or name_similarity > 0.6):
                matches.append({
                    '银行日期': bank['trans_date'],
                    '银行金额': bank['amount'],
                    '银行对方': bank['counterparty'],
                    '企业日期': company['trans_date'],
                    '企业金额': company['amount'],
                    '企业对方': company['counterparty'],
                    '匹配度': f"{(similarity + name_similarity) / 2 * 100:.1f}%"
                })
                matched_bank_ids.add(bank['id'])
                matched_company_ids.add(company['id'])
                matched = True
                break
        
        if not matched:
            unmatched_bank.append(bank.to_dict())
    
    for _, company in company_df.iterrows():
        if company['id'] not in matched_company_ids:
            unmatched_company.append(company.to_dict())
    
    return matches, unmatched_bank, unmatched_company

tab1, tab2, tab3 = st.tabs(["银行流水", "企业账务", "智能对账"])

with tab1:
    st.subheader("银行流水导入")
    
    uploaded_file = st.file_uploader("上传银行流水 Excel", type=['xlsx', 'xls'], key="bank")
    
    if uploaded_file:
        df = pd.read_excel(uploaded_file)
        st.dataframe(df.head())
        
        conn = get_connection()
        for _, row in df.iterrows():
            conn.execute(
                """INSERT INTO bank_statement (trans_date, trans_type, amount, counterparty, summary)
                   VALUES (?, ?, ?, ?, ?)""",
                (row.get('日期', datetime.now().strftime('%Y-%m-%d')),
                 row.get('类型', '转账'), row.get('金额', 0),
                 row.get('对方户名', ''), row.get('摘要', ''))
            )
        conn.commit()
        conn.close()
        st.success("银行流水导入成功")

with tab2:
    st.subheader("企业账务导入")
    
    uploaded_file = st.file_uploader("上传企业账务 Excel", type=['xlsx', 'xls'], key="company")
    
    if uploaded_file:
        df = pd.read_excel(uploaded_file)
        st.dataframe(df.head())
        
        conn = get_connection()
        for _, row in df.iterrows():
            conn.execute(
                """INSERT INTO company_statement (trans_date, trans_type, amount, counterparty, summary)
                   VALUES (?, ?, ?, ?, ?)""",
                (row.get('日期', datetime.now().strftime('%Y-%m-%d')),
                 row.get('类型', '转账'), row.get('金额', 0),
                 row.get('对方单位', ''), row.get('摘要', ''))
            )
        conn.commit()
        conn.close()
        st.success("企业账务导入成功")

with tab3:
    st.subheader("智能对账匹配")
    
    tolerance = st.number_input("金额容差范围", value=Tolerance.DEFAULT, step=0.01)
    date_tolerance = st.number_input("日期容差 (天)", value=DateTolerance.DEFAULT, min_value=0)
    
    # 性能优化：使用缓存的对账结果
    if st.button("开始对账", type="primary"):
        # 使用缓存函数获取对账结果（30 分钟缓存）
        matches, unmatched_bank, unmatched_company = get_reconciliation_cached(
            float(tolerance), 
            int(date_tolerance)
        )
        
        st.success(f"找到 {len(matches)} 对匹配记录")
        
        if matches:
            st.subheader("✅ 匹配结果")
            st.dataframe(pd.DataFrame(matches), use_container_width=True)
            
            # 导出匹配结果
            csv = pd.DataFrame(matches).to_csv(index=False, encoding='utf-8-sig')
            st.download_button(
                label="📥 下载匹配结果 CSV",
                data=csv,
                file_name=f"对账匹配结果_{datetime.now().strftime('%Y%m%d')}.csv",
                mime="text/csv"
            )
            
            # 统计信息
            st.divider()
            col1, col2, col3 = st.columns(3)
            conn = get_connection()
            bank_total = conn.execute("SELECT COUNT(*) FROM bank_statement").fetchone()[0]
            company_total = conn.execute("SELECT COUNT(*) FROM company_statement").fetchone()[0]
            conn.close()
            
            col1.metric("银行流水总数", bank_total)
            col2.metric("企业账务总数", company_total)
            col3.metric("已匹配", len(matches))
        
        if unmatched_bank:
            st.subheader(f"⚠️ 银行未达账项 ({len(unmatched_bank)}条)")
            st.dataframe(pd.DataFrame(unmatched_bank), use_container_width=True)
        
        if unmatched_company:
            st.subheader(f"⚠️ 企业未达账项 ({len(unmatched_company)}条)")
            st.dataframe(pd.DataFrame(unmatched_company), use_container_width=True)
