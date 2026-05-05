"""
财务工作台 - 页面初始化助手
统一页面初始化和常用功能
"""
import streamlit as st
from .database import init_db
from .constants import UI, CacheTTL


def init_page(title: str, icon: str = UI.DEFAULT_ICON, layout: str = UI.DEFAULT_LAYOUT):
    """
    统一页面初始化
    
    Args:
        title: 页面标题
        icon: 页面图标 emoji
        layout: 布局模式 ('wide' 或 'centered')
    """
    st.set_page_config(
        page_title=title,
        page_icon=icon,
        layout=layout,
        initial_sidebar_state="expanded"
    )
    init_db()


def render_page_header(title: str, icon: str = None, show_help: bool = True):
    """渲染页面头部"""
    if icon:
        st.title(f"{icon} {title}")
    else:
        st.title(title)


def get_dashboard_stats():
    """获取仪表盘统计数据"""
    from .database import get_connection
    import pandas as pd
    
    conn = get_connection()
    
    try:
        invoice_df = pd.read_sql_query("SELECT COUNT(*) as count, COALESCE(SUM(amount), 0) as total FROM invoice", conn)
        invoice_count = int(invoice_df['count'].iloc[0]) if not invoice_df.empty else 0
        invoice_total = float(invoice_df['total'].iloc[0]) if not invoice_df.empty else 0.0
    except Exception:
        invoice_count = 0
        invoice_total = 0.0
    
    try:
        ar_ap_df = pd.read_sql_query("""
            SELECT 
                COALESCE(SUM(CASE WHEN type = 'AR' THEN amount ELSE 0 END), 0) as ar_total,
                COALESCE(SUM(CASE WHEN type = 'AP' THEN amount ELSE 0 END), 0) as ap_total
            FROM ar_ap
        """, conn)
        ar_total = float(ar_ap_df['ar_total'].iloc[0]) if not ar_ap_df.empty else 0.0
        ap_total = float(ar_ap_df['ap_total'].iloc[0]) if not ar_ap_df.empty else 0.0
    except Exception:
        ar_total = 0.0
        ap_total = 0.0
    
    conn.close()
    
    return {
        'invoice_count': invoice_count,
        'invoice_total': invoice_total,
        'ar_total': ar_total,
        'ap_total': ap_total,
    }
