"""
财务工具箱 - 数据验证工具
"""
import re
from datetime import datetime


def validate_invoice_code(code: str) -> bool:
    """验证发票代码格式（10 位或 12 位数字）"""
    if not code:
        return False
    return bool(re.match(r'^\d{10}(\d{2})?$', code))


def validate_invoice_number(number: str) -> bool:
    """验证发票号码格式（8 位数字）"""
    if not number:
        return False
    return bool(re.match(r'^\d{8}$', number))


def validate_amount(amount) -> bool:
    """验证金额（正数）"""
    try:
        return float(amount) >= 0
    except (ValueError, TypeError):
        return False


def validate_date(date_str: str) -> bool:
    """验证日期格式（YYYY-MM-DD）"""
    if not date_str:
        return False
    try:
        datetime.strptime(date_str, '%Y-%m-%d')
        return True
    except ValueError:
        return False


def validate_phone(phone: str) -> bool:
    """验证手机号码格式"""
    if not phone:
        return False
    return bool(re.match(r'^1[3-9]\d{9}$', phone))


def validate_tax_id(tax_id: str) -> bool:
    """验证纳税人识别号（15-20 位）"""
    if not tax_id:
        return False
    return bool(re.match(r'^[A-Z0-9]{15,20}$', tax_id.upper()))


def validate_bank_account(account: str) -> bool:
    """验证银行账号（16-20 位数字）"""
    if not account:
        return False
    return bool(re.match(r'^\d{16,20}$', account))


def format_currency(amount) -> str:
    """格式化金额（千分位，两位小数）"""
    try:
        return f"{float(amount):,.2f}"
    except (ValueError, TypeError):
        return "0.00"


def parse_amount(amount_str: str) -> float:
    """解析金额字符串（支持千分位）"""
    if not amount_str:
        return 0.0
    try:
        return float(amount_str.replace(',', ''))
    except ValueError:
        return 0.0
