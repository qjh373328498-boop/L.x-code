"""
🏦 银行对账 - 自动匹配银行流水与企业账务
"""
import streamlit as st
import pandas as pd

# ========== 性能优化 ==========
# Session State: 保存用户输入
if '_session_init' not in st.session_state:
    st.session_state._session_init = True

from datetime import datetime, timedelta
from utils.database import get_connection, init_db
from difflib import SequenceMatcher

st.set_page_config(page_title="银行对账", page_icon="🏦", layout="wide")
init_db()

st.title("🏦 银行对账")

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
    
    tolerance = st.number_input("金额容差范围", value=0.01, step=0.01)
    date_tolerance = st.number_input("日期容差 (天)", value=3, min_value=0)
    
    if st.button("开始对账", type="primary"):
        conn = get_connection()
        
        bank_df = pd.read_sql_query("SELECT * FROM bank_statement", conn)
        company_df = pd.read_sql_query("SELECT * FROM company_statement", conn)
        conn.close()
        
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
                date_match = abs((bank_date - comp_date).days) <= date_tolerance
                
                similarity = SequenceMatcher(None, bank.get('summary', ''), company.get('summary', '')).ratio()
                name_similarity = SequenceMatcher(None, bank.get('counterparty', ''), company.get('counterparty', '')).ratio()
                
                if amount_match and date_match and (similarity > 0.6 or name_similarity > 0.6):
                    matches.append({
                        '银行日期': bank['trans_date'],
                        '银行金额': bank['amount'],
                        '银行对方': bank.get('counterparty', ''),
                        '银行摘要': bank.get('summary', ''),
                        '企业日期': company['trans_date'],
                        '企业金额': company['amount'],
                        '企业对方': company.get('counterparty', ''),
                        '企业摘要': company.get('summary', ''),
                        '匹配度': f"{(similarity + name_similarity) / 2 * 100:.1f}%"
                    })
                    matched_bank_ids.add(bank['id'])
                    matched_company_ids.add(company['id'])
                    matched = True
                    break
            
            if not matched:
                unmatched_bank.append(bank)
        
        for _, company in company_df.iterrows():
            if company['id'] not in matched_company_ids:
                unmatched_company.append(company)
        
        st.success(f"找到 {len(matches)} 对匹配记录")
        
        if matches:
            st.subheader("✅ 匹配结果")
            st.dataframe(pd.DataFrame(matches), use_container_width=True)
        
        if unmatched_bank:
            st.subheader(f"⚠️ 银行未达账项 ({len(unmatched_bank)}条)")
            st.dataframe(pd.DataFrame(unmatched_bank), use_container_width=True)
        
        if unmatched_company:
            st.subheader(f"⚠️ 企业未达账项 ({len(unmatched_company)}条)")
            st.dataframe(pd.DataFrame(unmatched_company), use_container_width=True)
