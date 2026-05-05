"""
FinCopilot - 金融测算页面
"""
import streamlit as st
from core.calculator import (
    straight_line_depreciation,
    double_declining_balance,
    calculate_irr,
    calculate_npv,
    calculate_pmt
)

st.set_page_config(page_title="金融测算", page_icon="🧮", layout="wide")

st.title("🧮 金融测算")

calc_type = st.selectbox(
    "选择计算类型",
    [
        "直线折旧",
        "双倍余额递减法",
        "IRR 计算",
        "NPV 计算",
        "年金计算"
    ]
)

# 直线折旧
if calc_type == "直线折旧":
    st.markdown("### 直线折旧计算")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        cost = st.number_input("原值", min_value=0.0, value=10000.0)
    with col2:
        salvage = st.number_input("残值", min_value=0.0, value=1000.0)
    with col3:
        life = st.number_input("使用年限", min_value=1, step=1, value=5)
    
    if st.button("计算"):
        result = straight_line_depreciation(cost, salvage, life)
        
        st.metric("年折旧额", f"¥{result['annual_depreciation']:,.2f}")
        st.metric("总折旧额", f"¥{result['total_depreciation']:,.2f}")
        
        # 显示折旧计划
        st.markdown("### 📊 折旧计划表")
        import pandas as pd
        df = pd.DataFrame(result['schedule'])
        df['depreciation'] = df['depreciation'].apply(lambda x: f"¥{x:,.2f}")
        df['book_value'] = df['book_value'].apply(lambda x: f"¥{x:,.2f}")
        st.dataframe(df, use_container_width=True)

# 双倍余额递减法
elif calc_type == "双倍余额递减法":
    st.markdown("### 双倍余额递减法")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        cost = st.number_input("原值", min_value=0.0, value=10000.0)
    with col2:
        salvage = st.number_input("残值", min_value=0.0, value=1000.0)
    with col3:
        life = st.number_input("使用年限", min_value=1, step=1, value=5)
    
    if st.button("计算"):
        result = double_declining_balance(cost, salvage, life)
        
        st.info(f"折旧率：{result['rate']*100:.1f}%")
        
        # 显示折旧计划
        st.markdown("### 📊 折旧计划表")
        import pandas as pd
        df = pd.DataFrame(result['schedule'])
        df['depreciation'] = df['depreciation'].apply(lambda x: f"¥{x:,.2f}")
        df['book_value'] = df['book_value'].apply(lambda x: f"¥{x:,.2f}")
        st.dataframe(df, use_container_width=True)

# IRR 计算
elif calc_type == "IRR 计算":
    st.markdown("### 内部收益率 (IRR)")
    
    st.info("输入现金流列表，第一个为初始投资（负值）")
    
    cash_flows_str = st.text_input(
        "现金流（用逗号分隔）",
        value="-10000, 3000, 4000, 5000, 6000"
    )
    
    if st.button("计算"):
        try:
            cash_flows = [float(x.strip()) for x in cash_flows_str.split(',')]
            irr = calculate_irr(cash_flows)
            
            st.metric("IRR", f"{irr*100:.2f}%")
            
            # 显示现金流
            st.markdown("### 📊 现金流")
            import pandas as pd
            df = pd.DataFrame({
                '期数': range(len(cash_flows)),
                '现金流': [f"¥{x:,.2f}" for x in cash_flows]
            })
            st.dataframe(df, use_container_width=True)
        except Exception as e:
            st.error(f"计算失败：{e}")

# NPV 计算
elif calc_type == "NPV 计算":
    st.markdown("### 净现值 (NPV)")
    
    col1, col2 = st.columns(2)
    
    with col1:
        rate = st.number_input("折现率 (%)", min_value=0.0, value=10.0)
    with col2:
        cash_flows_str = st.text_input(
            "现金流（用逗号分隔）",
            value="-10000, 3000, 4000, 5000, 6000"
        )
    
    if st.button("计算"):
        try:
            cash_flows = [float(x.strip()) for x in cash_flows_str.split(',')]
            npv = calculate_npv(cash_flows, rate/100)
            
            st.metric("NPV", f"¥{npv:,.2f}")
        except Exception as e:
            st.error(f"计算失败：{e}")

# 年金计算
elif calc_type == "年金计算":
    st.markdown("### 年金计算 (PMT)")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        rate = st.number_input("年利率 (%)", min_value=0.0, value=5.0)
    with col2:
        nper = st.number_input("期数", min_value=1, step=1, value=10)
    with col3:
        pv = st.number_input("现值", min_value=0.0, value=100000.0)
    
    if st.button("计算"):
        pmt = calculate_pmt(rate/100, nper, pv)
        
        st.metric("每期支付额", f"¥{abs(pmt):,.2f}")

st.markdown("---")

st.info("""
💡 **使用提示**

- 所有计算均在本地完成
- 基于 numpy-financial 库
- 与财务工具箱算法保持一致
""")
