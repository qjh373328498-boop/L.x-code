"""
缓存配置 - 全局缓存策略
减少重复计算，提升页面切换速度
"""
import streamlit as st
from functools import lru_cache

# ========== 页面切换缓存 ==========

@st.cache_data(ttl=3600)
def get_cached_data(key):
    """
    从 session_state 获取缓存数据
    ttl=3600 表示缓存 1 小时
    """
    return st.session_state.get(key, None)


# ========== 解析结果缓存 ==========

@st.cache_data(ttl=7200, show_spinner="正在缓存解析结果...")
def cache_financial_data(data_dict):
    """
    缓存解析后的财报数据
    避免页面切换时重复解析
    """
    return data_dict


# ========== 行业标准值缓存 ==========

@st.cache_data(ttl=86400)
def get_industry_standards(industry_name):
    """
    缓存行业标准值
    行业数据不变，缓存 24 小时
    """
    from utils.industry import get_industry_standard
    return get_industry_standard(industry_name)


# ========== 比率计算缓存 ==========

@st.cache_data(ttl=3600)
def calculate_ratios_cached(financial_data):
    """
    缓存财务比率计算结果
    """
    from utils.ratios import calculate_all_ratios
    return calculate_all_ratios(financial_data)


# ========== 可视化数据缓存 ==========

@st.cache_data(ttl=1800)
def prepare_chart_data(data_type, financial_data):
    """
    缓存图表数据预处理结果
    """
    if data_type == "trend":
        # 趋势分析数据准备
        return {
            "revenue": financial_data.get("income_stmt", {}).get("营业收入", 0),
            "net_profit": financial_data.get("income_stmt", {}).get("净利润", 0),
        }
    elif data_type == "structure":
        # 结构分析数据准备
        return {
            "assets": financial_data.get("balance_sheet", {}),
            "liabilities": financial_data.get("balance_sheet", {}),
        }
    return {}


# ========== Session State 初始化 ==========

def init_session_state():
    """
    统一初始化 session_state
    避免每次页面加载都检查
    """
    defaults = {
        'uploaded_file': None,
        'financial_data': None,
        'cached_analysis': None,
        'company_info': {},
        'industry': None,
        'ratios': None,
        'last_page': None,
    }
    
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value


# ========== 页面加载优化 ==========

@st.cache_resource
def get_page_cache():
    """
    缓存页面资源（只加载一次）
    """
    return {
        'css_loaded': False,
        'imports_done': False,
    }


def lazy_import(module_name):
    """
    延迟导入模块，减少首次加载时间
    """
    @st.cache_resource
    def _import():
        if module_name == "ratios":
            from utils import ratios
            return ratios
        elif module_name == "formatters":
            from utils import formatters
            return formatters
        elif module_name == "visualization":
            from utils import visualization
            return visualization
        return None
    return _import()
