"""
财务工具箱 - 增强版数据库工具（带缓存）
"""
import sqlite3
import hashlib
import json
from datetime import datetime
from pathlib import Path
from typing import Optional, List, Dict, Any
import streamlit as st

DATA_DIR = Path(__file__).parent.parent / "data"
DATA_DIR.mkdir(exist_ok=True)
DB_PATH = DATA_DIR / "finance.db"


@st.cache_resource
def get_connection():
    """获取数据库连接（资源缓存）"""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    """初始化数据库表和索引"""
    conn = get_connection()
    cursor = conn.cursor()
    
    # 用户表
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            role TEXT DEFAULT 'user',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    # 发票表
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS invoice (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            code TEXT NOT NULL,
            number TEXT NOT NULL,
            date TEXT NOT NULL,
            amount REAL NOT NULL,
            type TEXT DEFAULT 'special',
            supplier TEXT,
            buyer TEXT,
            status TEXT DEFAULT 'normal',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            UNIQUE(code, number)
        )
    """)
    
    # 银行流水表
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS bank_statement (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            trans_date TEXT NOT NULL,
            trans_type TEXT NOT NULL,
            amount REAL NOT NULL,
            balance REAL,
            counterparty TEXT,
            summary TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    # 企业账务流水表
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS company_statement (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            trans_date TEXT NOT NULL,
            trans_type TEXT NOT NULL,
            amount REAL NOT NULL,
            counterparty TEXT,
            summary TEXT,
            voucher_no TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    # 凭证表
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS voucher (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            voucher_no TEXT NOT NULL,
            trans_date TEXT NOT NULL,
            attachment_count INTEGER DEFAULT 0,
            summary TEXT,
            created_by TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    # 凭证分录表
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS voucher_entry (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            voucher_id INTEGER NOT NULL,
            entry_type TEXT NOT NULL,
            subject_code TEXT NOT NULL,
            subject_name TEXT NOT NULL,
            amount REAL NOT NULL,
            FOREIGN KEY (voucher_id) REFERENCES voucher(id)
        )
    """)
    
    # 应收应付表
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS ar_ap (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            type TEXT NOT NULL,
            counterparty TEXT NOT NULL,
            amount REAL NOT NULL,
            date TEXT NOT NULL,
            due_date TEXT,
            status TEXT DEFAULT 'pending',
            summary TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    # 财务日历表
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS calendar_event (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            event_date TEXT NOT NULL,
            event_type TEXT DEFAULT 'reminder',
            description TEXT,
            is_recurring BOOLEAN DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    # 科目余额表
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS balance_sheet (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            period TEXT NOT NULL,
            subject_code TEXT NOT NULL,
            subject_name TEXT NOT NULL,
            opening_balance REAL DEFAULT 0,
            debit_amount REAL DEFAULT 0,
            credit_amount REAL DEFAULT 0,
            closing_balance REAL DEFAULT 0,
            direction TEXT DEFAULT 'debit',
            UNIQUE(period, subject_code)
        )
    """)
    
    # 财务指标表
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS financial_metrics (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            period TEXT NOT NULL,
            metric_name TEXT NOT NULL,
            value REAL NOT NULL,
            unit TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            UNIQUE(period, metric_name)
        )
    """)
    
    # 创建默认管理员账户 (密码：admin123)
    cursor.execute("SELECT COUNT(*) FROM users")
    if cursor.fetchone()[0] == 0:
        password_hash = hashlib.sha256("admin123".encode()).hexdigest()
        cursor.execute(
            "INSERT INTO users (username, password_hash, role) VALUES (?, ?, ?)",
            ("admin", password_hash, "admin")
        )
    
    conn.commit()
    conn.close()


def check_user(username: str, password: str) -> bool:
    """验证用户登录"""
    conn = get_connection()
    cursor = conn.cursor()
    password_hash = hashlib.sha256(password.encode()).hexdigest()
    cursor.execute(
        "SELECT * FROM users WHERE username=? AND password_hash=?",
        (username, password_hash)
    )
    user = cursor.fetchone()
    conn.close()
    return user is not None


def get_user_role(username: str) -> str:
    """获取用户角色"""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT role FROM users WHERE username=?", (username,))
    row = cursor.fetchone()
    conn.close()
    return row['role'] if row else 'guest'


def export_to_excel(table_name: str, output_path: str) -> bool:
    """导出数据到 Excel"""
    try:
        import pandas as pd
        conn = get_connection()
        df = pd.read_sql_query(f"SELECT * FROM {table_name}", conn)
        conn.close()
        df.to_excel(output_path, index=False)
        return True
    except Exception as e:
        print(f"导出失败：{e}")
        return False


def import_from_excel(table_name: str, excel_path: str) -> int:
    """从 Excel 导入数据"""
    try:
        import pandas as pd
        df = pd.read_excel(excel_path)
        conn = get_connection()
        count = 0
        for _, row in df.iterrows():
            try:
                columns = ', '.join(row.index)
                placeholders = ', '.join(['?' for _ in row])
                cursor = conn.cursor()
                cursor.execute(
                    f"INSERT OR REPLACE INTO {table_name} ({columns}) VALUES ({placeholders})",
                    tuple(row.values)
                )
                count += 1
            except Exception:
                continue
        conn.commit()
        conn.close()
        return count
    except Exception as e:
        print(f"导入失败：{e}")
        return 0


def get_dashboard_stats() -> Dict[str, Any]:
    """获取仪表盘统计数据"""
    conn = get_connection()
    cursor = conn.cursor()
    
    stats = {}
    
    # 发票统计
    cursor.execute("SELECT COUNT(*), SUM(amount) FROM invoice")
    row = cursor.fetchone()
    stats['invoice_count'] = row[0] if row[0] else 0
    stats['invoice_total'] = row[1] if row[1] else 0
    
    # 应收账款统计
    cursor.execute("SELECT SUM(amount) FROM ar_ap WHERE type='AR' AND status='pending'")
    row = cursor.fetchone()
    stats['ar_total'] = row[0] if row[0] else 0
    
    # 应付账款统计
    cursor.execute("SELECT SUM(amount) FROM ar_ap WHERE type='AP' AND status='pending'")
    row = cursor.fetchone()
    stats['ap_total'] = row[0] if row[0] else 0
    
    # 日历事件统计
    cursor.execute("SELECT COUNT(*) FROM calendar_event WHERE event_date >= date('now')")
    row = cursor.fetchone()
    stats['upcoming_events'] = row[0] if row[0] else 0
    
    conn.close()
    return stats


def clear_all_data(confirm: bool = False) -> bool:
    """清空所有数据（需要确认）"""
    if not confirm:
        return False
    
    conn = get_connection()
    cursor = conn.cursor()
    
    tables = ['voucher_entry', 'voucher', 'ar_ap', 'calendar_event', 
              'balance_sheet', 'financial_metrics', 'company_statement', 
              'bank_statement', 'invoice']
    
    for table in tables:
        try:
            cursor.execute(f"DELETE FROM {table}")
        except Exception:
            pass
    
    conn.commit()
    conn.close()
    return True


def create_indexes():
    """创建数据库索引，优化查询性能"""
    conn = get_connection()
    cursor = conn.cursor()
    
    indexes = [
        # 发票表索引
        "CREATE INDEX IF NOT EXISTS idx_invoice_code ON invoice(code)",
        "CREATE INDEX IF NOT EXISTS idx_invoice_number ON invoice(number)",
        "CREATE INDEX IF NOT EXISTS idx_invoice_date ON invoice(date DESC)",
        "CREATE INDEX IF NOT EXISTS idx_invoice_supplier ON invoice(supplier)",
        "CREATE INDEX IF NOT EXISTS idx_invoice_buyer ON invoice(buyer)",
        
        # 凭证表索引
        "CREATE INDEX IF NOT EXISTS idx_voucher_date ON voucher_entry(date DESC)",
        "CREATE INDEX IF NOT EXISTS idx_voucher_type ON voucher_entry(type)",
        
        # 应收应付索引
        "CREATE INDEX IF NOT EXISTS idx_ar_ap_date ON ar_ap(due_date)",
        "CREATE INDEX IF NOT EXISTS idx_ar_ap_type ON ar_ap(type)",
        "CREATE INDEX IF NOT EXISTS idx_ar_ap_status ON ar_ap(status)",
        
        # 财务指标索引
        "CREATE INDEX IF NOT EXISTS idx_metrics_period ON financial_metrics(period DESC)",
        "CREATE INDEX IF NOT EXISTS idx_metrics_category ON financial_metrics(category)",
        
        # 日历事件索引
        "CREATE INDEX IF NOT EXISTS idx_calendar_date ON calendar_event(event_date)",
        
        # 银行对账索引
        "CREATE INDEX IF NOT EXISTS idx_bank_date ON bank_statement(statement_date DESC)",
        "CREATE INDEX IF NOT EXISTS idx_bank_amount ON bank_statement(amount)",
    ]
    
    created_count = 0
    for sql in indexes:
        try:
            cursor.execute(sql)
            created_count += 1
        except Exception:
            pass  # 表不存在或索引已存在
    
    conn.commit()
    conn.close()
    return created_count


if __name__ == "__main__":
    init_db()
    print("✅ 数据库初始化完成")
    
    # 创建索引
    index_count = create_indexes()
    print(f"📁 创建 {index_count} 个数据库索引")
    
    # 显示统计
    stats = get_dashboard_stats()
    print(f"📊 数据统计:")
    print(f"   发票总数：{stats['invoice_count']}")
    print(f"   发票总额：¥{stats['invoice_total']:,.2f}")
    print(f"   应收账款：¥{stats['ar_total']:,.2f}")
    print(f"   应付账款：¥{stats['ap_total']:,.2f}")
    print(f"   即将到期事件：{stats['upcoming_events']}")
