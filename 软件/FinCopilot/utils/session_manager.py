"""
FinCopilot - 会话管理工具
简化版，复用《一键财报分析》session_manager.py 核心逻辑
"""
import streamlit as st
from typing import Any, Dict


def init_session_state(defaults: Dict[str, Any]) -> None:
    """
    初始化 Session State
    
    参数:
        defaults: 默认值字典
    """
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value


def get_session_value(key: str, default: Any = None) -> Any:
    """
    获取 Session State 值
    
    参数:
        key: 键名
        default: 默认值
    
    返回:
        值
    """
    return st.session_state.get(key, default)


def set_session_value(key: str, value: Any) -> None:
    """
    设置 Session State 值
    
    参数:
        key: 键名
        value: 值
    """
    st.session_state[key] = value


def clear_session_state(keys: list = None) -> None:
    """
    清空 Session State
    
    参数:
        keys: 要清空的键列表，None 则清空所有
    """
    if keys:
        for key in keys:
            if key in st.session_state:
                del st.session_state[key]
    else:
        st.session_state.clear()
