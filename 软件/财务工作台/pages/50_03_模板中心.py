"""
FinCopilot - 模板中心
提供 16 种比赛常用表格模板
"""
import streamlit as st
import pandas as pd

# init_page disabled

# init_page disabled

st.title("📋 模板中心")

st.markdown("""
**说明**：下载标准 Excel 模板，导入后可自动识别字段
""")

# 模板分类
TAB_BANK, TAB_FINANCE, TAB_REPORT = st.tabs(["🏦 银行单据", "💰 财务分析", "📊 报表模板"])

with TAB_BANK:
    st.subheader("🏦 银行单据模板")
    
    # 银行回单模板
    if st.button("下载：银行回单模板"):
        df = pd.DataFrame({
            '日期': ['2024-01-15'],
            '金额': [10000.00],
            '对方户名': ['示例公司'],
            '对方账号': ['6222 **** **** 1234'],
            '摘要': ['货款'],
            '凭证号': ['20240115001']
        })
        csv = df.to_csv(index=False, encoding='utf-8-sig')
        st.download_button(
            label="📥 银行回单模板.csv",
            data=csv,
            file_name="银行回单模板.csv",
            mime='text/csv'
        )
    
    # 发票模板
    if st.button("下载：发票记录模板"):
        df = pd.DataFrame({
            '发票代码': ['1100171130'],
            '发票号码': ['12345678'],
            '开票日期': ['2024-01-15'],
            '购买方': ['示例公司'],
            '销售方': ['供应商公司'],
            '金额': [1000.00],
            '税额': [60.00]
        })
        csv = df.to_csv(index=False, encoding='utf-8-sig')
        st.download_button(
            label="📥 发票记录模板.csv",
            data=csv,
            file_name="发票记录模板.csv",
            mime='text/csv'
        )

with TAB_FINANCE:
    st.subheader("💰 财务分析模板")
    
    # 资产负债表模板
    if st.button("下载：资产负债表模板"):
        df = pd.DataFrame({
            '项目': ['货币资金', '应收账款', '存货', '固定资产', '资产总计'],
            '期末余额': [100000, 50000, 80000, 200000, 430000],
            '期初余额': [90000, 45000, 75000, 180000, 390000]
        })
        csv = df.to_csv(index=False, encoding='utf-8-sig')
        st.download_button(
            label="📥 资产负债表模板.csv",
            data=csv,
            file_name="资产负债表模板.csv",
            mime='text/csv'
        )
    
    # 利润表模板
    if st.button("下载：利润表模板"):
        df = pd.DataFrame({
            '项目': ['营业收入', '营业成本', '税金及附加', '销售费用', '管理费用', '财务费用', '净利润'],
            '本期金额': [500000, 300000, 5000, 20000, 30000, 10000, 135000],
            '上期金额': [450000, 280000, 4500, 18000, 28000, 12000, 107500]
        })
        csv = df.to_csv(index=False, encoding='utf-8-sig')
        st.download_button(
            label="📥 利润表模板.csv",
            data=csv,
            file_name="利润表模板.csv",
            mime='text/csv'
        )
    
    # 现金流量表模板
    if st.button("下载：现金流量表模板"):
        df = pd.DataFrame({
            '项目': ['销售商品提供劳务收到的现金', '购买商品接受劳务支付的现金', '支付给职工的现金', '支付的各项税费'],
            '本期金额': [550000, 280000, 50000, 30000],
            '上期金额': [480000, 250000, 45000, 25000]
        })
        csv = df.to_csv(index=False, encoding='utf-8-sig')
        st.download_button(
            label="📥 现金流量表模板.csv",
            data=csv,
            file_name="现金流量表模板.csv",
            mime='text/csv'
        )

with TAB_REPORT:
    st.subheader("📊 报表模板")
    
    # 费用报销单模板
    if st.button("下载：费用报销单模板"):
        df = pd.DataFrame({
            '日期': ['2024-01-15', '2024-01-16', '2024-01-17'],
            '费用类型': ['差旅费', '招待费', '办公费'],
            '金额': [1000.00, 500.00, 200.00],
            '摘要': ['北京出差', '客户招待', '办公用品'],
            '发票张数': [3, 2, 1]
        })
        csv = df.to_csv(index=False, encoding='utf-8-sig')
        st.download_button(
            label="📥 费用报销单模板.csv",
            data=csv,
            file_name="费用报销单模板.csv",
            mime='text/csv'
        )
    
    # 供应商对比模板
    if st.button("下载：供应商对比模板"):
        df = pd.DataFrame({
            '供应商名称': ['供应商 A', '供应商 B', '供应商 C'],
            '单价': [100, 95, 105],
            '质量评分': [90, 85, 95],
            '交货周期 (天)': [7, 5, 10],
            '综合评分': [0, 0, 0]
        })
        csv = df.to_csv(index=False, encoding='utf-8-sig')
        st.download_button(
            label="📥 供应商对比模板.csv",
            data=csv,
            file_name="供应商对比模板.csv",
            mime='text/csv'
        )

st.markdown("---")

st.info("""
💡 **模板说明**

**银行单据类**：
- 银行回单模板
- 发票记录模板

**财务分析类**：
- 资产负债表模板
- 利润表模板
- 现金流量表模板

**报表类**：
- 费用报销单模板
- 供应商对比模板

**使用步骤**：
1. 下载对应模板
2. 按格式填写数据
3. 导入到对应功能页面
""")
