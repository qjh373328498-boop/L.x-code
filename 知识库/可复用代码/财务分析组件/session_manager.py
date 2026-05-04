"""
Streamlit Session State 管理组件
来源：一键财报分析、财务工具箱、学创杯辅助软件
功能：统一的状态管理、数据缓存、用户输入持久化
"""

import streamlit as st
from typing import Any, Dict, Optional, Callable
from datetime import datetime
import pandas as pd


# ==================== 初始化函数 ====================

def init_session_state(defaults: Optional[Dict[str, Any]] = None) -> None:
    """
    初始化 Session State（带默认值）
    
    Args:
        defaults: 默认值字典
    """
    if defaults:
        for key, value in defaults.items():
            if key not in st.session_state:
                st.session_state[key] = value


def reset_session_state(keys: Optional[list] = None) -> None:
    """
    重置 Session State
    
    Args:
        keys: 要重置的键列表，None 表示全部重置
    """
    if keys:
        for key in keys:
            if key in st.session_state:
                del st.session_state[key]
    else:
        # 保留关键键，清除其他
        keep_keys = ['_page_loaded', '_user_authenticated', '_theme']
        all_keys = list(st.session_state.keys())
        for key in all_keys:
            if key not in keep_keys:
                del st.session_state[key]


# ==================== 数据缓存 ====================

@st.cache_data
def cache_financial_data() -> Dict[str, Any]:
    """
    缓存财务数据（避免重复加载）
    """
    # 示例：加载行业标准数据
    from pathlib import Path
    
    cache_file = Path("_data_cache.pkl")
    if cache_file.exists():
        import pickle
        with open(cache_file, 'rb') as f:
            return pickle.load(f)
    return {}


def get_cached_data(key: str, loader_func: Callable, ttl: int = 3600) -> Any:
    """
    获取缓存数据（如果不存在则加载）
    
    Args:
        key: 缓存键
        loader_func: 数据加载函数
        ttl: 缓存时间（秒）
    
    Returns:
        缓存的数据
    """
    cache_key = f"_cache_{key}"
    
    if cache_key not in st.session_state:
        st.session_state[cache_key] = {
            'data': loader_func(),
            'timestamp': datetime.now()
        }
    
    # 检查是否过期
    cache = st.session_state[cache_key]
    if (datetime.now() - cache['timestamp']).seconds > ttl:
        st.session_state[cache_key] = {
            'data': loader_func(),
            'timestamp': datetime.now()
        }
    
    return cache['data']


# ==================== 用户输入持久化 ====================

def save_user_input(key: str, value: Any) -> None:
    """
    保存用户输入到 Session State
    
    Args:
        key: 输入键
        value: 输入值
    """
    if '_user_inputs' not in st.session_state:
        st.session_state['_user_inputs'] = {}
    st.session_state['_user_inputs'][key] = value


def get_user_input(key: str, default: Any = None) -> Any:
    """
    获取用户输入
    
    Args:
        key: 输入键
        default: 默认值
    
    Returns:
        用户输入值或默认值
    """
    if '_user_inputs' not in st.session_state:
        return default
    return st.session_state['_user_inputs'].get(key, default)


def clear_user_inputs() -> None:
    """清空所有用户输入"""
    if '_user_inputs' in st.session_state:
        del st.session_state['_user_inputs']


# ==================== 页面导航 ====================

def navigate_to(page: str) -> None:
    """
    导航到指定页面
    
    Args:
        page: 页面路径
    """
    st.session_state['_current_page'] = page


def get_current_page() -> str:
    """获取当前页面"""
    return st.session_state.get('_current_page', '首页')


def is_page_loaded() -> bool:
    """检查页面是否已加载"""
    return st.session_state.get('_page_loaded', False)


# ==================== 表单管理 ====================

class FormManager:
    """
    表单管理器（处理多步骤表单）
    """
    
    def __init__(self, form_id: str, total_steps: int = 1):
        self.form_id = form_id
        self.total_steps = total_steps
        self._init_form()
    
    def _init_form(self) -> None:
        """初始化表单状态"""
        if f'_form_{self.form_id}_step' not in st.session_state:
            st.session_state[f'_form_{self.form_id}_step'] = 0
        if f'_form_{self.form_id}_data' not in st.session_state:
            st.session_state[f'_form_{self.form_id}_data'] = {}
    
    def get_step(self) -> int:
        """获取当前步骤"""
        return st.session_state[f'_form_{self.form_id}_step']
    
    def next_step(self) -> bool:
        """进入下一步"""
        current = self.get_step()
        if current < self.total_steps - 1:
            st.session_state[f'_form_{self.form_id}_step'] = current + 1
            return True
        return False
    
    def prev_step(self) -> bool:
        """返回上一步"""
        current = self.get_step()
        if current > 0:
            st.session_state[f'_form_{self.form_id}_step'] = current - 1
            return True
        return False
    
    def save_step_data(self, data: Dict[str, Any]) -> None:
        """保存当前步骤数据"""
        step = self.get_step()
        st.session_state[f'_form_{self.form_id}_data'][step] = data
    
    def get_all_data(self) -> Dict[str, Any]:
        """获取全部表单数据"""
        return st.session_state[f'_form_{self.form_id}_data']
    
    def reset(self) -> None:
        """重置表单"""
        st.session_state[f'_form_{self.form_id}_step'] = 0
        st.session_state[f'_form_{self.form_id}_data'] = {}


# ==================== 数据共享 ====================

class DataShare:
    """
    跨页面数据共享管理器
    """
    
    _storage_key = '_shared_data'
    
    @classmethod
    def set(cls, key: str, value: Any) -> None:
        """设置共享数据"""
        if cls._storage_key not in st.session_state:
            st.session_state[cls._storage_key] = {}
        st.session_state[cls._storage_key][key] = value
    
    @classmethod
    def get(cls, key: str, default: Any = None) -> Any:
        """获取共享数据"""
        if cls._storage_key not in st.session_state:
            return default
        return st.session_state[cls._storage_key].get(key, default)
    
    @classmethod
    def delete(cls, key: str) -> None:
        """删除共享数据"""
        if cls._storage_key in st.session_state:
            st.session_state[cls._storage_key].pop(key, None)
    
    @classmethod
    def clear(cls) -> None:
        """清空所有共享数据"""
        if cls._storage_key in st.session_state:
            del st.session_state[cls._storage_key]


# ==================== 主题管理 ====================

def set_theme(theme: str) -> None:
    """
    设置应用主题
    
    Args:
        theme: 主题名称 ('light', 'dark', 'auto')
    """
    st.session_state['_theme'] = theme


def get_theme() -> str:
    """获取当前主题"""
    return st.session_state.get('_theme', 'light')


# ==================== 使用示例 ====================

if __name__ == "__main__":
    # 初始化示例
    init_session_state({
        '_page_loaded': True,
        '_user_authenticated': False,
        'selected_industry': '制造业',
        'analysis_year': 2024
    })
    
    # 表单管理示例
    # form = FormManager('budget_form', total_steps=3)
    # if st.button("下一步"):
    #     form.next_step()
    
    # 数据共享示例
    # DataShare.set('financial_data', df)
    # df = DataShare.get('financial_data')
