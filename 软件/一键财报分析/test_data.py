"""
测试用模拟财报数据
"""
import pandas as pd

# 创建模拟财报数据
balance_sheet = {
    '货币资金': 50000000,
    '应收账款': 30000000,
    '存货': 20000000,
    '流动资产': 150000000,
    '固定资产': 80000000,
    '总资产': 250000000,
    '流动负债': 80000000,
    '总负债': 120000000,
    '股东权益': 130000000,
}

income_stmt = {
    '营业收入': 200000000,
    '营业成本': 120000000,
    '毛利': 80000000,
    '营业利润': 35000000,
    '净利润': 28000000,
}

cash_flow = {
    '经营活动现金流净额': 32000000,
    '投资活动现金流净额': -15000000,
    '筹资活动现金流净额': -5000000,
}

# 打印测试数据
print("=== 资产负债表 ===")
for k, v in balance_sheet.items():
    print(f"{k}: {v:,.0f}")

print("\n=== 利润表 ===")
for k, v in income_stmt.items():
    print(f"{k}: {v:,.0f}")

print("\n=== 现金流量表 ===")
for k, v in cash_flow.items():
    print(f"{k}: {v:,.0f}")

# 测试指标计算
import sys
sys.path.insert(0, 'utils')
from ratios import (
    calculate_profitability_ratios,
    calculate_solvency_ratios,
    calculate_efficiency_ratios,
    calculate_cash_flow_ratios
)

print("\n=== 计算结果 ===")
profit = calculate_profitability_ratios({**income_stmt, **balance_sheet})
print("盈利能力:")
for k, v in profit.items():
    print(f"  {k}: {v:.2f}")

solvency = calculate_solvency_ratios(balance_sheet)
print("\n偿债能力:")
for k, v in solvency.items():
    print(f"  {k}: {v:.2f}")

efficiency = calculate_efficiency_ratios(income_stmt, balance_sheet)
print("\n运营效率:")
for k, v in efficiency.items():
    print(f"  {k}: {v:.2f}")

cashflow = calculate_cash_flow_ratios(cash_flow, income_stmt)
print("\n现金流:")
for k, v in cashflow.items():
    print(f"  {k}: {v:.2f}")

print("\n✅ 所有计算完成！")
