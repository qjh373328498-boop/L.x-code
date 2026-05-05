"""
财务工具箱 - 格式化工具
"""
from datetime import datetime


def format_currency(amount) -> str:
    """格式化金额为货币格式"""
    try:
        return f"¥{float(amount):,.2f}"
    except (ValueError, TypeError):
        return "¥0.00"


def format_number(num, decimals=2) -> str:
    """格式化数字（千分位）"""
    try:
        return f"{float(num):,.{decimals}f}"
    except (ValueError, TypeError):
        return "0"


def format_date(date_str: str, fmt: str = '%Y-%m-%d') -> str:
    """格式化日期"""
    if not date_str:
        return ""
    try:
        dt = datetime.strptime(date_str, '%Y-%m-%d')
        return dt.strftime(fmt)
    except ValueError:
        return date_str


def format_percentage(value, decimals=2) -> str:
    """格式化百分比"""
    try:
        return f"{float(value) * 100:.{decimals}f}%"
    except (ValueError, TypeError):
        return "0.00%"


def format_account_code(code: str) -> str:
    """格式化科目代码（添加空格分隔）"""
    if not code or len(code) < 4:
        return code
    return ' '.join([code[i:i+4] for i in range(0, len(code), 4)])


def get_period_label(period: str) -> str:
    """将期间字符串转换为可读标签"""
    if not period:
        return ""
    try:
        dt = datetime.strptime(period, '%Y-%m')
        return dt.strftime('%Y年%m月')
    except ValueError:
        return period


def get_quarter_label(period: str) -> str:
    """将月份转换为季度标签"""
    if not period:
        return ""
    try:
        dt = datetime.strptime(period, '%Y-%m')
        quarter = (dt.month - 1) // 3 + 1
        return f"{dt.year}年 Q{quarter}"
    except ValueError:
        return period
