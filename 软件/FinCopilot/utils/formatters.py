"""
FinCopilot - 数据格式化工具
复用《一键财报分析》formatters.py 核心逻辑
"""
from typing import Any


def format_currency(value: float, symbol: str = "¥") -> str:
    """
    格式化货币
    
    参数:
        value: 数值
        symbol: 货币符号
    
    返回:
        格式化后的字符串，如 ¥1,234.56
    """
    if value is None:
        return "-"
    return f"{symbol}{value:,.2f}"


def format_percentage(value: float, decimals: int = 2) -> str:
    """
    格式化百分比
    
    参数:
        value: 小数数值（如 0.15）
        decimals: 小数位数
    
    返回:
        格式化后的百分比字符串，如 15.00%
    """
    if value is None:
        return "-"
    return f"{value * 100:.{decimals}f}%"


def format_number(value: Any, decimals: int = 2) -> str:
    """
    格式化数字
    
    参数:
        value: 数值
        decimals: 小数位数
    
    返回:
        格式化后的字符串，如 1,234.56
    """
    if value is None:
        return "-"
    try:
        return f"{float(value):,.{decimals}f}"
    except:
        return str(value)


def format_date(date_str: str, format: str = "%Y-%m-%d") -> str:
    """
    格式化日期
    
    参数:
        date_str: 日期字符串
        format: 输出格式
    
    返回:
        格式化后的日期字符串
    """
    if not date_str:
        return "-"
    
    try:
        from datetime import datetime
        # 尝试多种格式解析
        for input_format in ["%Y-%m-%d", "%Y/%m/%d", "%Y%m%d", "%Y-%m-%d %H:%M:%S"]:
            try:
                dt = datetime.strptime(str(date_str), input_format)
                return dt.strftime(format)
            except:
                continue
        return str(date_str)
    except:
        return str(date_str)
