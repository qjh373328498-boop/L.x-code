"""
FinCopilot - 数据脱敏器
正则实现手机号/身份证/银行卡脱敏
"""
import re
from typing import Dict, Any


def desensitize_phone(phone: str) -> str:
    """
    手机号脱敏
    格式：138****1234
    """
    pattern = r'(\d{3})\d{4}(\d{4})'
    return re.sub(pattern, r'\1****\2', phone)


def desensitize_id_card(id_card: str) -> str:
    """
    身份证脱敏
    格式：110101********1234
    """
    if len(id_card) == 18:
        return id_card[:6] + '********' + id_card[-4:]
    elif len(id_card) == 15:
        return id_card[:6] + '******' + id_card[-3:]
    return id_card


def desensitize_bank_card(card: str) -> str:
    """
    银行卡脱敏
    格式：6222 **** **** 1234
    """
    # 去除空格
    card = card.replace(' ', '')
    if len(card) >= 16:
        return card[:4] + ' **** **** ' + card[-4:]
    return card


def desensitize_text(text: str) -> str:
    """
    批量脱敏文本中的敏感信息
    
    识别并脱敏：
    - 手机号
    - 身份证号
    - 银行卡号
    """
    # 手机号脱敏
    phone_pattern = r'(\d{3})\d{4}(\d{4})'
    text = re.sub(phone_pattern, r'\1****\2', text)
    
    # 身份证号脱敏（18 位）
    id_pattern = r'(\d{6})\d{8}(\w{4})'
    text = re.sub(id_pattern, r'\1********\2', text)
    
    # 银行卡脱敏
    bank_pattern = r'(\d{4})\s*\d{8,12}(\d{4})'
    text = re.sub(bank_pattern, r'\1 **** **** \2', text)
    
    return text


def desensitize_data(data: Dict[str, Any], fields: list = None) -> Dict[str, Any]:
    """
    脱敏字典数据
    
    参数:
        data: 数据字典
        fields: 需要脱敏的字段列表
    """
    if fields is None:
        fields = ['phone', 'id_card', 'bank_card', 'mobile']
    
    result = data.copy()
    
    for field in fields:
        if field in result:
            value = result[field]
            if isinstance(value, str):
                if field in ['phone', 'mobile']:
                    result[field] = desensitize_phone(value)
                elif field == 'id_card':
                    result[field] = desensitize_id_card(value)
                elif field == 'bank_card':
                    result[field] = desensitize_bank_card(value)
    
    return result
