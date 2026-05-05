"""
财务工作台 - 缓存配置模块
提供统一的缓存装饰器和缓存管理功能
"""
import streamlit as st
from functools import wraps
import hashlib
import json
from typing import Any, Callable, TypeVar, Union
from pathlib import Path

# ========== Streamlit 原生缓存装饰器 ==========

# 数据缓存 - 用于纯函数（如数据加载、计算）
cache_data = st.cache_data

# 资源缓存 - 用于不可序列化对象（如数据库连接、模型）
cache_resource = st.cache_resource


# ========== 数据库查询缓存 ==========

@cache_data(ttl=300)  # 5 分钟缓存
def get_cached_query(query: str, params: tuple = None) -> list:
    """
    带缓存的数据库查询
    
    Args:
        query: SQL 查询语句
        params: 查询参数
        
    Returns:
        查询结果列表
    """
    from utils.database import get_connection
    
    conn = get_connection()
    cursor = conn.cursor()
    
    if params:
        cursor.execute(query, params)
    else:
        cursor.execute(query)
    
    results = cursor.fetchall()
    conn.close()
    
    return [dict(row) for row in results]


# ========== 计算结果缓存 ==========

@cache_data
def cached_calculate(function_name: str, *args, **kwargs) -> Any:
    """
    通用计算结果缓存
    
    Args:
        function_name: 函数名称（用于区分不同计算）
        *args: 位置参数
        **kwargs: 关键字参数
        
    Returns:
        计算结果
    """
    # 根据参数生成缓存键
    cache_key = hashlib.md5(
        json.dumps({
            'function': function_name,
            'args': args,
            'kwargs': kwargs
        }, default=str).encode()
    ).hexdigest()
    
    # 这里可以根据需要从 session_state 或外部存储读取缓存
    # 目前依赖 @cache_data 自动管理
    return None


# ========== 页面级缓存 ==========

def page_cache(ttl: int = 300):
    """
    页面级缓存装饰器
    
    Args:
        ttl: 缓存时间（秒），默认 5 分钟
        
    Use case:
        @page_cache(ttl=600)
        def load_page_data():
            # 加载页面数据
            pass
    """
    def decorator(func: Callable) -> Callable:
        @cache_data(ttl=ttl)
        @wraps(func)
        def wrapper(*args, **kwargs):
            return func(*args, **kwargs)
        return wrapper
    return decorator


# ========== 大数据集缓存 ==========

@cache_data
def load_large_dataset(table_name: str, limit: int = None) -> list:
    """
    加载大数据集（带分页缓存）
    
    Args:
        table_name: 表名
        limit: 限制返回行数
        
    Returns:
        数据列表
    """
    from utils.database import get_connection
    
    conn = get_connection()
    cursor = conn.cursor()
    
    if limit:
        cursor.execute(f"SELECT * FROM {table_name} LIMIT ?", (limit,))
    else:
        cursor.execute(f"SELECT * FROM {table_name}")
    
    results = cursor.fetchall()
    conn.close()
    
    return [dict(row) for row in results]


# ========== 清除缓存 ==========

def clear_cache(scope: str = 'all'):
    """
    清除缓存
    
    Args:
        scope: 清除范围
            - 'all': 清除所有缓存
            - 'data': 清除数据缓存
            - 'resource': 清除资源缓存
    """
    if scope in ('all', 'data'):
        cache_data.clear()
    
    if scope in ('all', 'resource'):
        cache_resource.clear()


# ========== 缓存状态显示 ==========

def show_cache_status():
    """显示缓存状态信息"""
    import psutil
    import os
    
    process = psutil.Process(os.getpid())
    memory_info = process.memory_info()
    
    with st.expander("📊 缓存状态", expanded=False):
        st.write(f"**内存使用**: {memory_info.rss / 1024 / 1024:.2f} MB")
        st.write(f"**缓存策略**: 数据缓存 TTL=300s")
        
        if st.button("🗑️ 清除所有缓存"):
            clear_cache('all')
            st.success("缓存已清除，页面将刷新")
            st.rerun()
