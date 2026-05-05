"""
FinCopilot - 金融计算器
numpy-financial 实现折旧/IRR/NPV/年金计算
"""
import numpy_financial as npf
from typing import Dict, Any


def straight_line_depreciation(cost: float, salvage: float, life: int) -> Dict[str, float]:
    """
    直线折旧法
    
    参数:
        cost: 原值
        salvage: 残值
        life: 使用年限
    
    返回:
        年折旧额、累计折旧等
    """
    annual_dep = (cost - salvage) / life
    
    # 计算每年的折旧
    schedule = []
    book_value = cost
    for year in range(1, life + 1):
        depreciation = annual_dep
        book_value -= depreciation
        schedule.append({
            'year': year,
            'depreciation': depreciation,
            'book_value': book_value
        })
    
    return {
        'annual_depreciation': annual_dep,
        'total_depreciation': cost - salvage,
        'schedule': schedule
    }


def double_declining_balance(cost: float, salvage: float, life: int) -> Dict[str, Any]:
    """
    双倍余额递减法
    
    参数:
        cost: 原值
        salvage: 残值
        life: 使用年限
    """
    rate = 2.0 / life
    
    schedule = []
    book_value = cost
    for year in range(1, life + 1):
        depreciation = book_value * rate
        book_value -= depreciation
        
        # 最后一年调整
        if year == life:
            depreciation = book_value - salvage
            book_value = salvage
        
        schedule.append({
            'year': year,
            'depreciation': depreciation,
            'book_value': book_value
        })
    
    return {
        'rate': rate,
        'schedule': schedule
    }


def calculate_irr(cash_flows: list) -> float:
    """
    内部收益率 (IRR)
    
    参数:
        cash_flows: 现金流列表，如 [-10000, 3000, 4000, 5000, 6000]
    """
    return npf.irr(cash_flows)


def calculate_npv(cash_flows: list, rate: float) -> float:
    """
    净现值 (NPV)
    
    参数:
        cash_flows: 现金流列表
        rate: 折现率
    """
    return npf.npv(rate, cash_flows)


def calculate_pmt(rate: float, nper: int, pv: float, fv: float = 0) -> float:
    """
    年金支付额（PMT）
    
    参数:
        rate: 利率
        nper: 期数
        pv: 现值
        fv: 终值（可选，默认 0）
    """
    return npf.pmt(rate, nper, pv, fv)


def calculate_pv(rate: float, nper: int, pmt: float, fv: float = 0) -> float:
    """
    现值 (PV)
    
    参数:
        rate: 利率
        nper: 期数
        pmt: 每期支付额
        fv: 终值（可选，默认 0）
    """
    return npf.pv(rate, nper, pmt, fv)


def calculate_fv(rate: float, nper: int, pmt: float, pv: float = 0) -> float:
    """
    终值 (FV)
    
    参数:
        rate: 利率
        nper: 期数
        pmt: 每期支付额
        pv: 现值（可选，默认 0）
    """
    return npf.fv(rate, nper, pmt, pv)


def calculate_nper(rate: float, pmt: float, pv: float, fv: float = 0) -> float:
    """
    期数 (NPER)
    
    参数:
        rate: 利率
        pmt: 每期支付额
        pv: 现值
        fv: 终值（可选，默认 0）
    """
    return npf.nper(rate, pmt, pv, fv)
