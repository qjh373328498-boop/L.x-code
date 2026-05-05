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
    st.info("行业对标功能开发中...")

def show_cashflow():
    st.title("💵 资金诊断")
    st.info("资金诊断功能开发中...")

def show_budget():
    st.title("📈 预算分析")
    st.info("预算分析功能开发中...")

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
    st.info("本量利分析功能开发中...")

def show_beautify():
    st.title("📑 报表美化")
    st.info("报表美化功能开发中...")

def show_tools():
    st.title("🧰 快捷工具箱")
    st.info("快捷工具箱功能开发中...")

def show_template():
    st.title("📋 模板中心")
    st.info("模板中心功能开发中...")

def show_enhanced():
    st.title("🚀 增强功能")
    st.info("增强功能开发中...")

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
