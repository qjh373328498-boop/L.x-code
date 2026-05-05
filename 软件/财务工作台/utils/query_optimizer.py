"""
财务工作台 - 数据库查询优化工具
提供分页查询、索引优化、批量操作等功能
"""
import streamlit as st
from typing import List, Dict, Any, Optional, Tuple
import sqlite3
from functools import wraps

# ========== 分页查询 ==========

@st.cache_data
def get_paginated_data(
    table: str,
    page: int = 1,
    page_size: int = 50,
    where_clause: str = "",
    params: tuple = (),
    order_by: str = "id DESC"
) -> Tuple[List[Dict], int]:
    """
    分页查询数据
    
    Args:
        table: 表名
        page: 页码（从 1 开始）
        page_size: 每页数量
        where_clause: WHERE 子句（不含 WHERE 关键字）
        params: 查询参数
        order_by: 排序子句
        
    Returns:
        (数据列表，总记录数)
    """
    from utils.database import get_connection
    
    conn = get_connection()
    cursor = conn.cursor()
    
    # 计算总数
    if where_clause:
        cursor.execute(f"SELECT COUNT(*) FROM {table} WHERE {where_clause}", params)
    else:
        cursor.execute(f"SELECT COUNT(*) FROM {table}")
    total = cursor.fetchone()[0]
    
    # 分页查询
    offset = (page - 1) * page_size
    query = f"SELECT * FROM {table}"
    if where_clause:
        query += f" WHERE {where_clause}"
    query += f" ORDER BY {order_by} LIMIT {page_size} OFFSET {offset}"
    
    cursor.execute(query, params)
    rows = cursor.fetchall()
    conn.close()
    
    return [dict(row) for row in rows], total


def render_pagination(total_records: int, page: int, page_size: int = 50):
    """
    渲染分页控件
    
    Args:
        total_records: 总记录数
        page: 当前页码
        page_size: 每页数量
    """
    total_pages = (total_records + page_size - 1) // page_size
    
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col1:
        st.write(f"共 **{total_records}** 条记录")
    
    with col2:
        if total_pages > 1:
            page_options = list(range(1, total_pages + 1))
            st.selectbox(
                "页码",
                page_options,
                index=min(page - 1, len(page_options) - 1),
                key=f"page_select_{page_size}",
                label_visibility="collapsed"
            )
    
    with col3:
        st.write(f"每页 {page_size} 条")


# ========== 懒加载 ==========

def lazy_load_data(key: str, load_func, *args, **kwargs):
    """
    懒加载数据：只有当用户需要时才加载
    
    Args:
        key: Session State 键
        load_func: 数据加载函数
        *args: 加载函数参数
        **kwargs: 加载函数关键字参数
    """
    if key not in st.session_state:
        st.session_state[key] = load_func(*args, **kwargs)
    return st.session_state[key]


# ========== 增量加载 ==========

def load_more_data(
    load_func,
    last_id: Optional[int] = None,
    batch_size: int = 100
) -> List[Dict]:
    """
    增量加载数据（基于 ID）
    
    Args:
        load_func: 加载函数，接受 last_id 和 limit 参数
        last_id: 上次加载的最后一条记录 ID
        batch_size: 每批加载数量
        
    Returns:
        新加载的数据列表
    """
    return load_func(last_id=last_id, limit=batch_size)


# ========== 批量操作优化 ==========

def batch_insert(
    table: str,
    columns: List[str],
    data: List[Tuple],
    batch_size: int = 1000
) -> int:
    """
    批量插入数据（事务优化）
    
    Args:
        table: 表名
        columns: 列名列表
        data: 数据列表
        batch_size: 每批插入数量
        
    Returns:
        成功插入的记录数
    """
    from utils.database import get_connection
    
    conn = get_connection()
    cursor = conn.cursor()
    
    placeholders = ",".join(["?" for _ in columns])
    column_names = ",".join(columns)
    sql = f"INSERT OR IGNORE INTO {table} ({column_names}) VALUES ({placeholders})"
    
    count = 0
    try:
        for i in range(0, len(data), batch_size):
            batch = data[i:i + batch_size]
            cursor.executemany(sql, batch)
            count += len(batch)
        conn.commit()
    except Exception as e:
        st.error(f"批量插入失败：{e}")
        conn.rollback()
    finally:
        conn.close()
    
    return count


# ========== 查询结果缓存装饰器 ==========

def query_cache(ttl: int = 300):
    """
    查询结果缓存装饰器（带 TTL）
    
    Args:
        ttl: 缓存时间（秒）
    """
    def decorator(func):
        @st.cache_data(ttl=ttl)
        @wraps(func)
        def wrapper(*args, **kwargs):
            return func(*args, **kwargs)
        return wrapper
    return decorator


# ========== 数据库索引建议 ==========

def suggest_indexes(table: str) -> List[str]:
    """
    为常用查询字段建议索引
    
    Args:
        table: 表名
        
    Returns:
        建议创建的索引列表
    """
    index_suggestions = {
        'invoice': [
            "CREATE INDEX IF NOT EXISTS idx_invoice_code ON invoice(code)",
            "CREATE INDEX IF NOT EXISTS idx_invoice_number ON invoice(number)",
            "CREATE INDEX IF NOT EXISTS idx_invoice_date ON invoice(date DESC)",
            "CREATE INDEX IF NOT EXISTS idx_invoice_supplier ON invoice(supplier)",
        ],
        'financial_metrics': [
            "CREATE INDEX IF NOT EXISTS idx_metrics_period ON financial_metrics(period DESC)",
            "CREATE INDEX IF NOT EXISTS idx_metrics_category ON financial_metrics(category)",
        ],
        'bank_transaction': [
            "CREATE INDEX IF NOT EXISTS idx_bank_date ON bank_transaction(date DESC)",
            "CREATE INDEX IF NOT EXISTS idx_bank_counterpart ON bank_transaction(counterparty)",
        ]
    }
    
    return index_suggestions.get(table, [])


def create_recommended_indexes(tables: List[str] = None):
    """
    为指定表创建推荐索引
    
    Args:
        tables: 表名列表，None 则处理所有已知表
    """
    from utils.database import get_connection
    
    if tables is None:
        tables = ['invoice', 'financial_metrics', 'bank_transaction']
    
    conn = get_connection()
    cursor = conn.cursor()
    
    created = []
    for table in tables:
        for sql in suggest_indexes(table):
            try:
                cursor.execute(sql)
                created.append(sql)
            except sqlite3.OperationalError:
                pass  # 索引已存在
    
    conn.commit()
    conn.close()
    
    return created
