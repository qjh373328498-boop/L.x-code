"""
FinCopilot - 财务比率计算
复用《一键财报分析》ratios.py 核心逻辑
"""
from typing import Dict, Any


def calculate_profitability_ratios(data: Dict[str, Any]) -> Dict[str, float]:
    """
    计算盈利能力比率
    
    参数:
        data: 财务数据字典，包含：
            - 营业收入
            - 营业成本
            - 净利润
            - 总资产
            - 股东权益
    
    返回:
        盈利能力比率字典
    """
    result = {}
    
    # 毛利率 = (营业收入 - 营业成本) / 营业收入
    revenue = data.get('营业收入', 0)
    cost = data.get('营业成本', 0)
    if revenue > 0:
        result['gross_margin'] = (revenue - cost) / revenue * 100
    else:
        result['gross_margin'] = 0
    
    # 净利率 = 净利润 / 营业收入
    net_profit = data.get('净利润', 0)
    if revenue > 0:
        result['net_margin'] = net_profit / revenue * 100
    else:
        result['net_margin'] = 0
    
    # ROA = 净利润 / 总资产
    total_assets = data.get('总资产', 0)
    if total_assets > 0:
        result['roa'] = net_profit / total_assets * 100
    else:
        result['roa'] = 0
    
    # ROE = 净利润 / 股东权益
    equity = data.get('股东权益', 0)
    if equity > 0:
        result['roe'] = net_profit / equity * 100
    else:
        result['roe'] = 0
    
    return result


def calculate_solvency_ratios(data: Dict[str, Any]) -> Dict[str, float]:
    """
    计算偿债能力比率
    
    参数:
        data: 财务数据字典，包含：
            - 流动资产
            - 流动负债
            - 总资产
            - 总负债
    
    返回:
        偿债能力比率字典
    """
    result = {}
    
    # 流动比率 = 流动资产 / 流动负债
    current_assets = data.get('流动资产', 0)
    current_liabilities = data.get('流动负债', 0)
    if current_liabilities > 0:
        result['current_ratio'] = current_assets / current_liabilities
    else:
        result['current_ratio'] = 0
    
    # 速动比率 = (流动资产 - 存货) / 流动负债
    inventory = data.get('存货', 0)
    if current_liabilities > 0:
        result['quick_ratio'] = (current_assets - inventory) / current_liabilities
    else:
        result['quick_ratio'] = 0
    
    # 资产负债率 = 总负债 / 总资产
    total_assets = data.get('总资产', 0)
    total_liabilities = data.get('总负债', 0)
    if total_assets > 0:
        result['debt_ratio'] = total_liabilities / total_assets * 100
    else:
        result['debt_ratio'] = 0
    
    return result


def calculate_efficiency_ratios(data: Dict[str, Any]) -> Dict[str, float]:
    """
    计算运营效率比率
    
    参数:
        data: 财务数据字典，包含：
            - 营业收入
            - 存货
            - 应收账款
    
    返回:
        运营效率比率字典
    """
    result = {}
    
    # 存货周转率 = 营业成本 / 平均存货
    cost = data.get('营业成本', 0)
    inventory = data.get('存货', 0)
    if inventory > 0:
        result['inventory_turnover'] = cost / inventory
    else:
        result['inventory_turnover'] = 0
    
    # 应收账款周转率 = 营业收入 / 平均应收账款
    revenue = data.get('营业收入', 0)
    receivables = data.get('应收账款', 0)
    if receivables > 0:
        result['receivables_turnover'] = revenue / receivables
    else:
        result['receivables_turnover'] = 0
    
    return result


def calculate_all_ratios(data: Dict[str, Any]) -> Dict[str, float]:
    """
    计算所有财务比率
    
    参数:
        data: 财务数据字典
    
    返回:
        所有比率的完整字典
    """
    result = {}
    result.update(calculate_profitability_ratios(data))
    result.update(calculate_solvency_ratios(data))
    result.update(calculate_efficiency_ratios(data))
    return result
