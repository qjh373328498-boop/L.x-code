"""
财务工作台 v2.0 - 单页应用 SPA 方案（完整版）
所有页面整合到一个文件中，用 Tabs + Radio 分组
"""
import streamlit as st
import hashlib
import pandas as pd
import sqlite3
from datetime import datetime, timedelta
from pathlib import Path
import os
import json
from io import BytesIO

# ==================== 页面配置 ====================
st.set_page_config(
    page_title="财务工作台",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ==================== 初始化 ====================
if 'authenticated' not in st.session_state:
    st.session_state.authenticated = False
if 'username' not in st.session_state:
    st.session_state.username = None
if 'current_section' not in st.session_state:
    st.session_state.current_section = "首页"

# ==================== 数据库工具 ====================
DATA_DIR = Path(__file__).parent / "data"
DATA_DIR.mkdir(exist_ok=True)
DB_PATH = DATA_DIR / "finance.db"

def get_connection():
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_connection()
    cursor = conn.cursor()
    
    # 发票表
    cursor.execute("""CREATE TABLE IF NOT EXISTS invoice (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        code TEXT NOT NULL, number TEXT NOT NULL, date TEXT NOT NULL,
        amount REAL NOT NULL, type TEXT DEFAULT 'special',
        supplier TEXT, buyer TEXT, status TEXT DEFAULT 'normal',
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP, UNIQUE(code, number)
    )""")
    
    # 银行流水表
    cursor.execute("""CREATE TABLE IF NOT EXISTS bank_statement (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        trans_date TEXT NOT NULL, trans_type TEXT NOT NULL,
        amount REAL NOT NULL, balance REAL, counterparty TEXT,
        summary TEXT, created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )""")
    
    # 企业账务表
    cursor.execute("""CREATE TABLE IF NOT EXISTS company_statement (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        trans_date TEXT NOT NULL, trans_type TEXT NOT NULL,
        amount REAL NOT NULL, counterparty TEXT, summary TEXT,
        voucher_no TEXT, created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )""")
    
    # 凭证表
    cursor.execute("""CREATE TABLE IF NOT EXISTS voucher (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        voucher_no TEXT NOT NULL, trans_date TEXT NOT NULL,
        attachment_count INTEGER DEFAULT 0, summary TEXT,
        created_by TEXT, created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )""")
    
    # 凭证分录表
    cursor.execute("""CREATE TABLE IF NOT EXISTS voucher_entry (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        voucher_id INTEGER NOT NULL, entry_type TEXT NOT NULL,
        subject_code TEXT NOT NULL, subject_name TEXT NOT NULL,
        amount REAL NOT NULL, FOREIGN KEY (voucher_id) REFERENCES voucher(id)
    )""")
    
    # 应收应付表
    cursor.execute("""CREATE TABLE IF NOT EXISTS ar_ap (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        type TEXT NOT NULL, counterparty TEXT NOT NULL,
        amount REAL NOT NULL, date TEXT NOT NULL,
        due_date TEXT, summary TEXT, status TEXT DEFAULT 'pending',
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )""")
    
    # 财务指标表
    cursor.execute("""CREATE TABLE IF NOT EXISTS financial_metrics (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        period TEXT NOT NULL, metric_name TEXT NOT NULL,
        value REAL NOT NULL, unit TEXT DEFAULT '元',
        UNIQUE(period, metric_name)
    )""")
    
    # 日历事件表
    cursor.execute("""CREATE TABLE IF NOT EXISTS calendar_event (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT NOT NULL, event_date TEXT NOT NULL,
        event_type TEXT NOT NULL, description TEXT,
        is_recurring BOOLEAN DEFAULT FALSE,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )""")
    
    conn.commit()
    conn.close()

# ==================== 用户认证 ====================
def sha256_hash(password: str) -> str:
    return hashlib.sha256(password.encode()).hexdigest()

def check_user(username: str, password: str) -> bool:
    users = {
        'admin': sha256_hash('703102'),
        'finance': sha256_hash('finance123'),
        'intern': sha256_hash('intern123'),
    }
    return username in users and users[username] == sha256_hash(password)

def login():
    st.title("🔐 用户登录")
    col1, col2 = st.columns([1, 2])
    with col1:
        username = st.text_input("用户名")
        password = st.text_input("密码", type="password")
        if st.button("🔑 登录", type="primary", use_container_width=True):
            if check_user(username, password):
                st.session_state.authenticated = True
                st.session_state.username = username
                st.rerun()
            else:
                st.error("用户名或密码错误")
    with col2:
        st.info("**默认账户**\n\n管理员：admin / 703102\n财务专员：finance / finance123\n实习生：intern / intern123")

def logout():
    with st.sidebar:
        if st.button("🔓 退出登录", use_container_width=True):
            st.session_state.authenticated = False
            st.session_state.username = None
            st.session_state.current_section = "首页"
            st.rerun()

# ==================== 页面函数 - 首页 ====================
def show_home():
    st.title("📊 财务工作台")
    st.markdown(f"欢迎回来，**{st.session_state.username}**！")
    st.markdown("---")
    st.markdown("""
### 📋 功能模块

**📝 日常核算** - 发票管理、银行对账、凭证录入、科目余额表、应收应付、纳税申报

**📊 财务分析** - 财务比率分析、杜邦分析、行业对标、资金诊断、预算分析、智能透视分析

**🏭 数据工厂** - 文档解析、批量解析、数据治理、合规风控

**💼 决策支持** - 金融测算、本量利分析、报表美化

**🧰 办公工具** - 财务日历、快捷工具箱、模板中心、增强功能、帮助中心
""")

# ==================== 页面函数 - 日常核算 ====================
def show_invoice():
    st.title("📄 发票管理")
    
    if 'invoice_page' not in st.session_state:
        st.session_state.invoice_page = 1
    
    tab1, tab2, tab3 = st.tabs(["录入发票", "发票查询", "批量导入"])
    
    with tab1:
        st.subheader("录入新发票")
        col1, col2 = st.columns(2)
        with col1:
            code = st.text_input("发票代码", key="inv_code")
            number = st.text_input("发票号码", key="inv_number")
            date = st.date_input("开票日期", value=datetime.now(), key="inv_date")
            amount = st.number_input("金额", min_value=0.0, step=0.01, key="inv_amount")
        with col2:
            inv_type = st.selectbox("发票类型", ["专用发票", "普通电子发票", "普通纸质发票"], key="inv_type")
            supplier = st.text_input("销售方", key="inv_supplier")
            buyer = st.text_input("购买方", key="inv_buyer")
            status = st.selectbox("认证状态", ["已认证", "未认证"], key="inv_status")
        if st.button("💾 保存发票", key="save_inv", type="primary"):
            if code and number and amount:
                conn = get_connection()
                cursor = conn.cursor()
                try:
                    cursor.execute("INSERT INTO invoice (code, number, date, amount, type, supplier, buyer, status) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
                        (code, number, date.strftime('%Y-%m-%d'), amount, inv_type, supplier, buyer, status))
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
        search_code = st.text_input("搜索发票代码或号码", key="invoice_search")
        page_size = st.selectbox("每页显示", [20, 50, 100], index=1, key="invoice_page_size")
        
        where_clause = ""
        params = ()
        if search_code:
            where_clause = "WHERE (code LIKE ? OR number LIKE ?)"
            params = (f'%{search_code}%', f'%{search_code}%')
        
        conn = get_connection()
        count_query = f"SELECT COUNT(*) FROM invoice {where_clause}"
        total_records = conn.execute(count_query, params).fetchone()[0]
        
        query = f"SELECT * FROM invoice {where_clause} ORDER BY date DESC LIMIT ? OFFSET ?"
        offset = (st.session_state.invoice_page - 1) * page_size
        params_with_limit = params + (page_size, offset)
        df = pd.read_sql_query(query, conn, params=params_with_limit)
        conn.close()
        
        if not df.empty:
            st.dataframe(df, use_container_width=True, hide_index=True)
            col1, col2, col3 = st.columns([1, 1, 2])
            with col1:
                st.metric("发票总数", total_records)
            with col2:
                if st.button("上一页", disabled=st.session_state.invoice_page == 1, key="prev_page"):
                    st.session_state.invoice_page -= 1
                    st.rerun()
                if st.button("下一页", disabled=(st.session_state.invoice_page * page_size) >= total_records, key="next_page"):
                    st.session_state.invoice_page += 1
                    st.rerun()
        else:
            st.info("暂无发票数据")
    
    with tab3:
        st.subheader("批量导入发票")
        uploaded_file = st.file_uploader("上传 Excel 文件", type=['xlsx', 'xls'], key="invoice_upload")
        if uploaded_file:
            try:
                df_upload = pd.read_excel(uploaded_file)
                st.write(f"预览数据：{len(df_upload)} 行")
                st.dataframe(df_upload.head(), use_container_width=True)
                if st.button("确认导入", key="confirm_import"):
                    conn = get_connection()
                    cursor = conn.cursor()
                    count = 0
                    for _, row in df_upload.iterrows():
                        try:
                            cursor.execute("INSERT INTO invoice (code, number, date, amount, type, supplier, buyer, status) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
                                (str(row.get('code', '')), str(row.get('number', '')), row.get('date', datetime.now().strftime('%Y-%m-%d')),
                                 float(row.get('amount', 0)), row.get('type', '专用发票'), row.get('supplier', ''), row.get('buyer', ''), row.get('status', '未认证')))
                            count += 1
                        except sqlite3.IntegrityError:
                            pass
                    conn.commit()
                    conn.close()
                    st.success(f"成功导入 {count} 条发票记录")
            except Exception as e:
                st.error(f"导入失败：{e}")

def show_bank():
    st.title("🏦 银行对账")
    tab1, tab2, tab3 = st.tabs(["银行流水", "企业账务", "智能对账"])
    
    with tab1:
        st.subheader("银行流水导入")
        uploaded_file = st.file_uploader("上传银行流水 Excel", type=['xlsx', 'xls'], key="bank_file")
        if uploaded_file:
            try:
                df = pd.read_excel(uploaded_file)
                st.dataframe(df.head())
                if st.button("确认导入银行流水", key="import_bank"):
                    conn = get_connection()
                    for _, row in df.iterrows():
                        conn.execute("INSERT INTO bank_statement (trans_date, trans_type, amount, balance, counterparty, summary) VALUES (?, ?, ?, ?, ?, ?)",
                            (row.get('日期', datetime.now().strftime('%Y-%m-%d')), row.get('类型', '转账'), row.get('金额', 0),
                             row.get('余额', None), row.get('对方户名', ''), row.get('摘要', '')))
                    conn.commit()
                    conn.close()
                    st.success("银行流水导入成功")
            except Exception as e:
                st.error(f"导入失败：{e}")
    
    with tab2:
        st.subheader("企业账务导入")
        uploaded_file = st.file_uploader("上传企业账务 Excel", type=['xlsx', 'xls'], key="company_file")
        if uploaded_file:
            try:
                df = pd.read_excel(uploaded_file)
                st.dataframe(df.head())
                if st.button("确认导入企业账务", key="import_company"):
                    conn = get_connection()
                    for _, row in df.iterrows():
                        conn.execute("INSERT INTO company_statement (trans_date, trans_type, amount, counterparty, summary) VALUES (?, ?, ?, ?, ?)",
                            (row.get('日期', datetime.now().strftime('%Y-%m-%d')), row.get('类型', '转账'), row.get('金额', 0),
                             row.get('对方单位', ''), row.get('摘要', '')))
                    conn.commit()
                    conn.close()
                    st.success("企业账务导入成功")
            except Exception as e:
                st.error(f"导入失败：{e}")
    
    with tab3:
        st.subheader("智能对账匹配")
        tolerance = st.number_input("金额容差范围", value=0.01, step=0.01)
        date_tolerance = st.number_input("日期容差 (天)", value=3, min_value=0)
        
        if st.button("开始对账", type="primary"):
            conn = get_connection()
            bank_df = pd.read_sql_query("SELECT * FROM bank_statement", conn)
            company_df = pd.read_sql_query("SELECT * FROM company_statement", conn)
            conn.close()
            
            if bank_df.empty or company_df.empty:
                st.warning("请先导入银行流水和企业账务数据")
            else:
                from difflib import SequenceMatcher
                matches = []
                matched_bank_ids = set()
                matched_company_ids = set()
                
                for _, bank in bank_df.iterrows():
                    for _, company in company_df.iterrows():
                        if company['id'] in matched_company_ids:
                            continue
                        amount_match = abs(bank['amount'] - company['amount']) <= tolerance
                        bank_date = datetime.strptime(bank['trans_date'], '%Y-%m-%d')
                        comp_date = datetime.strptime(company['trans_date'], '%Y-%m-%d')
                        date_match = abs((bank_date - comp_date).days) <= date_tolerance
                        similarity = SequenceMatcher(None, str(bank['summary']), str(company['summary'])).ratio()
                        name_similarity = SequenceMatcher(None, str(bank.get('counterparty', '')), str(company.get('counterparty', ''))).ratio()
                        
                        if amount_match and date_match and (similarity > 0.6 or name_similarity > 0.6):
                            matches.append({
                                '银行日期': bank['trans_date'], '银行金额': bank['amount'], '银行对方': bank.get('counterparty', ''),
                                '企业日期': company['trans_date'], '企业金额': company['amount'], '企业对方': company.get('counterparty', ''),
                                '匹配度': f"{(similarity + name_similarity) / 2 * 100:.1f}%"
                            })
                            matched_bank_ids.add(bank['id'])
                            matched_company_ids.add(company['id'])
                            break
                
                st.success(f"找到 {len(matches)} 对匹配记录")
                if matches:
                    st.dataframe(pd.DataFrame(matches), use_container_width=True)
                col1, col2, col3 = st.columns(3)
                col1.metric("银行流水总数", len(bank_df))
                col2.metric("企业账务总数", len(company_df))
                col3.metric("已匹配", len(matches))

def show_voucher():
    st.title("📝 凭证录入")
    SUBJECTS = {
        '1001': '库存现金', '1002': '银行存款', '1122': '应收账款', '1221': '其他应收款',
        '1405': '库存商品', '1601': '固定资产', '2001': '短期借款', '2202': '应付账款',
        '2211': '应付职工薪酬', '2221': '应交税费', '6001': '主营业务收入', '6401': '主营业务成本',
        '6601': '销售费用', '6602': '管理费用', '6603': '财务费用',
    }
    
    if 'entries' not in st.session_state:
        st.session_state.entries = []
    
    tab1, tab2 = st.tabs(["录入凭证", "凭证查询"])
    
    with tab1:
        st.subheader("新增凭证")
        col1, col2 = st.columns(2)
        with col1:
            voucher_no = st.text_input("凭证号", key="voucher_no")
            trans_date = st.date_input("日期", value=datetime.now(), key="voucher_date")
            attachment_count = st.number_input("附件数", min_value=0, value=0, key="voucher_attach")
        with col2:
            summary = st.text_input("摘要", key="voucher_summary")
            created_by = st.text_input("制单人", value=st.session_state.username or "admin", key="voucher_user")
        
        st.divider()
        st.subheader("分录明细")
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            entry_type = st.selectbox("方向", ["借方", "贷方"], key="entry_type")
        with col2:
            subject_code = st.selectbox("科目代码", list(SUBJECTS.keys()), key="entry_code")
        with col3:
            entry_amount = st.number_input("金额", min_value=0.01, step=0.01, key="entry_amount")
        with col4:
            if st.button("添加分录", key="add_entry"):
                st.session_state.entries.append({
                    'type': entry_type, 'code': subject_code, 'name': SUBJECTS[subject_code], 'amount': entry_amount
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
                    cursor.execute("INSERT INTO voucher (voucher_no, trans_date, attachment_count, summary, created_by) VALUES (?, ?, ?, ?, ?)",
                        (voucher_no, trans_date.strftime('%Y-%m-%d'), attachment_count, summary, created_by))
                    voucher_id = cursor.lastrowid
                    for entry in st.session_state.entries:
                        cursor.execute("INSERT INTO voucher_entry (voucher_id, entry_type, subject_code, subject_name, amount) VALUES (?, ?, ?, ?, ?)",
                            (voucher_id, entry['type'], entry['code'], entry['name'], entry['amount']))
                    conn.commit()
                    conn.close()
                    st.success("凭证保存成功！")
                    st.session_state.entries = []
                    st.rerun()
        
        if st.button("清空分录", key="clear_entries"):
            st.session_state.entries = []
            st.rerun()
    
    with tab2:
        st.subheader("凭证查询")
        search = st.text_input("搜索凭证号或摘要", key="voucher_search")
        conn = get_connection()
        if search:
            vouchers = pd.read_sql_query(
                """SELECT DISTINCT v.* FROM voucher v JOIN voucher_entry ve ON v.id = ve.voucher_id
                   WHERE v.voucher_no LIKE ? OR v.summary LIKE ? OR ve.subject_name LIKE ?
                   ORDER BY v.trans_date DESC""", conn, params=(f'%{search}%', f'%{search}%', f'%{search}%'))
        else:
            vouchers = pd.read_sql_query("SELECT * FROM voucher ORDER BY trans_date DESC", conn)
        conn.close()
        if not vouchers.empty:
            st.dataframe(vouchers, use_container_width=True)
            selected_voucher = st.selectbox("查看凭证详情", vouchers['voucher_no'].tolist(), key="select_voucher")
            if selected_voucher:
                conn = get_connection()
                entries = pd.read_sql_query(
                    """SELECT entry_type, subject_code, subject_name, amount FROM voucher_entry
                       WHERE voucher_id = (SELECT id FROM voucher WHERE voucher_no = ?)""", conn, params=(selected_voucher,))
                conn.close()
                if not entries.empty:
                    st.dataframe(entries, use_container_width=True)

def show_balance():
    st.title("📋 科目余额表")
    st.info("科目余额表功能开发中... 请先录入凭证数据")
    
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT ve.subject_code, ve.subject_name,
               SUM(CASE WHEN ve.entry_type = '借方' THEN ve.amount ELSE 0 END) as debit_total,
               SUM(CASE WHEN ve.entry_type = '贷方' THEN ve.amount ELSE 0 END) as credit_total
        FROM voucher_entry ve
        GROUP BY ve.subject_code, ve.subject_name
        ORDER BY ve.subject_code
    """)
    data = cursor.fetchall()
    conn.close()
    
    if data:
        df = pd.DataFrame(data, columns=['科目代码', '科目名称', '借方发生额', '贷方发生额'])
        df['借方发生额'] = df['借方发生额'].apply(lambda x: f"¥{x:,.2f}")
        df['贷方发生额'] = df['贷方发生额'].apply(lambda x: f"¥{x:,.2f}")
        st.dataframe(df, use_container_width=True)
    else:
        st.warning("暂无凭证数据，请先录入凭证")

def show_arap():
    st.title("💰 应收应付管理")
    tab1, tab2, tab3 = st.tabs(["应收账款", "应付账款", "账龄分析"])
    
    with tab1:
        st.subheader("应收账款管理")
        col1, col2 = st.columns(2)
        with col1:
            customer = st.text_input("客户名称", key="ar_customer")
            amount = st.number_input("应收金额", min_value=0.01, key="ar_amount")
            ar_date = st.date_input("应收日期", value=datetime.now(), key="ar_date")
        with col2:
            due_date = st.date_input("到期日期", value=datetime.now() + timedelta(days=30), key="ar_due")
            ar_summary = st.text_input("摘要", key="ar_summary")
        if st.button("添加应收账款", key="add_ar", type="primary"):
            if customer and amount:
                conn = get_connection()
                conn.execute("INSERT INTO ar_ap (type, counterparty, amount, date, due_date, summary, status) VALUES ('AR', ?, ?, ?, ?, ?, 'pending')",
                    (customer, amount, ar_date.strftime('%Y-%m-%d'), due_date.strftime('%Y-%m-%d'), ar_summary))
                conn.commit()
                conn.close()
                st.success("添加成功")
                st.rerun()
        conn = get_connection()
        ar_df = pd.read_sql_query("SELECT * FROM ar_ap WHERE type='AR' ORDER BY date DESC", conn)
        conn.close()
        if not ar_df.empty:
            st.dataframe(ar_df, use_container_width=True)
            st.metric("应收账款总额", f"¥{ar_df['amount'].sum():,.2f}")
    
    with tab2:
        st.subheader("应付账款管理")
        col1, col2 = st.columns(2)
        with col1:
            supplier = st.text_input("供应商名称", key="ap_supplier")
            amount = st.number_input("应付金额", min_value=0.01, key="ap_amount")
            ap_date = st.date_input("应付日期", value=datetime.now(), key="ap_date")
        with col2:
            due_date = st.date_input("到期日期", value=datetime.now() + timedelta(days=30), key="ap_due")
            ap_summary = st.text_input("摘要", key="ap_summary")
        if st.button("添加应付账款", key="add_ap", type="primary"):
            if supplier and amount:
                conn = get_connection()
                conn.execute("INSERT INTO ar_ap (type, counterparty, amount, date, due_date, summary, status) VALUES ('AP', ?, ?, ?, ?, ?, 'pending')",
                    (supplier, amount, ap_date.strftime('%Y-%m-%d'), due_date.strftime('%Y-%m-%d'), ap_summary))
                conn.commit()
                conn.close()
                st.success("添加成功")
                st.rerun()
        conn = get_connection()
        ap_df = pd.read_sql_query("SELECT * FROM ar_ap WHERE type='AP' ORDER BY date DESC", conn)
        conn.close()
        if not ap_df.empty:
            st.dataframe(ap_df, use_container_width=True)
            st.metric("应付账款总额", f"¥{ap_df['amount'].sum():,.2f}")
    
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
                if days_overdue < 0: return '未到期'
                elif days_overdue <= 30: return '1-30 天'
                elif days_overdue <= 60: return '31-60 天'
                elif days_overdue <= 90: return '61-90 天'
                else: return '90 天以上'
            ar_df['账龄'] = ar_df['due_date'].apply(age_category)
            age_summary = ar_df.groupby('账龄')['amount'].sum().reindex(['未到期', '1-30 天', '31-60 天', '61-90 天', '90 天以上'], fill_value=0)
            col1, col2 = st.columns(2)
            col1.write("### 应收账款账龄")
            col1.dataframe(age_summary)
            try:
                import plotly.express as px
                fig = px.pie(values=age_summary.values, names=age_summary.index, title="应收账款账龄分布")
                col2.plotly_chart(fig, use_container_width=True)
            except:
                pass

def show_tax():
    st.title("📑 纳税申报")
    tab1, tab2, tab3 = st.tabs(["增值税", "企业所得税", "个税"])
    
    with tab1:
        st.subheader("增值税计算")
        col1, col2 = st.columns(2)
        with col1:
            sales = st.number_input("不含税销售额", min_value=0.0, step=1000.0, key="sales")
            purchase = st.number_input("不含税采购额", min_value=0.0, step=1000.0, key="purchase")
            tax_rate = st.selectbox("税率", [0.13, 0.09, 0.06, 0.03], key="tax_rate", format_func=lambda x: f"{x*100:.0f}%")
        with col2:
            output_tax = sales * tax_rate
            input_tax = purchase * tax_rate
            payable_tax = output_tax - input_tax
            st.metric("销项税额", f"¥{output_tax:,.2f}")
            st.metric("进项税额", f"¥{input_tax:,.2f}")
            st.metric("应纳增值税", f"¥{max(0, payable_tax):,.2f}")
        if payable_tax < 0:
            st.info(f"留抵税额：¥{abs(payable_tax):,.2f}")
    
    with tab2:
        st.subheader("企业所得税计算")
        col1, col2 = st.columns(2)
        with col1:
            revenue = st.number_input("营业收入", min_value=0.0, step=10000.0, key="erp_rev")
            cogs = st.number_input("营业成本", min_value=0.0, step=10000.0, key="erp_cogs")
            operating_expenses = st.number_input("期间费用", min_value=0.0, step=10000.0, key="erp_exp")
            other_income = st.number_input("其他收益", min_value=0.0, step=10000.0, key="erp_other_inc")
            other_expenses = st.number_input("其他支出", min_value=0.0, step=10000.0, key="erp_other_exp")
        with col2:
            profit_before_tax = revenue - cogs - operating_expenses + other_income - other_expenses
            tax_adjustments = st.number_input("纳税调整金额", value=0.0, step=10000.0, key="tax_adj")
            taxable_income = max(0, profit_before_tax + tax_adjustments)
            is_small = st.checkbox("小型微利企业", value=False, key="is_small")
            if is_small:
                tax_rate = 0.025 if taxable_income <= 1000000 else 0.05 if taxable_income <= 3000000 else 0.25
                tax_desc = "2.5%" if taxable_income <= 1000000 else "5%" if taxable_income <= 3000000 else "25%"
            else:
                tax_rate = 0.25
                tax_desc = "25%"
            income_tax = taxable_income * tax_rate
            st.metric("利润总额", f"¥{profit_before_tax:,.2f}")
            st.metric("应纳税所得额", f"¥{taxable_income:,.2f}")
            st.metric(f"应纳所得税 ({tax_desc})", f"¥{income_tax:,.2f}")
    
    with tab3:
        st.subheader("个人所得税计算")
        monthly_salary = st.number_input("月工资", min_value=0.0, step=1000.0, key="tax_salary")
        social_security = st.number_input("社保公积金个人部分", min_value=0.0, step=100.0, key="tax_social")
        special_deduction = st.number_input("专项附加扣除", min_value=0.0, step=100.0, key="tax_special")
        other_deduction = st.number_input("其他扣除", min_value=0.0, step=100.0, key="tax_other")
        threshold = 5000
        taxable_income = monthly_salary - social_security - threshold - special_deduction - other_deduction
        if taxable_income <= 0:
            tax = 0
            tax_rate_display = "0%"
        elif taxable_income <= 3000:
            tax = taxable_income * 0.03
            tax_rate_display = "3%"
        elif taxable_income <= 12000:
            tax = taxable_income * 0.1 - 210
            tax_rate_display = "10%"
        elif taxable_income <= 25000:
            tax = taxable_income * 0.2 - 1410
            tax_rate_display = "20%"
        elif taxable_income <= 35000:
            tax = taxable_income * 0.25 - 2660
            tax_rate_display = "25%"
        elif taxable_income <= 55000:
            tax = taxable_income * 0.3 - 4410
            tax_rate_display = "30%"
        elif taxable_income <= 80000:
            tax = taxable_income * 0.35 - 7160
            tax_rate_display = "35%"
        else:
            tax = taxable_income * 0.45 - 15160
            tax_rate_display = "45%"
        col1, col2, col3 = st.columns(3)
        col1.metric("应纳税所得额", f"¥{max(0, taxable_income):,.2f}")
        col2.metric("适用税率", tax_rate_display)
        col3.metric("应纳个税", f"¥{tax:,.2f}")
        net_salary = monthly_salary - social_security - tax
        st.metric("税后工资", f"¥{net_salary:,.2f}")

# ==================== 页面函数 - 财务分析 ====================
def show_ratios():
    st.title("📊 财务比率分析")
    tab1, tab2 = st.tabs(["数据录入", "比率分析"])
    
    with tab1:
        st.subheader("录入财务数据")
        col1, col2, col3 = st.columns(3)
        with col1:
            period = st.text_input("期间", placeholder="2024-12", key="fm_period")
            current_assets = st.number_input("流动资产", value=0.0, key="fm_current_assets")
            non_current_assets = st.number_input("非流动资产", value=0.0, key="fm_non_current_assets")
            total_assets = st.number_input("资产总计", value=0.0, key="fm_total_assets")
        with col2:
            current_liabilities = st.number_input("流动负债", value=0.0, key="fm_current_liab")
            non_current_liabilities = st.number_input("非流动负债", value=0.0, key="fm_non_current_liab")
            total_liabilities = st.number_input("负债总计", value=0.0, key="fm_total_liab")
            equity = st.number_input("所有者权益", value=0.0, key="fm_equity")
        with col3:
            revenue = st.number_input("营业收入", value=0.0, key="fm_revenue")
            net_profit = st.number_input("净利润", value=0.0, key="fm_net_profit")
            cogs = st.number_input("营业成本", value=0.0, key="fm_cogs")
            inventory = st.number_input("存货", value=0.0, key="fm_inventory")
            receivables = st.number_input("应收账款", value=0.0, key="fm_receivables")
        
        if st.button("保存数据", type="primary", key="save_fm_data"):
            if period and total_assets > 0:
                conn = get_connection()
                metrics = [
                    (period, '流动资产', current_assets, '元'), (period, '非流动资产', non_current_assets, '元'),
                    (period, '资产总计', total_assets, '元'), (period, '流动负债', current_liabilities, '元'),
                    (period, '非流动负债', non_current_liabilities, '元'), (period, '负债总计', total_liabilities, '元'),
                    (period, '所有者权益', equity, '元'), (period, '营业收入', revenue, '元'),
                    (period, '净利润', net_profit, '元'), (period, '营业成本', cogs, '元'),
                    (period, '存货', inventory, '元'), (period, '应收账款', receivables, '元'),
                ]
                for m in metrics:
                    conn.execute("INSERT OR REPLACE INTO financial_metrics (period, metric_name, value, unit) VALUES (?, ?, ?, ?)", m)
                conn.commit()
                conn.close()
                st.success("数据保存成功")
    
    with tab2:
        st.subheader("财务比率计算")
        conn = get_connection()
        df_all = pd.read_sql_query("SELECT * FROM financial_metrics ORDER BY period DESC", conn)
        conn.close()
        if df_all.empty:
            st.info("暂无数据")
        else:
            latest_period = df_all['period'].max()
            df = df_all[df_all['period'] == latest_period]
            m = dict(zip(df['metric_name'], df['value']))
            current_assets = m.get('流动资产', 0); current_liabilities = m.get('流动负债', 0)
            total_assets = m.get('资产总计', 0); total_liabilities = m.get('负债总计', 0)
            equity = m.get('所有者权益', 0); revenue = m.get('营业收入', 0)
            net_profit = m.get('净利润', 0); cogs = m.get('营业成本', 0)
            inventory = m.get('存货', 0); receivables = m.get('应收账款', 0)
            
            current_ratio = current_assets / current_liabilities if current_liabilities > 0 else 0
            quick_ratio = (current_assets - inventory) / current_liabilities if current_liabilities > 0 else 0
            debt_ratio = total_liabilities / total_assets * 100 if total_assets > 0 else 0
            equity_ratio = equity / total_assets * 100 if total_assets > 0 else 0
            gross_margin = (revenue - cogs) / revenue * 100 if revenue > 0 else 0
            net_margin = net_profit / revenue * 100 if revenue > 0 else 0
            roa = net_profit / total_assets * 100 if total_assets > 0 else 0
            roe = net_profit / equity * 100 if equity > 0 else 0
            inventory_turnover = cogs / inventory if inventory > 0 else 0
            receivables_turnover = revenue / receivables if receivables > 0 else 0
            asset_turnover = revenue / total_assets if total_assets > 0 else 0
            
            st.subheader("💧 偿债能力")
            col1, col2, col3, col4 = st.columns(4)
            col1.metric("流动比率", f"{current_ratio:.2f}", "标准值：2.0")
            col2.metric("速动比率", f"{quick_ratio:.2f}", "标准值：1.0")
            col3.metric("资产负债率", f"{debt_ratio:.1f}%", "标准值：<60%")
            col4.metric("权益比率", f"{equity_ratio:.1f}%", "标准值：>40%")
            st.divider()
            st.subheader("💰 盈利能力")
            col1, col2, col3, col4 = st.columns(4)
            col1.metric("毛利率", f"{gross_margin:.1f}%")
            col2.metric("净利率", f"{net_margin:.1f}%")
            col3.metric("ROA", f"{roa:.1f}%")
            col4.metric("ROE", f"{roe:.1f}%")
            st.divider()
            st.subheader("🔄 营运能力")
            col1, col2, col3 = st.columns(3)
            col1.metric("存货周转率", f"{inventory_turnover:.2f}次")
            col2.metric("应收账款周转率", f"{receivables_turnover:.2f}次")
            col3.metric("总资产周转率", f"{asset_turnover:.2f}次")

def show_dupont():
    st.title("🏛️ 杜邦分析")
    st.subheader("关键经营指标")
    
    conn = get_connection()
    revenue_query = "SELECT SUM(amount) as total, COUNT(*) as count FROM invoice"
    revenue_data = pd.read_sql_query(revenue_query, conn)
    total_revenue = revenue_data['total'].iloc[0] or 0
    invoice_count = revenue_data['count'].iloc[0] or 0
    
    cost_query = """SELECT SUM(ve.amount) as total FROM voucher_entry ve JOIN voucher v ON ve.voucher_id = v.id
                    WHERE ve.entry_type = '借方' AND ve.subject_code LIKE '64%'"""
    try:
        cost_data = pd.read_sql_query(cost_query, conn)
        total_cost = cost_data['total'].iloc[0] or 0
    except:
        total_cost = 0
    
    ar_query = "SELECT SUM(amount) FROM ar_ap WHERE type='AR' AND status='pending'"
    ap_query = "SELECT SUM(amount) FROM ar_ap WHERE type='AP' AND status='pending'"
    ar_total = pd.read_sql_query(ar_query, conn).iloc[0, 0] or 0
    ap_total = pd.read_sql_query(ap_query, conn).iloc[0, 0] or 0
    conn.close()
    
    gross_profit = total_revenue - total_cost
    gross_margin = (gross_profit / total_revenue * 100) if total_revenue > 0 else 0
    
    col1, col2, col3, col4, col5 = st.columns(5)
    col1.metric("经营收入", f"¥{total_revenue:,.2f}", f"{invoice_count} 张发票")
    col2.metric("经营成本", f"¥{total_cost:,.2f}", delta_color="inverse" if total_cost > 0 else "off")
    col3.metric("毛利润", f"¥{gross_profit:,.2f}", f"毛利率 {gross_margin:.1f}%")
    col4.metric("应收账款", f"¥{ar_total:,.2f}", delta_color="inverse" if ar_total > total_revenue * 0.3 else "normal")
    col5.metric("应付账款", f"¥{ap_total:,.2f}", delta_color="normal" if ap_total > 0 else "off")
    
    st.divider()
    st.subheader("🔍 杜邦分析")
    if total_revenue > 0:
        roe = (gross_profit / total_revenue) * (total_revenue / (ar_total + total_cost)) * 100 if (ar_total + total_cost) > 0 else 0
        col1, col2, col3 = st.columns(3)
        col1.info(f"**净利润率**\n\n{gross_margin:.2f}%\n\n每 1 元收入产生 {gross_margin/100:.2f}元利润")
        col2.info(f"**总资产周转率**\n\n{total_revenue / (ar_total + total_cost) if (ar_total + total_cost) > 0 else 0:.2f}\n\n资产利用效率")
        col3.success(f"**ROE (估算)**\n\n{roe:.2f}%\n\n股东权益回报率")
    else:
        st.warning("暂无足够数据进行杜邦分析")

def show_industry():
    st.title("🏭 行业对标")
    st.subheader("选择行业")
    industries = ["制造业", "信息技术", "批发零售", "餐饮服务", "建筑业", "交通运输", "房地产业", "金融业"]
    selected_industry = st.selectbox("选择所属行业", industries)
    
    st.subheader("企业财务数据")
    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown("**盈利能力**")
        company_gross_margin = st.number_input("毛利率 (%)", min_value=0.0, value=30.0, step=0.1, key="ind_gm")
        company_net_margin = st.number_input("净利润率 (%)", min_value=0.0, value=10.0, step=0.1, key="ind_nm")
        company_roe = st.number_input("净资产收益率 (%)", min_value=0.0, value=15.0, step=0.1, key="ind_roe")
    with col2:
        st.markdown("**偿债能力**")
        company_current_ratio = st.number_input("流动比率", min_value=0.0, value=2.0, step=0.1, key="ind_cr")
        company_quick_ratio = st.number_input("速动比率", min_value=0.0, value=1.5, step=0.1, key="ind_qr")
        company_debt_ratio = st.number_input("资产负债率 (%)", min_value=0.0, value=50.0, step=0.1, key="ind_dr")
    with col3:
        st.markdown("**营运能力**")
        company_ar_turnover = st.number_input("应收账款周转率 (次)", min_value=0.0, value=6.0, step=0.1, key="ind_art")
        company_inv_turnover = st.number_input("存货周转率 (次)", min_value=0.0, value=8.0, step=0.1, key="ind_inv")
    
    if st.button("开始对比分析", type="primary", key="ind_compare"):
        industry_avg = {
            '制造业': {'毛利率': 25.0, '净利率': 8.0, 'ROE': 12.0, '流动比率': 1.8, '速动比率': 1.0, '资产负债率': 50.0, '应收周转': 6.0, '存货周转': 5.0},
            '信息技术': {'毛利率': 45.0, '净利率': 18.0, 'ROE': 20.0, '流动比率': 2.5, '速动比率': 2.0, '资产负债率': 35.0, '应收周转': 8.0, '存货周转': 10.0},
            '批发零售': {'毛利率': 20.0, '净利率': 5.0, 'ROE': 15.0, '流动比率': 1.5, '速动比率': 0.8, '资产负债率': 55.0, '应收周转': 10.0, '存货周转': 8.0},
        }.get(selected_industry, {'毛利率': 25.0, '净利率': 8.0, 'ROE': 12.0, '流动比率': 1.8, '速动比率': 1.0, '资产负债率': 50.0, '应收周转': 6.0, '存货周转': 5.0})
        
        st.subheader("📊 对比结果")
        metrics = ['毛利率', '净利率', 'ROE', '流动比率', '速动比率', '资产负债率']
        company_vals = [company_gross_margin, company_net_margin, company_roe, company_current_ratio, company_quick_ratio, company_debt_ratio]
        industry_vals = [industry_avg['毛利率'], industry_avg['净利率'], industry_avg['ROE'], industry_avg['流动比率'], industry_avg['速动比率'], industry_avg['资产负债率']]
        
        import plotly.graph_objects as go
        fig = go.Figure()
        fig.add_trace(go.Bar(name='行业平均', x=metrics, y=industry_vals, marker_color='lightblue'))
        fig.add_trace(go.Bar(name='本公司', x=metrics, y=company_vals, marker_color='steelblue'))
        fig.update_layout(barmode='group', height=500, xaxis_title="指标", yaxis_title="数值", showlegend=True)
        st.plotly_chart(fig, use_container_width=True)
        
        st.subheader("💡 评价与建议")
        if company_gross_margin > industry_avg['毛利率']:
            st.success(f"✅ 毛利率 ({company_gross_margin:.1f}%) 高于行业平均 ({industry_avg['毛利率']:.1f}%)，产品竞争力强")
        else:
            st.warning(f"⚠️ 毛利率 ({company_gross_margin:.1f}%) 低于行业平均 ({industry_avg['毛利率']:.1f}%)，需提升产品附加值")
        if company_current_ratio > industry_avg['流动比率']:
            st.success(f"✅ 流动比率 ({company_current_ratio:.1f}) 高于行业平均 ({industry_avg['流动比率']:.1f})，短期偿债能力强")
        else:
            st.warning(f"⚠️ 流动比率 ({company_current_ratio:.1f}) 低于行业平均 ({industry_avg['流动比率']:.1f})，注意资金风险")

def show_cashflow():
    st.title("💵 资金诊断")
    tab1, tab2 = st.tabs(["数据录入", "资金分析"])
    with tab1:
        st.subheader("录入资金数据")
        col1, col2 = st.columns(2)
        with col1:
            period = st.text_input("期间", placeholder="2024-01", key="cf_period")
            opening_cash = st.number_input("期初货币资金", value=0.0, key="cf_opening")
            closing_cash = st.number_input("期末货币资金", value=0.0, key="cf_closing")
            avg_receivables = st.number_input("平均应收账款", value=0.0, key="cf_ar")
            avg_inventory = st.number_input("平均存货", value=0.0, key="cf_inv")
        with col2:
            revenue = st.number_input("营业收入", value=0.0, key="cf_rev")
            cogs = st.number_input("营业成本", value=0.0, key="cf_cogs")
            operating_expense = st.number_input("期间费用", value=0.0, key="cf_exp")
            operating_cash_flow = st.number_input("经营活动现金流净额", value=0.0, key="cf_ocf")
        if st.button("保存数据", type="primary", key="cf_save"):
            if period:
                conn = get_connection()
                metrics = [('期初货币资金', opening_cash), ('期末货币资金', closing_cash), ('平均应收账款', avg_receivables), ('平均存货', avg_inventory), ('营业收入', revenue), ('营业成本', cogs), ('期间费用', operating_expense), ('经营现金流', operating_cash_flow)]
                for m_name, m_val in metrics:
                    conn.execute("INSERT OR REPLACE INTO financial_metrics (period, metric_name, value, unit) VALUES (?, ?, ?, ?)", (period, m_name, m_val, '元'))
                conn.commit()
                conn.close()
                st.success("数据保存成功")
    with tab2:
        st.subheader("资金使用效率分析")
        conn = get_connection()
        df_all = pd.read_sql_query("SELECT * FROM financial_metrics ORDER BY period DESC", conn)
        conn.close()
        if df_all.empty:
            st.info("暂无数据，请先录入")
        else:
            latest_period = df_all['period'].max()
            df = df_all[df_all['period'] == latest_period]
            m = dict(zip(df['metric_name'], df['value']))
            opening = m.get('期初货币资金', 0); closing = m.get('期末货币资金', 0)
            avg_ar = m.get('平均应收账款', 0); avg_inv = m.get('平均存货', 0)
            revenue = m.get('营业收入', 0); cogs = m.get('营业成本', 0)
            ocf = m.get('经营现金流', 0)
            
            avg_cash = (opening + closing) / 2
            ar_turnover = revenue / avg_ar if avg_ar > 0 else 0
            ar_days = 365 / ar_turnover if ar_turnover > 0 else 0
            inv_turnover = cogs / avg_inv if avg_inv > 0 else 0
            inv_days = 365 / inv_turnover if inv_turnover > 0 else 0
            cash_to_asset = closing / (closing + avg_ar + avg_inv) * 100 if (closing + avg_ar + avg_inv) > 0 else 0
            
            st.subheader("📊 核心指标")
            col1, col2, col3, col4 = st.columns(4)
            col1.metric("货币资金", f"¥{closing:,.0f}", f"平均：¥{avg_cash:,.0f}")
            col2.metric("应收账款周转天数", f"{ar_days:.0f} 天", f"周转率：{ar_turnover:.1f}次")
            col3.metric("存货周转天数", f"{inv_days:.0f} 天", f"周转率：{inv_turnover:.1f}次")
            col4.metric("资金占比", f"{cash_to_asset:.1f}%", "货币资金/总资产")
            
            st.divider()
            st.subheader("💡 资金诊断建议")
            if ar_days > 90:
                st.warning(f"⚠️ 应收账款周转天数 ({ar_days:.0f}天) 较长，建议加强催收管理")
            else:
                st.success(f"✅ 应收账款周转天数 ({ar_days:.0f}天) 合理")
            if inv_days > 60:
                st.warning(f"⚠️ 存货周转天数 ({inv_days:.0f}天) 较长，建议优化库存管理")
            else:
                st.success(f"✅ 存货周转天数 ({inv_days:.0f}天) 合理")
            if ocf < 0:
                st.error(f"❌ 经营活动现金流为负 (¥{ocf:,.0f})，需关注资金链安全")
            else:
                st.success(f"✅ 经营活动现金流健康 (¥{ocf:,.0f})")

def show_budget():
    st.title("📈 预算分析")
    tab1, tab2 = st.tabs(["预算录入", "执行分析"])
    with tab1:
        st.subheader("录入预算数据")
        col1, col2 = st.columns(2)
        with col1:
            period = st.text_input("期间", placeholder="2024-01", key="bud_period")
            budget_revenue = st.number_input("预算收入", value=0.0, key="bud_rev")
            budget_cost = st.number_input("预算成本", value=0.0, key="bud_cost")
            budget_expense = st.number_input("预算费用", value=0.0, key="bud_exp")
        with col2:
            actual_revenue = st.number_input("实际收入", value=0.0, key="act_rev")
            actual_cost = st.number_input("实际成本", value=0.0, key="act_cost")
            actual_expense = st.number_input("实际费用", value=0.0, key="act_exp")
        if st.button("保存预算数据", type="primary", key="bud_save"):
            if period:
                conn = get_connection()
                metrics = [('预算收入', budget_revenue), ('预算成本', budget_cost), ('预算费用', budget_expense), ('实际收入', actual_revenue), ('实际成本', actual_cost), ('实际费用', actual_expense)]
                for m_name, m_val in metrics:
                    conn.execute("INSERT OR REPLACE INTO financial_metrics (period, metric_name, value, unit) VALUES (?, ?, ?, ?)", (period, m_name, m_val, '元'))
                conn.commit()
                conn.close()
                st.success("预算数据保存成功")
    with tab2:
        st.subheader("预算执行分析")
        conn = get_connection()
        df_all = pd.read_sql_query("SELECT * FROM financial_metrics ORDER BY period DESC", conn)
        conn.close()
        if df_all.empty:
            st.info("暂无数据")
        else:
            latest_period = df_all['period'].max()
            df = df_all[df_all['period'] == latest_period]
            m = dict(zip(df['metric_name'], df['value']))
            bud_rev = m.get('预算收入', 0); act_rev = m.get('实际收入', 0)
            bud_cost = m.get('预算成本', 0); act_cost = m.get('实际成本', 0)
            bud_exp = m.get('预算费用', 0); act_exp = m.get('实际费用', 0)
            
            rev_var = ((act_rev - bud_rev) / bud_rev * 100) if bud_rev > 0 else 0
            cost_var = ((act_cost - bud_cost) / bud_cost * 100) if bud_cost > 0 else 0
            exp_var = ((act_exp - bud_exp) / bud_exp * 100) if bud_exp > 0 else 0
            
            st.subheader("📊 预算执行对比")
            col1, col2, col3 = st.columns(3)
            col1.metric("收入", f"¥{act_rev:,.0f}", f"预算：¥{bud_rev:,.0f} ({rev_var:+.1f}%)")
            col2.metric("成本", f"¥{act_cost:,.0f}", f"预算：¥{bud_cost:,.0f} ({cost_var:+.1f}%)", delta_color="inverse")
            col3.metric("费用", f"¥{act_exp:,.0f}", f"预算：¥{bud_exp:,.0f} ({exp_var:+.1f}%)", delta_color="inverse")
            
            st.divider()
            st.subheader("💡 预算执行评价")
            if rev_var >= 0:
                st.success(f"✅ 收入超额完成 {rev_var:.1f}%")
            else:
                st.error(f"❌ 收入未达标，差 {abs(rev_var):.1f}%")
            if cost_var <= 0:
                st.success(f"✅ 成本控制在预算内 ({cost_var:+.1f}%)")
            else:
                st.warning(f"⚠️ 成本超支 {cost_var:.1f}%")
            if exp_var <= 0:
                st.success(f"✅ 费用控制在预算内 ({exp_var:+.1f}%)")
            else:
                st.warning(f"⚠️ 费用超支 {exp_var:.1f}%")

def show_pivot():
    st.title("🎯 智能透视分析")
    st.info("智能透视分析功能开发中...")

def show_doc_parse():
    st.title("📄 文档解析")
    st.info("文档解析功能开发中...")

def show_batch_parse():
    st.title("📄 批量解析")
    st.info("批量解析功能开发中...")

def show_governance():
    st.title("🧹 数据治理")
    st.info("数据治理功能开发中...")

def show_compliance():
    st.title("🛡️ 合规风控")
    st.info("合规风控功能开发中...")

def show_finance_calc():
    st.title("🧮 金融测算")
    calc_type = st.selectbox("计算类型", ["直线折旧", "双倍余额递减法", "IRR 计算", "NPV 计算", "年金计算"])
    
    if calc_type == "直线折旧":
        st.markdown("### 直线折旧计算")
        col1, col2, col3 = st.columns(3)
        with col1:
            cost = st.number_input("原值", min_value=0.0, value=10000.0, key="fd_cost")
        with col2:
            salvage = st.number_input("残值", min_value=0.0, value=1000.0, key="fd_salvage")
        with col3:
            life = st.number_input("使用年限", min_value=1, step=1, value=5, key="fd_life")
        if st.button("计算", key="calc_fd"):
            annual = (cost - salvage) / life
            total = cost - salvage
            st.metric("年折旧额", f"¥{annual:,.2f}")
            st.metric("总折旧额", f"¥{total:,.2f}")
            schedule = []
            book_value = cost
            for year in range(1, life + 1):
                schedule.append({'年份': year, '年折旧额': annual, '年末账面价值': book_value - annual})
                book_value -= annual
            df = pd.DataFrame(schedule)
            df['年折旧额'] = df['年折旧额'].apply(lambda x: f"¥{x:,.2f}")
            df['年末账面价值'] = df['年末账面价值'].apply(lambda x: f"¥{x:,.2f}")
            st.dataframe(df, use_container_width=True)
    
    elif calc_type == "双倍余额递减法":
        st.markdown("### 双倍余额递减法")
        col1, col2, col3 = st.columns(3)
        with col1:
            cost = st.number_input("原值", min_value=0.0, value=10000.0, key="ddb_cost")
        with col2:
            salvage = st.number_input("残值", min_value=0.0, value=1000.0, key="ddb_salvage")
        with col3:
            life = st.number_input("使用年限", min_value=1, step=1, value=5, key="ddb_life")
        if st.button("计算", key="calc_ddb"):
            rate = 2 / life
            book_value = cost
            schedule = []
            for year in range(1, life + 1):
                depreciation = book_value * rate
                if year == life:
                    depreciation = book_value - salvage
                book_value -= depreciation
                schedule.append({'年份': year, '年折旧额': depreciation, '年末账面价值': book_value})
            st.info(f"折旧率：{rate*100:.1f}%")
            df = pd.DataFrame(schedule)
            df['年折旧额'] = df['年折旧额'].apply(lambda x: f"¥{x:,.2f}")
            df['年末账面价值'] = df['年末账面价值'].apply(lambda x: f"¥{x:,.2f}")
            st.dataframe(df, use_container_width=True)
    
    elif calc_type == "IRR 计算":
        st.markdown("### 内部收益率 (IRR)")
        st.info("输入现金流列表，第一个为初始投资（负值）")
        cash_flows_str = st.text_input("现金流（用逗号分隔）", value="-10000, 3000, 4000, 5000, 6000", key="irr_cf")
        if st.button("计算", key="calc_irr"):
            try:
                cash_flows = [float(x.strip()) for x in cash_flows_str.split(',')]
                import numpy as np
                irr = np.irr(cash_flows)
                st.metric("IRR", f"{irr*100:.2f}%")
                df = pd.DataFrame({'期数': range(len(cash_flows)), '现金流': [f"¥{x:,.2f}" for x in cash_flows]})
                st.dataframe(df, use_container_width=True)
            except Exception as e:
                st.error(f"计算失败：{e}")
    
    elif calc_type == "NPV 计算":
        st.markdown("### 净现值 (NPV)")
        col1, col2 = st.columns(2)
        with col1:
            rate = st.number_input("折现率 (%)", min_value=0.0, value=10.0, key="npv_rate")
        with col2:
            cash_flows_str = st.text_input("现金流（用逗号分隔）", value="-10000, 3000, 4000, 5000, 6000", key="npv_cf")
        if st.button("计算", key="calc_npv"):
            try:
                cash_flows = [float(x.strip()) for x in cash_flows_str.split(',')]
                import numpy as np
                npv = np.npv(rate/100, cash_flows)
                st.metric("NPV", f"¥{npv:,.2f}")
            except Exception as e:
                st.error(f"计算失败：{e}")
    
    elif calc_type == "年金计算":
        st.markdown("### 年金计算 (PMT)")
        col1, col2, col3 = st.columns(3)
        with col1:
            rate = st.number_input("年利率 (%)", min_value=0.0, value=5.0, key="pmt_rate")
        with col2:
            nper = st.number_input("期数", min_value=1, step=1, value=10, key="pmt_nper")
        with col3:
            pv = st.number_input("现值", min_value=0.0, value=100000.0, key="pmt_pv")
        if st.button("计算", key="calc_pmt"):
            try:
                import numpy as np
                pmt = np.pmt(rate/100, nper, pv)
                st.metric("每期支付额", f"¥{abs(pmt):,.2f}")
            except Exception as e:
                st.error(f"计算失败：{e}")

def show_cvp():
    st.title("📊 本量利分析")
    st.sidebar.header("输入参数")
    fixed_cost = st.sidebar.number_input("固定成本 (元)", value=100000.0, step=1000.0, key="cvp_fc")
    unit_price = st.sidebar.number_input("单价 (元)", value=100.0, step=1.0, key="cvp_price")
    unit_variable_cost = st.sidebar.number_input("单位变动成本 (元)", value=60.0, step=1.0, key="cvp_vc")
    sales_volume = st.sidebar.number_input("预计销量 (件)", value=5000, step=100, key="cvp_vol")
    
    contribution_margin = unit_price - unit_variable_cost
    contribution_margin_ratio = contribution_margin / unit_price if unit_price > 0 else 0
    break_even_volume = fixed_cost / contribution_margin if contribution_margin > 0 else 0
    break_even_revenue = break_even_volume * unit_price
    
    st.subheader("📊 核心指标")
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("单位边际贡献", f"¥{contribution_margin:,.2f}")
    col2.metric("边际贡献率", f"{contribution_margin_ratio * 100:.1f}%")
    col3.metric("盈亏平衡点 (销量)", f"{break_even_volume:.0f} 件")
    col4.metric("盈亏平衡点 (金额)", f"¥{break_even_revenue:,.2f}")
    
    st.divider()
    tab1, tab2 = st.tabs(["盈亏平衡图", "敏感性分析"])
    with tab1:
        volumes = list(range(0, int(sales_volume * 1.5), max(100, int(sales_volume // 10))))
        revenue = [v * unit_price for v in volumes]
        total_cost = [fixed_cost + v * unit_variable_cost for v in volumes]
        import plotly.graph_objects as go
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=volumes, y=revenue, name='销售收入', line=dict(width=3)))
        fig.add_trace(go.Scatter(x=volumes, y=total_cost, name='总成本', line=dict(width=3)))
        fig.add_trace(go.Scatter(x=volumes, y=[fixed_cost] * len(volumes), name='固定成本', line=dict(dash='dash')))
        fig.add_vline(x=break_even_volume, line_dash="dash", annotation_text="盈亏平衡点")
        fig.update_layout(xaxis_title="销量 (件)", yaxis_title="金额 (元)", height=500, hovermode='x unified')
        st.plotly_chart(fig, use_container_width=True)
    with tab2:
        factor = st.slider("变动幅度", -50, 50, 20, key="cvp_factor")
        base_profit = sales_volume * contribution_margin - fixed_cost
        scenarios = []
        scenarios.append({'因素': '基准方案', '利润': base_profit, '变动率': '0.0%'})
        new_price = unit_price * (1 + factor / 100)
        new_profit = sales_volume * (new_price - unit_variable_cost) - fixed_cost
        change = (new_profit - base_profit) / base_profit * 100 if base_profit != 0 else 0
        scenarios.append({'因素': f'价格 {factor:+d}%', '利润': new_profit, '变动率': f'{change:+.1f}%'})
        new_vc = unit_variable_cost * (1 + factor / 100)
        new_profit = sales_volume * (unit_price - new_vc) - fixed_cost
        change = (new_profit - base_profit) / base_profit * 100 if base_profit != 0 else 0
        scenarios.append({'因素': f'变动成本 {factor:+d}%', '利润': new_profit, '变动率': f'{change:+.1f}%'})
        new_fc = fixed_cost * (1 + factor / 100)
        new_profit = sales_volume * contribution_margin - new_fc
        change = (new_profit - base_profit) / base_profit * 100 if base_profit != 0 else 0
        scenarios.append({'因素': f'固定成本 {factor:+d}%', '利润': new_profit, '变动率': f'{change:+.1f}%'})
        new_volume = sales_volume * (1 + factor / 100)
        new_profit = new_volume * contribution_margin - fixed_cost
        change = (new_profit - base_profit) / base_profit * 100 if base_profit != 0 else 0
        scenarios.append({'因素': f'销量 {factor:+d}%', '利润': new_profit, '变动率': f'{change:+.1f}%'})
        df_scenarios = pd.DataFrame(scenarios)
        df_scenarios['利润'] = df_scenarios['利润'].apply(lambda x: f"¥{x:,.0f}")
        st.dataframe(df_scenarios, use_container_width=True, hide_index=True)
    
    st.divider()
    current_profit = sales_volume * contribution_margin - fixed_cost
    margin_of_safety = (sales_volume - break_even_volume) / sales_volume * 100 if sales_volume > 0 else 0
    st.subheader("💡 经营安全分析")
    col1, col2 = st.columns(2)
    col1.info(f"**当前利润**: ¥{current_profit:,.2f}\n\n**安全边际率**: {margin_of_safety:.1f}%\n\n{'✅ 经营很安全' if margin_of_safety > 30 else '⚠️ 需要注意风险' if margin_of_safety > 10 else '❌ 经营风险较高'}")
    col2.success(f"**经营杠杆系数**: {sales_volume * contribution_margin / current_profit if current_profit > 0 else 0:.2f}\n\n销量每增长 1%,利润将增长 {sales_volume * contribution_margin / current_profit if current_profit > 0 else 0:.1f}%")

def show_beautify():
    st.title("📑 报表美化")
    st.info("报表美化功能开发中...")

def show_tools():
    st.title("🧰 快捷工具箱")
    tool = st.selectbox("选择工具", ["🧮 快速计算器", "📊 批量对比", "⏱️ 计时器", "📝 快速备忘录"])
    if tool == "🧮 快速计算器":
        calc_type = st.selectbox("计算类型", ["加减乘除", "百分比计算", "税额计算", "小写转大写金额"])
        if calc_type == "加减乘除":
            col1, col2, col3 = st.columns(3)
            with col1:
                num1 = st.number_input("数字 1", value=0.0, key="calc_num1")
                op = st.selectbox("运算符", ["+", "-", "×", "÷"], key="calc_op")
            with col2:
                num2 = st.number_input("数字 2", value=0.0, key="calc_num2")
            with col3:
                if st.button("=", type="primary", key="calc_eq"):
                    if op == "+": result = num1 + num2
                    elif op == "-": result = num1 - num2
                    elif op == "×": result = num1 * num2
                    elif op == "÷": result = num1 / num2 if num2 != 0 else "错误：除数为 0"
                    st.metric("结果", result)
        elif calc_type == "百分比计算":
            col1, col2 = st.columns(2)
            with col1:
                base = st.number_input("基数", value=100.0, key="pct_base")
                percent = st.number_input("百分比 (%)", value=10.0, key="pct_val")
            with col2:
                if st.button("计算百分比", key="pct_btn"):
                    result = base * (percent / 100)
                    st.metric("结果", result)
        elif calc_type == "税额计算":
            col1, col2 = st.columns(2)
            with col1:
                amount = st.number_input("金额", value=1000.0, key="tax_amt")
                tax_rate = st.selectbox("税率", [0.03, 0.06, 0.09, 0.13, 0.17], key="tax_rate")
            with col2:
                if st.button("计算税额", key="tax_btn"):
                    tax = amount * tax_rate
                    total = amount + tax
                    st.metric("税额", f"¥{tax:,.2f}")
                    st.metric("含税总额", f"¥{total:,.2f}")
        elif calc_type == "小写转大写金额":
            amount = st.number_input("小写金额", value=12345.67, key="cap_amt")
            def num_to_cn_upper(num):
                cn_upper_map = {'0': '零', '1': '壹', '2': '贰', '3': '叁', '4': '肆', '5': '伍', '6': '陆', '7': '柒', '8': '捌', '9': '玖'}
                unit = '分角元拾佰仟万拾佰仟亿拾佰仟'
                num_str = f"{num:.2f}"
                result = ""
                unit_index = 0
                for digit in num_str.replace('.', '').replace('-', ''):
                    if digit in cn_upper_map:
                        result += cn_upper_map[digit] + unit[unit_index]
                        unit_index += 1
                return result + "整"
            if st.button("转换", key="cap_btn"):
                cn_amount = num_to_cn_upper(amount)
                st.text_area("大写金额", value=cn_amount, height=100)
    elif tool == "📊 批量对比":
        data_input = st.text_area("输入数据（每行一组，逗号分隔）", placeholder="例如：\n2024 年，1000,200,50\n2025 年，1200,250,60\n2026 年，1500,300,75")
        if data_input:
            lines = data_input.strip().split('\n')
            data = [line.split(',') for line in lines]
            df = pd.DataFrame(data)
            st.dataframe(df, use_container_width=True)
            csv = df.to_csv(index=False, encoding='utf-8-sig')
            st.download_button(label="📥 导出为 CSV", data=csv, file_name="批量对比数据.csv", mime='text/csv')
    elif tool == "⏱️ 计时器":
        col1, col2, col3 = st.columns(3)
        with col1:
            hours = st.number_input("小时", min_value=0, max_value=23, value=0, key="timer_h")
        with col2:
            minutes = st.number_input("分钟", min_value=0, max_value=59, value=5, key="timer_m")
        with col3:
            seconds = st.number_input("秒", min_value=0, max_value=59, value=0, key="timer_s")
        total_seconds = hours * 3600 + minutes * 60 + seconds
        if st.button("▶️ 开始倒计时", key="timer_start"):
            if total_seconds > 0:
                progress_bar = st.progress(0)
                timer_text = st.empty()
                remaining = total_seconds
                while remaining > 0:
                    mins, secs = divmod(remaining, 60)
                    hrs, mins = divmod(mins, 60)
                    timer_text.text(f"剩余时间：{hrs:02d}:{mins:02d}:{secs:02d}")
                    progress_bar.progress(1 - remaining / total_seconds)
                    import time
                    time.sleep(1)
                    remaining -= 1
                timer_text.text("⏰ 时间到！")
                st.balloons()
    elif tool == "📝 快速备忘录":
        notes = st.text_area("输入备忘内容", height=300, placeholder="在此记录重要事项...")
        if notes:
            st.download_button(label="💾 保存为文本文件", data=notes, file_name=f"备忘录_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt", mime='text/plain')

def show_template():
    st.title("📋 模板中心")
    st.info("模板中心功能开发中...")

def show_enhanced():
    st.title("🚀 增强功能")
    tab1, tab2, tab3 = st.tabs(["数据导出", "数据导入", "备份恢复"])
    tables = {'invoice': '发票数据', 'bank_statement': '银行流水', 'company_statement': '企业账务', 'voucher': '凭证主表', 'voucher_entry': '凭证分录', 'ar_ap': '应收应付', 'calendar_event': '日历事件', 'financial_metrics': '财务指标'}
    with tab1:
        st.subheader("导出数据到 Excel")
        selected_table = st.selectbox("选择要导出的表", list(tables.keys()), format_func=lambda x: tables[x], key="exp_table")
        if st.button("导出 Excel", type="primary", key="exp_btn"):
            try:
                conn = get_connection()
                df = pd.read_sql_query(f"SELECT * FROM {selected_table}", conn)
                conn.close()
                if not df.empty:
                    output = BytesIO()
                    with pd.ExcelWriter(output, engine='openpyxl') as writer:
                        df.to_excel(writer, index=False, sheet_name=selected_table)
                    st.download_button(label=f"📥 下载 {tables[selected_table]}.xlsx", data=output.getvalue(), file_name=f"{selected_table}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx", mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
                    st.success(f"导出成功，共 {len(df)} 条记录")
                else:
                    st.warning("该表暂无数据")
            except Exception as e:
                st.error(f"导出失败：{e}")
    with tab2:
        st.subheader("从 Excel 导入数据")
        uploaded_file = st.file_uploader("上传 Excel 文件", type=['xlsx', 'xls'], key="imp_file")
        target_table = st.selectbox("导入到表", list(tables.keys()), format_func=lambda x: tables[x], key="imp_table")
        if uploaded_file and st.button("开始导入", key="imp_btn"):
            try:
                df = pd.read_excel(uploaded_file)
                st.write(f"预览数据（前 5 行）:")
                st.dataframe(df.head())
                conn = get_connection()
                count = 0
                for _, row in df.iterrows():
                    try:
                        row_dict = row.dropna().to_dict()
                        if not row_dict: continue
                        columns = ', '.join(row_dict.keys())
                        placeholders = ', '.join(['?' for _ in row_dict])
                        values = list(row_dict.values())
                        conn.execute(f"INSERT OR REPLACE INTO {target_table} ({columns}) VALUES ({placeholders})", values)
                        count += 1
                    except: pass
                conn.commit()
                conn.close()
                st.success(f"导入完成，共 {count} 条记录")
            except Exception as e:
                st.error(f"导入失败：{e}")
    with tab3:
        st.subheader("数据备份与恢复")
        st.warning("⚠️ 备份操作会导出所有数据，恢复操作会清空现有数据并导入备份文件")
        col1, col2 = st.columns(2)
        with col1:
            st.markdown("### 📤 备份全部数据")
            if st.button("备份所有数据", type="primary", key="backup_btn"):
                try:
                    conn = get_connection()
                    backup_data = {}
                    for table_name in tables.keys():
                        df = pd.read_sql_query(f"SELECT * FROM {table_name}", conn)
                        backup_data[table_name] = df.to_dict('records')
                    conn.close()
                    backup_json = json.dumps(backup_data, ensure_ascii=False, default=str)
                    st.download_button(label="📥 下载备份文件", data=backup_json, file_name=f"backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json", mime="application/json")
                    st.success("备份数据已生成")
                except Exception as e:
                    st.error(f"备份失败：{e}")
        with col2:
            st.markdown("### 📥 恢复数据")
            backup_file = st.file_uploader("上传备份文件", type=['json'], key="restore_file")
            if backup_file and st.button("恢复数据", type="primary", key="restore_btn"):
                try:
                    backup_data = json.load(backup_file)
                    conn = get_connection()
                    cursor = conn.cursor()
                    total_imported = 0
                    for table_name, records in backup_data.items():
                        for record in records:
                            try:
                                columns = ', '.join(record.keys())
                                placeholders = ', '.join(['?' for _ in record])
                                cursor.execute(f"INSERT OR REPLACE INTO {table_name} ({columns}) VALUES ({placeholders})", list(record.values()))
                                total_imported += 1
                            except: pass
                    conn.commit()
                    conn.close()
                    st.success(f"恢复完成，共导入 {total_imported} 条记录")
                    st.rerun()
                except Exception as e:
                    st.error(f"恢复失败：{e}")

def show_help():
    st.title("❓ 帮助中心")
    st.info("帮助中心功能开发中...")

def show_calendar():
    st.title("📅 财务日历")
    tab1, tab2, tab3 = st.tabs(["添加事件", "日历视图", "即将到期"])
    
    with tab1:
        st.subheader("添加新事件")
        col1, col2 = st.columns(2)
        with col1:
            title = st.text_input("事件标题", key="event_title")
            event_date = st.date_input("事件日期", value=datetime.now(), key="cal_event_date")
            event_type = st.selectbox("事件类型", ["纳税申报", "财务报表", "审计", "付款", "收款", "会议", "年检", "其他"], key="cal_event_type")
        with col2:
            description = st.text_area("描述", key="cal_event_desc")
            is_recurring = st.checkbox("每年重复", value=False, key="cal_recurring")
        if st.button("保存事件", type="primary", key="save_event"):
            if title:
                conn = get_connection()
                conn.execute("INSERT INTO calendar_event (title, event_date, event_type, description, is_recurring) VALUES (?, ?, ?, ?, ?)",
                    (title, event_date.strftime('%Y-%m-%d'), event_type, description, is_recurring))
                conn.commit()
                conn.close()
                st.success("事件保存成功")
                st.rerun()
    
    with tab2:
        st.subheader("日历视图")
        col1, col2 = st.columns(2)
        with col1:
            filter_month = st.selectbox("筛选月份", [(datetime.now() + timedelta(days=30*i)).strftime('%Y-%m') for i in range(-3, 6)], key="cal_filter_month")
        with col2:
            filter_type = st.multiselect("筛选类型", ["纳税申报", "财务报表", "审计", "付款", "收款", "会议", "年检", "其他"], default=[], key="cal_filter_type")
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
            st.dataframe(df[['日期', '标题', '类型', '重复', 'description']], use_container_width=True,
                column_config={'日期': '日期', '标题': '标题', '类型': '类型', '重复': '重复', 'description': '描述'})
        else:
            st.info("该月份暂无事件")
    
    with tab3:
        st.subheader("即将到期提醒")
        days_limit = st.slider("查看未来多少天的事件", 7, 90, 30, key="cal_lookahead")
        today = datetime.now()
        end_date = today + timedelta(days=days_limit)
        conn = get_connection()
        df = pd.read_sql_query("SELECT * FROM calendar_event WHERE event_date BETWEEN ? AND ? ORDER BY event_date",
            conn, params=[today.strftime('%Y-%m-%d'), end_date.strftime('%Y-%m-%d')])
        conn.close()
        if not df.empty:
            for _, row in df.iterrows():
                event_date = datetime.strptime(row['event_date'], '%Y-%m-%d')
                days_remaining = (event_date - today).days
                if days_remaining == 0: status = "🔴 今天"
                elif days_remaining <= 3: status = "🟠 即将到期"
                elif days_remaining <= 7: status = "🟡 本周内"
                else: status = "🟢"
                with st.container():
                    col1, col2, col3 = st.columns([1, 3, 1])
                    col1.write(f"**{event_date.strftime('%m-%d')}**")
                    col2.write(f"{row['title']} ({row['event_type']})")
                    col3.write(status)
                    st.divider()
        else:
            st.success(f"未来{days_limit}天内没有待办事件")

# ==================== 主函数 ====================
def main():
    init_db()
    
    if not st.session_state.authenticated:
        login()
        return
    
    logout()
    
    # 侧边栏导航
    with st.sidebar:
        st.title("📊 财务工作台")
        st.markdown(f"👤 {st.session_state.username}")
        st.divider()
        
        section = st.radio(
            "📁 功能模块",
            ["🏠 首页", "📝 日常核算", "📊 财务分析", "🏭 数据工厂", "💼 决策支持", "🧰 办公工具"],
            index=0
        )
        
        st.divider()
        st.info("**财务工作台 v2.0**\n\n2026-05-05")
    
    # 根据选择显示对应模块
    if section == "🏠 首页":
        show_home()
    
    elif section == "📝 日常核算":
        tabs = st.tabs(["📄 发票管理", "🏦 银行对账", "📝 凭证录入", "📋 科目余额表", "💰 应收应付", "📑 纳税申报"])
        with tabs[0]: show_invoice()
        with tabs[1]: show_bank()
        with tabs[2]: show_voucher()
        with tabs[3]: show_balance()
        with tabs[4]: show_arap()
        with tabs[5]: show_tax()
    
    elif section == "📊 财务分析":
        tabs = st.tabs(["📊 财务比率", "🏛️ 杜邦分析", "🏭 行业对标", "💵 资金诊断", "📈 预算分析", "🎯 智能透视"])
        with tabs[0]: show_ratios()
        with tabs[1]: show_dupont()
        with tabs[2]: show_industry()
        with tabs[3]: show_cashflow()
        with tabs[4]: show_budget()
        with tabs[5]: show_pivot()
    
    elif section == "🏭 数据工厂":
        tabs = st.tabs(["📄 文档解析", "📄 批量解析", "🧹 数据治理", "🛡️ 合规风控"])
        with tabs[0]: show_doc_parse()
        with tabs[1]: show_batch_parse()
        with tabs[2]: show_governance()
        with tabs[3]: show_compliance()
    
    elif section == "💼 决策支持":
        tabs = st.tabs(["🧮 金融测算", "📊 本量利", "📑 报表美化"])
        with tabs[0]: show_finance_calc()
        with tabs[1]: show_cvp()
        with tabs[2]: show_beautify()
    
    elif section == "🧰 办公工具":
        tabs = st.tabs(["📅 财务日历", "🧰 工具箱", "📋 模板中心", "🚀 增强功能", "❓ 帮助中心"])
        with tabs[0]: show_calendar()
        with tabs[1]: show_tools()
        with tabs[2]: show_template()
        with tabs[3]: show_enhanced()
        with tabs[4]: show_help()


if __name__ == "__main__":
    main()
