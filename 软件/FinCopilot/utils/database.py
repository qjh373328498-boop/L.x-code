"""
FinCopilot - 数据库管理
简化版 SQLite 工具
"""
import sqlite3
from typing import List, Dict, Any


def get_connection(db_path: str = ":memory:") -> sqlite3.Connection:
    """
    获取数据库连接
    
    参数:
        db_path: 数据库路径
    
    返回:
        Connection 对象
    """
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row  # 返回字典格式
    return conn


def execute_query(conn: sqlite3.Connection, query: str, params: tuple = ()) -> List[Dict]:
    """
    执行查询
    
    参数:
        conn: 连接对象
        query: SQL 查询
        params: 参数
    
    返回:
        结果列表
    """
    cursor = conn.execute(query, params)
    return [dict(row) for row in cursor.fetchall()]


def execute_update(conn: sqlite3.Connection, query: str, params: tuple = ()) -> int:
    """
    执行更新/插入/删除
    
    参数:
        conn: 连接对象
        query: SQL 语句
        params: 参数
    
    返回:
        影响的行数
    """
    cursor = conn.execute(query, params)
    conn.commit()
    return cursor.rowcount


def create_table(conn: sqlite3.Connection, table_name: str, columns: Dict[str, str]) -> bool:
    """
    创建表
    
    参数:
        conn: 连接对象
        table_name: 表名
        columns: 列定义字典 {列名：类型}
    
    返回:
        是否成功
    """
    cols = ", ".join([f"{col} {dtype}" for col, dtype in columns.items()])
    query = f"CREATE TABLE IF NOT EXISTS {table_name} ({cols})"
    
    try:
        conn.execute(query)
        conn.commit()
        return True
    except Exception as e:
        print(f"创建表失败：{e}")
        return False


def insert_record(conn: sqlite3.Connection, table_name: str, data: Dict[str, Any]) -> int:
    """
    插入记录
    
    参数:
        conn: 连接对象
        table_name: 表名
        data: 数据字典
    
    返回:
        插入的行 ID
    """
    columns = ", ".join(data.keys())
    placeholders = ", ".join(["?" for _ in data])
    values = tuple(data.values())
    
    query = f"INSERT INTO {table_name} ({columns}) VALUES ({placeholders})"
    
    try:
        cursor = conn.execute(query, values)
        conn.commit()
        return cursor.lastrowid
    except Exception as e:
        print(f"插入失败：{e}")
        return -1
