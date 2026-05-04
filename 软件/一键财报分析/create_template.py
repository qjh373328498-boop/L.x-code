"""
生成 Excel 模板文件
"""
import pandas as pd

# 创建模板文件（数据平衡：资产 2.5 亿 = 负债 1.2 亿 + 权益 1.3 亿）
with pd.ExcelWriter('/workspace/软件/一键财报分析/财报模板.xlsx', engine='xlsxwriter') as writer:
    # 资产负债表
    balance_data = pd.DataFrame({
        '项目': ['货币资金', '应收账款', '存货', '流动资产合计', '固定资产', '资产总计', 
                '流动负债合计', '负债合计', '所有者权益合计'],
        '期末余额': [50000000, 30000000, 20000000, 150000000, 100000000, 250000000, 60000000, 120000000, 130000000],
        '期初余额': [45000000, 28000000, 18000000, 140000000, 90000000, 230000000, 55000000, 110000000, 120000000]
    })
    balance_data.to_excel(writer, sheet_name='资产负债表', index=False)
    
    # 利润表
    income_data = pd.DataFrame({
        '项目': ['营业总收入', '营业收入', '营业成本', '营业利润', '净利润'],
        '本期金额': [200000000, 200000000, 120000000, 35000000, 28000000],
        '上期金额': [180000000, 180000000, 110000000, 30000000, 24000000]
    })
    income_data.to_excel(writer, sheet_name='利润表', index=False)
    
    # 现金流量表
    cash_data = pd.DataFrame({
        '项目': ['经营活动产生的现金流量净额', '投资活动产生的现金流量净额', 
                '筹资活动产生的现金流量净额'],
        '本期金额': [32000000, -15000000, -5000000],
        '上期金额': [28000000, -12000000, -8000000]
    })
    cash_data.to_excel(writer, sheet_name='现金流量表', index=False)

import os
# 重新解析验证
from utils.parser import parse_excel
from utils.ratios import calculate_solvency_ratios, calculate_duPont_analysis

result = parse_excel('/workspace/软件/一键财报分析/财报模板.xlsx')
balance = result.get('balance_sheet', {})
solvency = calculate_solvency_ratios(balance)

print("\n=== 验证修复后的数据 ===")
print(f"总负债：{balance.get('总负债', 0):,.0f}")
print(f"权益乘数：{solvency.get('权益乘数', 0):.2f}")

dupont = calculate_duPont_analysis({**solvency, '净利润率': 14.0, '总资产周转率': 0.8})
print(f"杜邦分析 ROE: {dupont['ROE']:.2f}%")
