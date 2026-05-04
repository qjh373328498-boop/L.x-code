"""
一键财报分析 - 财务指标计算
"""
import pandas as pd
import numpy as np


def calculate_profitability_ratios(income_stmt: pd.DataFrame) -> dict:
    """计算盈利能力指标"""
    ratios = {}
    
    # 获取基础数据
    revenue = income_stmt.get('营业收入', 0)
    gross_profit = income_stmt.get('毛利', income_stmt.get('营业总收入', 0) - income_stmt.get('营业成本', 0))
    operating_profit = income_stmt.get('营业利润', 0)
    net_profit = income_stmt.get('净利润', 0)
    
    # 毛利率
    ratios['毛利率'] = (gross_profit / revenue * 100) if revenue > 0 else 0
    
    # 营业利润率
    ratios['营业利润率'] = (operating_profit / revenue * 100) if revenue > 0 else 0
    
    # 净利润率
    ratios['净利润率'] = (net_profit / revenue * 100) if revenue > 0 else 0
    
    # ROA（总资产收益率）
    total_assets = income_stmt.get('总资产', 0)
    ratios['ROA'] = (net_profit / total_assets * 100) if total_assets > 0 else 0
    
    # ROE（净资产收益率）
    equity = income_stmt.get('股东权益', 0)
    ratios['ROE'] = (net_profit / equity * 100) if equity > 0 else 0
    
    return ratios


def calculate_solvency_ratios(balance_sheet: pd.DataFrame) -> dict:
    """计算偿债能力指标"""
    ratios = {}
    
    current_assets = balance_sheet.get('流动资产', 0)
    current_liabilities = balance_sheet.get('流动负债', 0)
    inventory = balance_sheet.get('存货', 0)
    total_assets = balance_sheet.get('总资产', 0)
    total_liabilities = balance_sheet.get('总负债', 0)
    
    # 流动比率
    ratios['流动比率'] = (current_assets / current_liabilities) if current_liabilities > 0 else 0
    
    # 速动比率
    ratios['速动比率'] = ((current_assets - inventory) / current_liabilities) if current_liabilities > 0 else 0
    
    # 资产负债率
    ratios['资产负债率'] = (total_liabilities / total_assets * 100) if total_assets > 0 else 0
    
    # 权益乘数
    equity = total_assets - total_liabilities
    ratios['权益乘数'] = (total_assets / equity) if equity > 0 else 0
    
    return ratios


def calculate_efficiency_ratios(income_stmt: pd.DataFrame, balance_sheet: pd.DataFrame) -> dict:
    """计算运营效率指标"""
    ratios = {}
    
    revenue = income_stmt.get('营业收入', 0)
    cost = balance_sheet.get('存货', 0)
    inventory = balance_sheet.get('存货', 0)
    receivables = balance_sheet.get('应收账款', 0)
    total_assets = balance_sheet.get('总资产', 0)
    
    # 存货周转率
    ratios['存货周转率'] = (cost / inventory) if inventory > 0 else 0
    
    # 应收账款周转率
    ratios['应收账款周转率'] = (revenue / receivables) if receivables > 0 else 0
    
    # 总资产周转率
    ratios['总资产周转率'] = (revenue / total_assets) if total_assets > 0 else 0
    
    return ratios


def calculate_growth_ratios(current: dict, previous: dict) -> dict:
    """计算成长性指标"""
    ratios = {}
    
    # 营收增长率
    prev_revenue = previous.get('营业收入', 0)
    curr_revenue = current.get('营业收入', 0)
    ratios['营收增长率'] = ((curr_revenue - prev_revenue) / prev_revenue * 100) if prev_revenue > 0 else 0
    
    # 净利润增长率
    prev_net_profit = previous.get('净利润', 0)
    curr_net_profit = current.get('净利润', 0)
    ratios['净利润增长率'] = ((curr_net_profit - prev_net_profit) / prev_net_profit * 100) if prev_net_profit > 0 else 0
    
    # 总资产增长率
    prev_assets = previous.get('总资产', 0)
    curr_assets = current.get('总资产', 0)
    ratios['总资产增长率'] = ((curr_assets - prev_assets) / prev_assets * 100) if prev_assets > 0 else 0
    
    return ratios


def calculate_cash_flow_ratios(cash_flow: pd.DataFrame, income_stmt: pd.DataFrame) -> dict:
    """计算现金流指标"""
    ratios = {}
    
    operating_cash = cash_flow.get('经营活动现金流净额', 0)
    net_profit = income_stmt.get('净利润', 0)
    
    # 盈利现金比率
    ratios['盈利现金比率'] = (operating_cash / net_profit) if net_profit > 0 else 0
    
    # 销售收入现金率
    revenue = income_stmt.get('营业收入', 0)
    ratios['销售收入现金率'] = (operating_cash / revenue) if revenue > 0 else 0
    
    return ratios


def calculate_duPont_analysis(ratios: dict) -> dict:
    """杜邦分析"""
    duPont = {}
    
    net_margin = ratios.get('净利润率', 0) / 100
    asset_turnover = ratios.get('总资产周转率', 0)
    equity_multiplier = ratios.get('权益乘数', 1)
    
    duPont['净利率'] = net_margin * 100
    duPont['总资产周转率'] = asset_turnover
    duPont['权益乘数'] = equity_multiplier
    duPont['ROE'] = net_margin * asset_turnover * equity_multiplier * 100
    
    return duPont
