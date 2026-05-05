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
