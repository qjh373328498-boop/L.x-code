"""
FinCopilot - 关联匹配页面
"""
import streamlit as st
import pandas as pd
import tempfile
import os
from core.matcher import smart_match

st.set_page_config(page_title="关联匹配", page_icon="🔗", layout="wide")

st.title("🔗 关联匹配")

st.markdown("""
**功能说明**：上传银行回单和发票 Excel 文件，系统自动匹配勾稽
""")

col1, col2 = st.columns(2)

with col1:
    receipt_file = st.file_uploader(
        "上传银行回单",
        type=["xlsx", "xls", "csv"],
        help="包含银行回单的 Excel 或 CSV 文件"
    )

with col2:
    invoice_file = st.file_uploader(
        "上传发票记录",
        type=["xlsx", "xls", "csv"],
        help="包含发票信息的 Excel 或 CSV 文件"
    )

if receipt_file and invoice_file:
    try:
        # 读取文件
        if receipt_file.name.endswith('.csv'):
            receipts_df = pd.read_csv(receipt_file)
        else:
            receipts_df = pd.read_excel(receipt_file)
        
        if invoice_file.name.endswith('.csv'):
            invoices_df = pd.read_csv(invoice_file)
        else:
            invoices_df = pd.read_excel(invoice_file)
        
        st.success(f"已加载：银行回单 {len(receipts_df)} 条，发票 {len(invoices_df)} 条")
        
        # 选择匹配字段
        st.markdown("### 字段映射")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("**银行回单字段**")
            receipt_amount_col = st.selectbox(
                "金额列",
                receipts_df.columns.tolist(),
                key="receipt_amount"
            )
            receipt_date_col = st.selectbox(
                "日期列",
                receipts_df.columns.tolist(),
                key="receipt_date"
            )
            receipt_desc_col = st.selectbox(
                "摘要列",
                receipts_df.columns.tolist(),
                key="receipt_desc",
                index=min(2, len(receipts_df.columns)-1)
            )
        
        with col2:
            st.markdown("**发票字段**")
            invoice_amount_col = st.selectbox(
                "金额列",
                invoices_df.columns.tolist(),
                key="invoice_amount"
            )
            invoice_date_col = st.selectbox(
                "日期列",
                invoices_df.columns.tolist(),
                key="invoice_date"
            )
        
        if st.button("开始匹配", type="primary"):
            with st.spinner("正在智能匹配..."):
                # 重命名列以便匹配
                receipts_df_renamed = receipts_df.rename(columns={
                    receipt_amount_col: 'amount',
                    receipt_date_col: 'date',
                    receipt_desc_col: 'description'
                })
                
                invoices_df_renamed = invoices_df.rename(columns={
                    invoice_amount_col: 'amount',
                    invoice_date_col: 'date'
                })
                
                # 执行匹配
                result = smart_match(receipts_df_renamed, invoices_df_renamed)
                
                # 显示结果
                st.markdown("### ✅ 匹配结果")
                
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    st.metric("匹配成功", f"{len(result['matched'])} 条")
                with col2:
                    st.metric("未匹配回单", f"{result['unmatched_receipts_count']} 条")
                with col3:
                    st.metric("匹配率", f"{result['match_rate']*100:.1f}%")
                
                # 显示匹配详情
                with st.expander("📊 查看匹配详情"):
                    if not result['matched'].empty:
                        st.dataframe(result['matched'], use_container_width=True)
                    else:
                        st.info("无匹配记录")
                
                # 显示未匹配项
                with st.expander("⚠️ 查看未匹配项"):
                    st.warning(f"未匹配回单：{result['unmatched_receipts_count']} 条")
                    st.warning(f"未匹配发票：{result['unmatched_invoices_count']} 条")
    
    except Exception as e:
        st.error(f"处理失败：{e}")
        import traceback
        traceback.print_exc()

st.markdown("---")

st.info("""
💡 **使用提示**

1. 上传银行回单和发票的 Excel/CSV 文件
2. 正确映射金额、日期、摘要字段
3. 系统会自动匹配并标红未匹配项
4. 支持导出匹配结果
""")
