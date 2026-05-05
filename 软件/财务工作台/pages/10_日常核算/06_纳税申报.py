"""
🧾 纳税申报 - 税费计算与申报
"""
import streamlit as st
import pandas as pd

# ========== 性能优化 ==========
# Session State: 保存用户输入
if '_session_init' not in st.session_state:
    st.session_state._session_init = True

from utils.formatters import format_currency

st.set_page_config(page_title="纳税申报", page_icon="🧾", layout="wide")

st.title("🧾 纳税申报计算器")

tab1, tab2, tab3 = st.tabs(["增值税", "企业所得税", "个税计算"])

with tab1:
    st.subheader("增值税计算")
    
    col1, col2 = st.columns(2)
    
    with col1:
        sales_amount = st.number_input("不含税销售额", min_value=0.0, step=1000.0)
        purchase_amount = st.number_input("不含税采购额", min_value=0.0, step=1000.0)
        tax_rate = st.selectbox("适用税率", [0.13, 0.09, 0.06, 0.03], format_func=lambda x: f"{x*100:.0f}%")
    
    with col2:
        output_tax = sales_amount * tax_rate
        input_tax = purchase_amount * tax_rate
        payable_tax = output_tax - input_tax
        
        st.metric("销项税额", format_currency(output_tax))
        st.metric("进项税额", format_currency(input_tax))
        st.metric("应纳增值税", format_currency(max(0, payable_tax)))
    
    if payable_tax < 0:
        st.info(f"留抵税额：{format_currency(abs(payable_tax))}")

with tab2:
    st.subheader("企业所得税计算")
    
    col1, col2 = st.columns(2)
    
    with col1:
        revenue = st.number_input("营业收入", min_value=0.0, step=10000.0)
        cogs = st.number_input("营业成本", min_value=0.0, step=10000.0)
        operating_expenses = st.number_input("期间费用", min_value=0.0, step=10000.0)
        other_income = st.number_input("其他收益", min_value=0.0, step=10000.0)
        other_expenses = st.number_input("其他支出", min_value=0.0, step=10000.0)
    
    with col2:
        profit_before_tax = revenue - cogs - operating_expenses + other_income - other_expenses
        
        tax_adjustments = st.number_input("纳税调整金额", value=0.0, step=10000.0)
        taxable_income = max(0, profit_before_tax + tax_adjustments)
        
        is_small = st.checkbox("小型微利企业", value=False)
        
        if is_small:
            if taxable_income <= 1000000:
                tax_rate = 0.025
                tax_desc = "2.5% (小型微利优惠)"
            elif taxable_income <= 3000000:
                tax_rate = 0.05
                tax_desc = "5% (小型微利优惠)"
            else:
                tax_rate = 0.25
                tax_desc = "25% (超出优惠范围)"
        else:
            tax_rate = 0.25
            tax_desc = "25% (标准税率)"
        
        income_tax = taxable_income * tax_rate
        
        st.metric("利润总额", format_currency(profit_before_tax))
        st.metric("应纳税所得额", format_currency(taxable_income))
        st.metric(f"应纳所得税 ({tax_desc})", format_currency(income_tax))

with tab3:
    st.subheader("个人所得税计算")
    
    monthly_salary = st.number_input("月工资", min_value=0.0, step=1000.0)
    social_security = st.number_input("社保公积金个人部分", min_value=0.0, step=100.0)
    special_deduction = st.number_input("专项附加扣除", min_value=0.0, step=100.0)
    other_deduction = st.number_input("其他扣除", min_value=0.0, step=100.0)
    
    threshold = 5000
    
    taxable_income = monthly_salary - social_security - threshold - special_deduction - other_deduction
    
    if taxable_income <= 0:
        tax = 0
        tax_rate_display = "0%"
    elif taxable_income <= 3000:
        tax = taxable_income * 0.03
        tax_rate_display = "3%"
    elif taxable_income <= 12000:
        tax = taxable_income * 0.1 - 210
        tax_rate_display = "10%"
    elif taxable_income <= 25000:
        tax = taxable_income * 0.2 - 1410
        tax_rate_display = "20%"
    elif taxable_income <= 35000:
        tax = taxable_income * 0.25 - 2660
        tax_rate_display = "25%"
    elif taxable_income <= 55000:
        tax = taxable_income * 0.3 - 4410
        tax_rate_display = "30%"
    elif taxable_income <= 80000:
        tax = taxable_income * 0.35 - 7160
        tax_rate_display = "35%"
    else:
        tax = taxable_income * 0.45 - 15160
        tax_rate_display = "45%"
    
    col1, col2, col3 = st.columns(3)
    col1.metric("应纳税所得额", format_currency(max(0, taxable_income)))
    col2.metric("适用税率", tax_rate_display)
    col3.metric("应纳个税", format_currency(tax))
    
    net_salary = monthly_salary - social_security - tax
    st.metric("税后工资", format_currency(net_salary))
