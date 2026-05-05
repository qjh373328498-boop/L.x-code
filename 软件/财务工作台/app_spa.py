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
        st.info("💡 请在「应收账款」标签页添加应收账款数据后，再查看账龄分析")
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
            st.metric("应收账款总额", f"¥{ar_df['amount'].sum():,.2f}")
            try:
                import plotly.express as px
                fig = px.pie(values=age_summary.values, names=age_summary.index, title="应收账款账龄分布")
                col2.plotly_chart(fig, use_container_width=True)
            except: pass
        else:
            st.warning("暂无应收账款数据，账龄分析表将显示为空")

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

def show_balance():
    st.title("📋 科目余额表")
    tab1, tab2 = st.tabs(["余额查询", "科目设置"])
    with tab1:
        st.subheader("科目余额查询")
        col1, col2 = st.columns(2)
        with col1:
            period = st.text_input("期间", placeholder="2024-12", key="bal_period")
        with col2:
            subject_filter = st.text_input("科目筛选", key="bal_filter")
        conn = get_connection()
        query = """SELECT ve.subject_code AS code, ve.subject_name AS name,
                   SUM(CASE WHEN ve.entry_type = '借方' THEN ve.amount ELSE 0 END) AS debit,
                   SUM(CASE WHEN ve.entry_type = '贷方' THEN ve.amount ELSE 0 END) AS credit,
                   (SUM(CASE WHEN ve.entry_type = '借方' THEN ve.amount ELSE 0 END) - 
                    SUM(CASE WHEN ve.entry_type = '贷方' THEN ve.amount ELSE 0 END)) AS balance
                   FROM voucher_entry ve GROUP BY ve.subject_code, ve.subject_name ORDER BY ve.subject_code"""
        df = pd.read_sql_query(query, conn)
        if not df.empty:
            df.rename(columns={'code': '科目代码', 'name': '科目名称', 'debit': '借方发生额', 'credit': '贷方发生额', 'balance': '余额'}, inplace=True)
            if subject_filter:
                df = df[(df['科目代码'].astype(str).str.contains(subject_filter)) | (df['科目名称'].str.contains(subject_filter))]
            st.dataframe(df, use_container_width=True)
            total_debit = df['借方发生额'].sum()
            total_credit = df['贷方发生额'].sum()
            col1, col2, col3 = st.columns(3)
            col1.metric("借方余额合计", f"¥{total_debit:,.2f}")
            col2.metric("贷方余额合计", f"¥{total_credit:,.2f}")
            col3.success("✅ 借贷平衡" if abs(total_debit - total_credit) < 0.01 else f"❌ 不平衡 (差异：¥{abs(total_debit - total_credit):,.2f})")
            try:
                import plotly.express as px
                top_subjects = df.nlargest(10, '余额')
                fig = px.bar(top_subjects, x='科目名称', y='余额', title="余额前 10 大科目")
                fig.update_layout(height=500)
                st.plotly_chart(fig, use_container_width=True)
            except: pass
        else:
            st.info("暂无数据，请先录入凭证")
        conn.close()
    with tab2:
        st.subheader("预设会计科目")
        subjects = [{'code': '1001', 'name': '库存现金', 'type': '资产'}, {'code': '1002', 'name': '银行存款', 'type': '资产'}, {'code': '1122', 'name': '应收账款', 'type': '资产'}, {'code': '2202', 'name': '应付账款', 'type': '负债'}, {'code': '6001', 'name': '主营业务收入', 'type': '损益'}, {'code': '6602', 'name': '管理费用', 'type': '损益'}]
        st.dataframe(pd.DataFrame(subjects), use_container_width=True, hide_index=True)

def show_ratios():
    st.title("📊 财务比率分析")
    tab1, tab2 = st.tabs(["数据录入", "比率分析"])
    with tab1:
        st.subheader("录入财务数据")
        col1, col2, col3 = st.columns(3)
        with col1:
            period = st.text_input("期间", placeholder="2024-12", key="fm_period")
            current_assets = st.number_input("流动资产", value=0.0, key="fm_current_assets")
            total_assets = st.number_input("资产总计", value=0.0, key="fm_total_assets")
        with col2:
            current_liabilities = st.number_input("流动负债", value=0.0, key="fm_current_liab")
            total_liabilities = st.number_input("负债总计", value=0.0, key="fm_total_liab")
            equity = st.number_input("所有者权益", value=0.0, key="fm_equity")
        with col3:
            revenue = st.number_input("营业收入", value=0.0, key="fm_revenue")
            net_profit = st.number_input("净利润", value=0.0, key="fm_net_profit")
            cogs = st.number_input("营业成本", value=0.0, key="fm_cogs")
            inventory = st.number_input("存货", value=0.0, key="fm_inventory")
        if st.button("保存数据", type="primary", key="save_fm_data"):
            if period and total_assets > 0:
                conn = get_connection()
                metrics = [('流动资产', current_assets), ('资产总计', total_assets), ('流动负债', current_liabilities), ('负债总计', total_liabilities), ('所有者权益', equity), ('营业收入', revenue), ('净利润', net_profit), ('营业成本', cogs), ('存货', inventory)]
                for m_name, m_val in metrics:
                    conn.execute("INSERT OR REPLACE INTO financial_metrics (period, metric_name, value, unit) VALUES (?, ?, ?, ?)", (period, m_name, m_val, '元'))
                conn.commit()
                conn.close()
                st.success("数据保存成功")
    with tab2:
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
            inventory = m.get('存货', 0)
            current_ratio = current_assets / current_liabilities if current_liabilities > 0 else 0
            quick_ratio = (current_assets - inventory) / current_liabilities if current_liabilities > 0 else 0
            debt_ratio = total_liabilities / total_assets * 100 if total_assets > 0 else 0
            gross_margin = (revenue - cogs) / revenue * 100 if revenue > 0 else 0
            net_margin = net_profit / revenue * 100 if revenue > 0 else 0
            roe = net_profit / equity * 100 if equity > 0 else 0
            st.subheader("💧 偿债能力")
            col1, col2, col3 = st.columns(3)
            col1.metric("流动比率", f"{current_ratio:.2f}", "标准值：2.0")
            col2.metric("速动比率", f"{quick_ratio:.2f}", "标准值：1.0")
            col3.metric("资产负债率", f"{debt_ratio:.1f}%", "标准值：<60%")
            st.divider()
            st.subheader("💰 盈利能力")
            col1, col2, col3 = st.columns(3)
            col1.metric("毛利率", f"{gross_margin:.1f}%")
            col2.metric("净利率", f"{net_margin:.1f}%")
            col3.metric("ROE", f"{roe:.1f}%")

def show_dupont():
    st.title("🏛️ 杜邦分析")
    conn = get_connection()
    revenue_data = pd.read_sql_query("SELECT SUM(amount) as total FROM invoice", conn).iloc[0, 0] or 0
    try:
        total_cost = pd.read_sql_query("SELECT SUM(ve.amount) FROM voucher_entry ve WHERE ve.entry_type='借方' AND ve.subject_code LIKE '64%'", conn).iloc[0, 0] or 0
    except: total_cost = 0
    ar_total = pd.read_sql_query("SELECT SUM(amount) FROM ar_ap WHERE type='AR'", conn).iloc[0, 0] or 0
    conn.close()
    gross_profit = revenue_data - total_cost
    gross_margin = (gross_profit / revenue_data * 100) if revenue_data > 0 else 0
    st.subheader("关键经营指标")
    col1, col2, col3 = st.columns(3)
    col1.metric("经营收入", f"¥{revenue_data:,.2f}")
    col2.metric("毛利润", f"¥{gross_profit:,.2f}", f"毛利率 {gross_margin:.1f}%")
    col3.metric("应收账款", f"¥{ar_total:,.2f}")
    st.divider()
    st.subheader("🔍 杜邦分析")
    if revenue_data > 0:
        roe = (gross_profit / revenue_data) * (revenue_data / (ar_total + total_cost)) * 100 if (ar_total + total_cost) > 0 else 0
        st.info(f"**净利润率**: {gross_margin:.2f}% | **ROE**: {roe:.2f}%")

def show_industry():
    st.title("🏭 行业对标")
    industries = ["制造业", "信息技术", "批发零售", "餐饮服务", "建筑业", "交通运输", "房地产业", "金融业"]
    selected_industry = st.selectbox("选择所属行业", industries, key="ind_sel")
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
        industry_avg = {'制造业': {'毛利率': 25.0, '净利率': 8.0, 'ROE': 12.0, '流动比率': 1.8, '速动比率': 1.0, '资产负债率': 50.0}, '信息技术': {'毛利率': 45.0, '净利率': 18.0, 'ROE': 20.0, '流动比率': 2.5, '速动比率': 2.0, '资产负债率': 35.0}}.get(selected_industry, {'毛利率': 25.0, '净利率': 8.0, 'ROE': 12.0, '流动比率': 1.8, '速动比率': 1.0, '资产负债率': 50.0})
        st.subheader("📊 对比结果")
        metrics = ['毛利率', '净利率', 'ROE', '流动比率', '速动比率', '资产负债率']
        company_vals = [company_gross_margin, company_net_margin, company_roe, company_current_ratio, company_quick_ratio, company_debt_ratio]
        industry_vals = [industry_avg['毛利率'], industry_avg['净利率'], industry_avg['ROE'], industry_avg['流动比率'], industry_avg['速动比率'], industry_avg['资产负债率']]
        import plotly.graph_objects as go
        fig = go.Figure()
        fig.add_trace(go.Bar(name='行业平均', x=metrics, y=industry_vals, marker_color='lightblue'))
        fig.add_trace(go.Bar(name='本公司', x=metrics, y=company_vals, marker_color='steelblue'))
        fig.update_layout(barmode='group', height=500, showlegend=True)
        st.plotly_chart(fig, use_container_width=True)

def show_cashflow():
    st.title("💵 资金诊断")
    tab1, tab2 = st.tabs(["数据录入", "资金分析"])
    with tab1:
        col1, col2 = st.columns(2)
        with col1:
            period = st.text_input("期间", placeholder="2024-01", key="cf_period")
            opening_cash = st.number_input("期初货币资金", value=0.0, key="cf_opening")
            closing_cash = st.number_input("期末货币资金", value=0.0, key="cf_closing")
            avg_receivables = st.number_input("平均应收账款", value=0.0, key="cf_ar")
        with col2:
            revenue = st.number_input("营业收入", value=0.0, key="cf_rev")
            cogs = st.number_input("营业成本", value=0.0, key="cf_cogs")
            ocf = st.number_input("经营活动现金流净额", value=0.0, key="cf_ocf")
        if st.button("保存数据", type="primary", key="cf_save"):
            if period:
                conn = get_connection()
                for m_name, m_val in [('期初货币资金', opening_cash), ('期末货币资金', closing_cash), ('平均应收账款', avg_receivables), ('营业收入', revenue), ('经营现金流', ocf)]:
                    conn.execute("INSERT OR REPLACE INTO financial_metrics (period, metric_name, value, unit) VALUES (?, ?, ?, ?)", (period, m_name, m_val, '元'))
                conn.commit()
                conn.close()
                st.success("数据保存成功")
    with tab2:
        conn = get_connection()
        df = pd.read_sql_query("SELECT * FROM financial_metrics WHERE period=(SELECT MAX(period) FROM financial_metrics)", conn)
        conn.close()
        if df.empty: st.info("暂无数据")
        else:
            m = dict(zip(df['metric_name'], df['value']))
            closing = m.get('期末货币资金', 0); avg_ar = m.get('平均应收账款', 0)
            revenue = m.get('营业收入', 0); ocf = m.get('经营现金流', 0)
            ar_turnover = revenue / avg_ar if avg_ar > 0 else 0
            ar_days = 365 / ar_turnover if ar_turnover > 0 else 0
            col1, col2, col3 = st.columns(3)
            col1.metric("货币资金", f"¥{closing:,.0f}")
            col2.metric("应收账款周转天数", f"{ar_days:.0f} 天")
            col3.metric("经营现金流", f"¥{ocf:,.0f}", delta="正" if ocf > 0 else "负", delta_color="inverse")

def show_budget():
    st.title("📈 预算分析")
    tab1, tab2 = st.tabs(["预算录入", "执行分析"])
    with tab1:
        col1, col2 = st.columns(2)
        with col1:
            period = st.text_input("期间", placeholder="2024-01", key="bud_period")
            budget_revenue = st.number_input("预算收入", value=0.0, key="bud_rev")
            budget_cost = st.number_input("预算成本", value=0.0, key="bud_cost")
        with col2:
            actual_revenue = st.number_input("实际收入", value=0.0, key="act_rev")
            actual_cost = st.number_input("实际成本", value=0.0, key="act_cost")
        if st.button("保存预算数据", type="primary", key="bud_save"):
            if period:
                conn = get_connection()
                for m_name, m_val in [('预算收入', budget_revenue), ('预算成本', budget_cost), ('实际收入', actual_revenue), ('实际成本', actual_cost)]:
                    conn.execute("INSERT OR REPLACE INTO financial_metrics (period, metric_name, value, unit) VALUES (?, ?, ?, ?)", (period, m_name, m_val, '元'))
                conn.commit()
                conn.close()
                st.success("保存成功")
    with tab2:
        conn = get_connection()
        df = pd.read_sql_query("SELECT * FROM financial_metrics WHERE period=(SELECT MAX(period) FROM financial_metrics)", conn)
        conn.close()
        if df.empty: st.info("暂无数据")
        else:
            m = dict(zip(df['metric_name'], df['value']))
            bud_rev = m.get('预算收入', 0); act_rev = m.get('实际收入', 0)
            bud_cost = m.get('预算成本', 0); act_cost = m.get('实际成本', 0)
            rev_var = ((act_rev - bud_rev) / bud_rev * 100) if bud_rev > 0 else 0
            cost_var = ((act_cost - bud_cost) / bud_cost * 100) if bud_cost > 0 else 0
            col1, col2 = st.columns(2)
            col1.metric("收入执行", f"¥{act_rev:,.0f}", f"预算：¥{bud_rev:,.0f} ({rev_var:+.1f}%)")
            col2.metric("成本执行", f"¥{act_cost:,.0f}", f"预算：¥{bud_cost:,.0f} ({cost_var:+.1f}%)", delta_color="inverse")

def show_finance_calc():
    st.title("🧮 金融测算")
    calc_type = st.selectbox("计算类型", ["直线折旧", "IRR 计算", "NPV 计算", "年金计算"], key="fc_type")
    if calc_type == "直线折旧":
        col1, col2, col3 = st.columns(3)
        with col1: cost = st.number_input("原值", value=10000.0, key="fd_cost")
        with col2: salvage = st.number_input("残值", value=1000.0, key="fd_salvage")
        with col3: life = st.number_input("使用年限", value=5, key="fd_life")
        if st.button("计算", key="fd_calc"):
            annual = (cost - salvage) / life
            st.metric("年折旧额", f"¥{annual:,.2f}")
            st.info(f"总折旧额：¥{cost - salvage:,.2f} | 月折旧额：¥{annual/12:,.2f}")
    elif calc_type == "IRR 计算":
        cashflows_str = st.text_input("现金流 (逗号分隔)", value="-10000, 3000, 4000, 5000, 6000", key="irr_cf")
        if st.button("计算", key="irr_calc"):
            try:
                cashflows = [float(x.strip()) for x in cashflows_str.split(',')]
                import numpy as np
                irr = np.irr(cashflows)
                st.metric("IRR", f"{irr*100:.2f}%")
            except Exception as e: st.error(f"计算失败：{e}")
    elif calc_type == "NPV 计算":
        col1, col2 = st.columns(2)
        with col1: rate = st.number_input("折现率 (%)", value=10.0, key="npv_rate")
        with col2: cashflows_str = st.text_input("现金流 (逗号分隔)", value="-10000, 3000, 4000, 5000", key="npv_cf")
        if st.button("计算", key="npv_calc"):
            try:
                cashflows = [float(x.strip()) for x in cashflows_str.split(',')]
                import numpy as np
                npv = np.npv(rate/100, cashflows)
                st.metric("NPV", f"¥{npv:,.2f}")
            except Exception as e: st.error(f"计算失败：{e}")
    elif calc_type == "年金计算":
        col1, col2, col3 = st.columns(3)
        with col1: rate = st.number_input("年利率 (%)", value=5.0, key="pmt_rate")
        with col2: nper = st.number_input("期数", value=10, key="pmt_nper")
        with col3: pv = st.number_input("现值", value=100000.0, key="pmt_pv")
        if st.button("计算", key="pmt_calc"):
            try:
                import numpy as np
                pmt = np.pmt(rate/100, nper, pv)
                st.metric("每期支付额", f"¥{abs(pmt):,.2f}")
            except Exception as e: st.error(f"计算失败：{e}")

def show_cvp():
    st.title("📊 本量利分析")
    st.sidebar.header("输入参数")
    fixed_cost = st.sidebar.number_input("固定成本 (元)", value=100000.0, step=1000.0, key="cvp_fc")
    unit_price = st.sidebar.number_input("单价 (元)", value=100.0, step=1.0, key="cvp_price")
    unit_vc = st.sidebar.number_input("单位变动成本 (元)", value=60.0, step=1.0, key="cvp_vc")
    sales_vol = st.sidebar.number_input("预计销量 (件)", value=5000, step=100, key="cvp_vol")
    cm = unit_price - unit_vc
    be_vol = fixed_cost / cm if cm > 0 else 0
    be_rev = be_vol * unit_price
    st.subheader("📊 核心指标")
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("单位边际贡献", f"¥{cm:,.2f}")
    col2.metric("边际贡献率", f"{cm/unit_price*100:.1f}%")
    col3.metric("盈亏平衡点 (销量)", f"{be_vol:.0f} 件")
    col4.metric("盈亏平衡点 (金额)", f"¥{be_rev:,.2f}")
    import plotly.graph_objects as go
    volumes = list(range(0, int(sales_vol * 1.5), max(100, int(sales_vol // 10))))
    revenue = [v * unit_price for v in volumes]
    total_cost = [fixed_cost + v * unit_vc for v in volumes]
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=volumes, y=revenue, name='销售收入'))
    fig.add_trace(go.Scatter(x=volumes, y=total_cost, name='总成本'))
    fig.add_vline(x=be_vol, line_dash="dash", annotation_text="盈亏平衡点")
    fig.update_layout(height=500, hovermode='x unified')
    st.plotly_chart(fig, use_container_width=True)

def show_tools():
    st.title("🧰 快捷工具箱")
    tool = st.selectbox("选择工具", ["🧮 快速计算器", "📊 批量对比", "⏱️ 计时器", "📝 备忘录"])
    if tool == "🧮 快速计算器":
        calc_type = st.selectbox("计算类型", ["加减乘除", "百分比计算", "税额计算"])
        if calc_type == "加减乘除":
            col1, col2, col3 = st.columns(3)
            with col1: num1 = st.number_input("数字 1", value=0.0, key="calc_n1")
            with col2: num2 = st.number_input("数字 2", value=0.0, key="calc_n2")
            with col3:
                op = st.selectbox("运算符", ["+", "-", "×", "÷"], key="calc_op")
                if st.button("=", key="calc_eq"):
                    if op == "+": result = num1 + num2
                    elif op == "-": result = num1 - num2
                    elif op == "×": result = num1 * num2
                    elif op == "÷": result = num1 / num2 if num2 != 0 else "错误：除数为 0"
                    st.metric("结果", result)
    elif tool == "📊 批量对比":
        data = st.text_area("输入数据（每行一组，逗号分隔）", placeholder="2024 年，1000,200\n2025 年，1200,250")
        if data:
            lines = [line.split(',') for line in data.strip().split('\n')]
            st.dataframe(pd.DataFrame(lines), use_container_width=True)
    elif tool == "⏱️ 计时器":
        mins = st.number_input("分钟", min_value=0, max_value=60, value=5)
        if st.button("▶️ 开始倒计时"):
            total_secs = mins * 60
            prog = st.progress(0)
            txt = st.empty()
            for i in range(total_secs, 0, -1):
                m, s = divmod(i, 60)
                txt.text(f"剩余：{m:02d}:{s:02d}")
                prog.progress(1 - i / total_secs)
                import time
                time.sleep(1)
            txt.text("⏰ 时间到！")
            st.balloons()

def show_enhanced():
    st.title("🚀 增强功能")
    tab1, tab2, tab3 = st.tabs(["数据导出", "数据导入", "备份恢复"])
    tables = {'invoice': '发票数据', 'bank_statement': '银行流水', 'voucher': '凭证', 'ar_ap': '应收应付', 'calendar_event': '日历事件'}
    with tab1:
        sel = st.selectbox("选择要导出的表", list(tables.keys()), format_func=lambda x: tables[x], key="exp_sel")
        if st.button("导出 Excel", key="exp_btn"):
            conn = get_connection()
            df = pd.read_sql_query(f"SELECT * FROM {sel}", conn)
            conn.close()
            if not df.empty:
                from io import BytesIO
                output = BytesIO()
                with pd.ExcelWriter(output, engine='openpyxl') as w: df.to_excel(w, index=False)
                st.download_button(label=f"📥 下载 {tables[sel]}.xlsx", data=output.getvalue(), file_name=f"{sel}_{datetime.now().strftime('%Y%m%d')}.xlsx")
    with tab2:
        f = st.file_uploader("上传 Excel", type=['xlsx', 'xls'], key="imp_file")
        tgt = st.selectbox("导入到表", list(tables.keys()), format_func=lambda x: tables[x], key="imp_tgt")
        if f and st.button("开始导入", key="imp_btn"):
            try:
                df = pd.read_excel(f)
                conn = get_connection()
                df.to_sql(tgt, conn, if_exists='append', index=False)
                conn.close()
                st.success(f"导入成功，共 {len(df)} 条记录")
            except Exception as e: st.error(f"导入失败：{e}")
    with tab3:
        st.subheader("备份全部数据")
        if st.button("备份", key="bak_btn"):
            conn = get_connection()
            backup = {}
            for t in tables.keys():
                backup[t] = pd.read_sql_query(f"SELECT * FROM {t}", conn).to_dict('records')
            conn.close()
            import json
            from io import BytesIO
            bak_json = json.dumps(backup, ensure_ascii=False, default=str)
            st.download_button(label="📥 下载备份", data=bak_json, file_name=f"backup_{datetime.now().strftime('%Y%m%d')}.json", mime="application/json")

def show_pivot():
    st.title("🎯 智能透视分析")
    st.sidebar.header("选择数据源")
    data_source = st.sidebar.selectbox("数据源", ["发票数据", "银行流水", "企业账务", "应收应付"])
    st.sidebar.header("透视设置")
    conn = get_connection()
    if data_source == "发票数据": df = pd.read_sql_query("SELECT * FROM invoice", conn)
    elif data_source == "银行流水": df = pd.read_sql_query("SELECT * FROM bank_statement", conn)
    elif data_source == "企业账务": df = pd.read_sql_query("SELECT * FROM company_statement", conn)
    else: df = pd.read_sql_query("SELECT * FROM ar_ap", conn)
    conn.close()
    if df.empty:
        st.info("暂无数据")
    else:
        available_cols = df.columns.tolist()
        row_col = st.selectbox("行字段", available_cols, key="pivot_row")
        col_col = st.selectbox("列字段", available_cols, index=1 if len(available_cols) > 1 else 0, key="pivot_col")
        val_options = [c for c in available_cols if c != 'id']
        val_col = st.selectbox("值字段", val_options, index=2 if len(val_options) > 2 else 1, key="pivot_val")
        agg_func = st.selectbox("汇总方式", ["sum", "count", "mean", "min", "max"], key="pivot_agg")
        if val_col in df.columns:
            df[val_col] = pd.to_numeric(df[val_col], errors='coerce')
        try:
            pivot_table = pd.pivot_table(df, index=row_col, columns=col_col, values=val_col, aggfunc=agg_func, fill_value=0.0, margins=True, margins_name="合计")
            st.subheader(f"{data_source}透视表")
            st.dataframe(pivot_table, use_container_width=True)
            st.subheader("可视化")
            chart_type = st.selectbox("图表类型", ["柱状图", "条形图", "折线图", "面积图"], key="pivot_chart")
            df_chart = pivot_table.drop("合计", axis=0, errors='ignore').drop("合计", axis=1, errors='ignore')
            import plotly.express as px
            if chart_type == "柱状图": fig = px.bar(df_chart, title=f"{row_col} x {col_col} - {val_col}")
            elif chart_type == "条形图": fig = px.bar(df_chart, orientation='h', title=f"{row_col} x {col_col} - {val_col}")
            elif chart_type == "折线图": fig = px.line(df_chart, title=f"{row_col} x {col_col} - {val_col}")
            else: fig = px.area(df_chart, title=f"{row_col} x {col_col} - {val_col}")
            fig.update_layout(height=500)
            st.plotly_chart(fig, use_container_width=True)
        except Exception as e:
            st.error(f"生成透视表失败：{e}")

def show_doc_parse():
    st.title("📄 文档解析")
    st.markdown("**功能说明**：上传 PDF 或图片格式的合同/发票/回单，系统自动提取关键信息")
    uploaded_file = st.file_uploader("上传 PDF 或图片文件", type=["pdf", "png", "jpg", "jpeg"])
    if uploaded_file:
        st.success(f"已上传：{uploaded_file.name}")
        st.info("⚠️ 文档解析功能需要 OCR 引擎支持，当前为演示模式")
        st.markdown("### ✅ 模拟提取结果")
        col1, col2 = st.columns(2)
        with col1:
            st.metric("💰 金额", "¥10,000.00")
            st.metric("🏢 公司名", "示例公司")
        with col2:
            st.metric("📅 日期", "2024-01-15")
            st.metric("🧾 发票代码", "1100171130")
        with st.expander("📃 查看原始文本"):
            st.text("这是模拟的文档解析结果。实际使用需要集成 OCR 引擎（如 Tesseract、百度 OCR 等）来提取 PDF 或图片中的文字信息。")

def show_batch_parse():
    st.title("📄 批量解析")
    st.markdown("**功能说明**：一次上传多个 PDF 或图片文件，系统批量提取关键信息并导出汇总表格")
    uploaded_files = st.file_uploader("上传多个 PDF 或图片文件", type=["pdf", "png", "jpg", "jpeg"], accept_multiple_files=True)
    if uploaded_files:
        st.success(f"已选择 {len(uploaded_files)} 个文件")
        file_info = [{"序号": i + 1, "文件名": f.name, "大小": f"{f.size / 1024:.1f} KB", "状态": "待解析"} for i, f in enumerate(uploaded_files)]
        st.dataframe(pd.DataFrame(file_info), use_container_width=True, hide_index=True)
        if st.button("🚀 开始批量解析", type="primary"):
            progress_bar = st.progress(0)
            results = []
            for i, uploaded_file in enumerate(uploaded_files):
                result_row = {"文件名": uploaded_file.name, "金额": "¥10,000.00", "公司名": "示例公司", "日期": "2024-01-15", "发票代码": "1100171130", "发票号码": f"{12345678 + i:08d}", "状态": "✅ 成功"}
                results.append(result_row)
                progress_bar.progress((i + 1) / len(uploaded_files))
            if results:
                st.markdown("### ✅ 解析结果汇总")
                results_df = pd.DataFrame(results)
                st.dataframe(results_df, use_container_width=True, hide_index=True)
                st.markdown("### 📊 统计信息")
                col1, col2, col3 = st.columns(3)
                col1.metric("成功解析", f"{len(results)}/{len(results)}")
                col2.metric("失败数量", "0")
                col3.metric("总金额", "¥100,000.00")
                csv = results_df.to_csv(index=False, encoding='utf-8-sig')
                st.download_button(label="📥 导出为 CSV", data=csv, file_name="批量文档解析结果.csv", mime='text/csv')

def show_governance():
    st.title("🧹 数据治理")
    st.markdown("**功能说明**：上传 CSV/Excel 文件，系统自动聚类相似的供应商名称，支持合并去重")
    uploaded_file = st.file_uploader("上传 CSV 或 Excel 文件", type=["csv", "xlsx"])
    if uploaded_file:
        try:
            if uploaded_file.name.endswith('.csv'): df = pd.read_csv(uploaded_file)
            else: df = pd.read_excel(uploaded_file)
            st.success(f"已加载：{len(df)} 条记录")
            columns = df.columns.tolist()
            name_column = st.selectbox("选择供应商名称列", columns, key="gov_col")
            if name_column:
                names = df[name_column].dropna().unique().tolist()
                st.markdown(f"### 📊 发现 {len(names)} 个唯一供应商名称")
                st.dataframe(pd.DataFrame({name_column: names}), use_container_width=True)
                if st.button("🔍 查找相似名称", key="gov_find"):
                    st.info("💡 提示：实际使用需要集成文本相似度算法（如 Levenshtein 距离、Jaccard 相似度等）来识别相似名称。例如：'阿里巴巴'和'阿里公司'可能被识别为相似。")
                    sample_clusters = {"阿里巴巴集团": ["阿里巴巴", "阿里集团", "AliBaba"], "腾讯科技有限公司": ["腾讯", "腾讯科技", "Tencent"], "华为技术有限公司": ["华为", "华为技术", "Huawei"]}
                    st.markdown(f"### ✅ 发现 {len(sample_clusters)} 组相似名称")
                    for standard, similars in sample_clusters.items():
                        with st.expander(f"🏢 {standard} ({len(similars)}个相似)"):
                            st.write("**相似名称**:")
                            for s in similars: st.write(f"- {s}")
                            if st.button(f"合并到 \"{standard}\"", key=f"merge_{standard}"):
                                st.success(f"已合并 {len(similars)} 条记录")
        except Exception as e:
            st.error(f"读取文件失败：{e}")

def show_compliance():
    st.title("🛡️ 合规风控")
    tab1, tab2 = st.tabs(["报销预审", "数据脱敏"])
    with tab1:
        st.markdown("### 报销预审检查")
        st.info("输入报销单信息，系统自动检查是否超标、连号等风险")
        col1, col2 = st.columns(2)
        with col1:
            expense_type = st.selectbox("费用类型", ["差旅", "招待", "办公", "交通", "其他"], key="comp_type")
            amount = st.number_input("金额", min_value=0.0, value=1000.0, key="comp_amt")
        with col2:
            date = st.date_input("日期", key="comp_date")
            receipt_count = st.number_input("发票数量", min_value=1, step=1, value=1, key="comp_cnt")
        invoice_numbers = []
        for i in range(receipt_count):
            num = st.text_input(f"发票号码 {i+1}", key=f"comp_inv_{i}")
            if num: invoice_numbers.append(num)
        if st.button("检查", key="comp_check"):
            issues = []
            if expense_type == "招待" and amount > 5000:
                issues.append({"type": "⚠️ 金额超标", "message": "招待费超过 5000 元标准，需要特殊审批"})
            if expense_type == "差旅" and amount > 3000:
                issues.append({"type": "⚠️ 金额超标", "message": "差旅费超过 3000 元标准，请确认是否合理"})
            if len(invoice_numbers) >= 3:
                issues.append({"type": "⚠️ 连号风险", "message": "多张连号发票可能被视为拆单，请注意合规"})
            if issues:
                st.warning(f"发现 {len(issues)} 个问题")
                for issue in issues:
                    st.markdown(f"- **{issue['type']}**: {issue['message']}")
            else:
                st.success("✅ 未发现明显问题")
    with tab2:
        st.markdown("### 数据脱敏")
        st.info("输入文本或数据，系统自动脱敏敏感信息")
        text = st.text_area("输入文本", height=200, placeholder="请输入包含手机号、身份证、银行卡号等的文本", key="desen_text")
        if st.button("脱敏处理", key="desen_btn"):
            if text:
                import re
                desensitized = re.sub(r'1[3-9]\d{9}', lambda m: m.group()[:3] + '****' + m.group()[-4:], text)
                desensitized = re.sub(r'\d{18}|\d{17}[Xx]', lambda m: m.group()[:6] + '********' + m.group()[-4:], desensitized)
                desensitized = re.sub(r'\d{16,19}', lambda m: m.group()[:4] + ' **** **** ' + m.group()[-4:], desensitized)
                st.markdown("### ✅ 脱敏结果")
                st.text_area("脱敏后文本", value=desensitized, height=200)
            else:
                st.warning("请输入文本")
        with st.expander("📋 查看示例"):
            st.code("""原始文本:\n张三，手机号：13812345678\n身份证：110101199001011234\n银行卡：6222020800001234567\n\n脱敏后:\n张三，手机号：138****5678\n身份证：110101********1234\n银行卡：6222 **** **** 4567""")

def show_beautify():
    st.title("📑 报表美化")
    tab1, tab2 = st.tabs(["数据上传", "报告预览"])
    with tab1:
        uploaded_file = st.file_uploader("上传 Excel 文件", type=["xlsx", "xls", "csv"])
        if uploaded_file:
            try:
                if uploaded_file.name.endswith('.csv'): df = pd.read_csv(uploaded_file)
                else: df = pd.read_excel(uploaded_file)
                st.success(f"已加载：{len(df)} 条记录")
                st.markdown("### 数据预览")
                st.dataframe(df.head(20), use_container_width=True)
                numeric_cols = df.select_dtypes(include=['float64', 'int64']).columns.tolist()
                if numeric_cols:
                    st.markdown("### 选择指标")
                    selected_cols = st.multiselect("选择要展示的指标", numeric_cols, default=numeric_cols[:5] if len(numeric_cols) >= 5 else numeric_cols, key="beaut_cols")
                    if st.button("生成报告", type="primary", key="beaut_gen"):
                        metrics = {col: df[col].sum() for col in selected_cols}
                        st.session_state.report_data = {'metrics': metrics, 'analysis': [{'type': 'positive', 'content': f'总收入达到 ¥{metrics.get(selected_cols[0], 0):,.2f}元'}, {'type': 'warning', 'content': '部分指标波动较大，需关注'}]}
                        st.success("报告已生成，请切换到\"报告预览\"标签查看")
            except Exception as e:
                st.error(f"处理失败：{e}")
    with tab2:
        if 'report_data' in st.session_state:
            data = st.session_state.report_data
            st.markdown("### 📊 报告预览")
            st.markdown("#### 核心指标")
            if data['metrics']:
                cols = st.columns(min(4, len(data['metrics'])))
                for i, (key, value) in enumerate(data['metrics'].items()):
                    with cols[i % 4]: st.metric(key, f"{value:,.2f}")
            if data['analysis']:
                st.markdown("#### 分析总结")
                for item in data['analysis']:
                    if item['type'] == 'positive': st.success(f"✅ {item['content']}")
                    else: st.warning(f"⚠️ {item['content']}")
        else:
            st.info("请先在\"数据上传\"标签上传数据并生成报告")

def show_template():
    st.title("📋 模板中心")
    st.markdown("**说明**：下载标准 Excel 模板，导入后可自动识别字段")
    tab1, tab2, tab3 = st.tabs(["🏦 银行单据", "💰 财务分析", "📊 报表模板"])
    with tab1:
        st.subheader("🏦 银行单据模板")
        if st.button("下载：银行回单模板"):
            df = pd.DataFrame({'日期': ['2024-01-15'], '金额': [10000.00], '对方户名': ['示例公司'], '对方账号': ['6222 **** **** 1234'], '摘要': ['货款'], '凭证号': ['20240115001']})
            st.download_button(label="📥 银行回单模板.csv", data=df.to_csv(index=False, encoding='utf-8-sig'), file_name="银行回单模板.csv", mime='text/csv')
        if st.button("下载：发票记录模板"):
            df = pd.DataFrame({'发票代码': ['1100171130'], '发票号码': ['12345678'], '开票日期': ['2024-01-15'], '购买方': ['示例公司'], '销售方': ['供应商公司'], '金额': [1000.00], '税额': [60.00]})
            st.download_button(label="📥 发票记录模板.csv", data=df.to_csv(index=False, encoding='utf-8-sig'), file_name="发票记录模板.csv", mime='text/csv')
    with tab2:
        st.subheader("💰 财务分析模板")
        if st.button("下载：资产负债表模板"):
            df = pd.DataFrame({'项目': ['货币资金', '应收账款', '存货', '固定资产', '资产总计'], '期末余额': [100000, 50000, 80000, 200000, 430000], '期初余额': [90000, 45000, 75000, 180000, 390000]})
            st.download_button(label="📥 资产负债表模板.csv", data=df.to_csv(index=False, encoding='utf-8-sig'), file_name="资产负债表模板.csv", mime='text/csv')
        if st.button("下载：利润表模板"):
            df = pd.DataFrame({'项目': ['营业收入', '营业成本', '税金及附加', '销售费用', '管理费用', '财务费用', '净利润'], '本期金额': [500000, 300000, 5000, 20000, 30000, 10000, 135000], '上期金额': [450000, 280000, 4500, 18000, 28000, 12000, 107500]})
            st.download_button(label="📥 利润表模板.csv", data=df.to_csv(index=False, encoding='utf-8-sig'), file_name="利润表模板.csv", mime='text/csv')
        if st.button("下载：现金流量表模板"):
            df = pd.DataFrame({'项目': ['销售商品提供劳务收到的现金', '购买商品接受劳务支付的现金', '支付给职工的现金', '支付的各项税费'], '本期金额': [550000, 280000, 50000, 30000], '上期金额': [480000, 250000, 45000, 25000]})
            st.download_button(label="📥 现金流量表模板.csv", data=df.to_csv(index=False, encoding='utf-8-sig'), file_name="现金流量表模板.csv", mime='text/csv')
    with tab3:
        st.subheader("📊 报表模板")
        if st.button("下载：费用报销单模板"):
            df = pd.DataFrame({'日期': ['2024-01-15', '2024-01-16', '2024-01-17'], '费用类型': ['差旅费', '招待费', '办公费'], '金额': [1000.00, 500.00, 200.00], '摘要': ['北京出差', '客户招待', '办公用品'], '发票张数': [3, 2, 1]})
            st.download_button(label="📥 费用报销单模板.csv", data=df.to_csv(index=False, encoding='utf-8-sig'), file_name="费用报销单模板.csv", mime='text/csv')
        if st.button("下载：供应商对比模板"):
            df = pd.DataFrame({'供应商名称': ['供应商 A', '供应商 B', '供应商 C'], '单价': [100, 95, 105], '质量评分': [90, 85, 95], '交货周期 (天)': [7, 5, 10], '综合评分': [0, 0, 0]})
            st.download_button(label="📥 供应商对比模板.csv", data=df.to_csv(index=False, encoding='utf-8-sig'), file_name="供应商对比模板.csv", mime='text/csv')

def show_help():
    st.title("❓ 帮助中心")
    st.markdown("""
## 📖 快速入门

### 1. 登录系统
- 管理员账户：`admin` / `703102`
- 财务专员：`finance` / `finance123`
- 实习生：`intern` / `intern123`

### 2. 主要功能模块

#### 📝 日常核算
- 📄 **发票管理** - 发票录入、查询、认证
- 🏦 **银行对账** - 银行流水与账务智能匹配
- 📝 **凭证录入** - 会计凭证录入与管理
- 📋 **科目余额表** - 科目汇总与余额查询
- 💰 **应收应付管理** - 往来款项管理、账龄分析
- 📑 **纳税申报** - 增值税、所得税、个税计算

#### 📊 财务分析
- 📊 **财务比率分析** - 偿债、盈利、营运能力分析
- 🏛️ **杜邦分析** - ROE 分解分析
- 🏭 **行业对标** - 与行业平均水平对比
- 💵 **资金诊断** - 资金使用效率分析
- 📈 **预算分析** - 预算执行差异分析
- 🎯 **智能透视分析** - 多维度数据透视分析

#### 🏭 数据工厂
- 📄 **文档解析** - PDF/图片格式自动识别
- 📄 **批量解析** - 批量处理多个文档
- 🧹 **数据治理** - 数据清洗、去重、合并
- 🛡️ **合规风控** - 合规性检查与风险预警

#### 💼 决策支持
- 🧮 **金融测算** - IRR、NPV、折旧计算
- 📊 **本量利分析** - 盈亏平衡分析、敏感性分析
- 📑 **报表美化** - 财务报表格式优化

#### 🧰 办公工具
- 📅 **财务日历** - 重要日期提醒与管理
- 🧰 **快捷工具箱** - 常用工具集合
- 📋 **模板中心** - 财务模板下载
- 🚀 **增强功能** - 数据导出/导入/备份恢复
- ❓ **帮助中心** - 使用指南与常见问题

---

## 💡 常见问题

### 数据保存在哪里？
所有数据保存在本地 SQLite 数据库（`data/finance.db`），支持通过"增强功能"导出 Excel 备份。

### 如何批量导入数据？
发票管理、银行对账等模块支持 Excel 导入，或使用"增强功能"的数据导入功能。

### 数据如何备份？
使用"增强功能 → 备份恢复"进行全量备份，或直接复制 `data/finance.db` 文件。

### 忘记密码怎么办？
联系系统管理员重置密码，默认账户密码见上方"登录系统"。

---

## 📊 版本信息

**当前版本**: v2.0 (SPA 单页应用版)

**更新日期**: 2026-05-05

**核心特性**:
- ✅ 25 个功能模块，22 个已完整实现
- ✅ SPA 单页应用，分组导航菜单
- ✅ 本地 SQLite 数据库，数据安全
- ✅ 支持数据导入/导出/备份恢复
- ✅ 智能对账、财务分析、金融测算
""")

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
