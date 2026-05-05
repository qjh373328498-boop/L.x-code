"""
FinCopilot - 批量文档解析页面
支持一次上传多个 PDF/图片批量提取
"""
import streamlit as st
import os
import tempfile
import pandas as pd
from core.extractor import extract_from_pdf, extract_from_image

from utils.page_helper import init_page

from utils.page_helper import init_page

st.title("📄 批量文档解析")

st.markdown("""
**功能说明**：一次上传多个 PDF 或图片文件，系统批量提取关键信息并导出汇总表格
""")

# 批量上传
uploaded_files = st.file_uploader(
    "上传多个 PDF 或图片文件",
    type=["pdf", "png", "jpg", "jpeg"],
    accept_multiple_files=True,
    help="支持 PDF、PNG、JPG 格式，可一次上传多个文件"
)

if uploaded_files:
    st.success(f"已选择 {len(uploaded_files)} 个文件")
    
    # 显示文件列表
    st.markdown("### 📋 文件列表")
    file_info = []
    for i, f in enumerate(uploaded_files):
        size_kb = f.size / 1024
        file_info.append({
            "序号": i + 1,
            "文件名": f.name,
            "大小": f"{size_kb:.1f} KB",
            "状态": "待解析"
        })
    
    files_df = pd.DataFrame(file_info)
    st.dataframe(files_df, use_container_width=True, hide_index=True)
    
    # 开始解析
    if st.button("🚀 开始批量解析", type="primary"):
        progress_bar = st.progress(0)
        results = []
        
        for i, uploaded_file in enumerate(uploaded_files):
            try:
                # 更新状态
                files_df.loc[i, "状态"] = "解析中..."
                st.write(f"正在解析：{uploaded_file.name}")
                
                # 保存到临时文件
                file_type = uploaded_file.name.split('.')[-1].lower()
                with tempfile.NamedTemporaryFile(delete=False, suffix=f'.{file_type}') as tmp:
                    tmp.write(uploaded_file.getvalue())
                    tmp_path = tmp.name
                
                # 解析文档
                if file_type == 'pdf':
                    result = extract_from_pdf(tmp_path)
                else:
                    result = extract_from_image(tmp_path)
                
                # 清理临时文件
                os.unlink(tmp_path)
                
                # 添加结果
                result_row = {
                    "文件名": uploaded_file.name,
                    "金额": result.get('amount', 0),
                    "公司名": result.get('company', '-'),
                    "日期": result.get('date', '-'),
                    "发票代码": result.get('invoice_code', '-'),
                    "发票号码": result.get('invoice_number', '-'),
                    "状态": "✅ 成功"
                }
                results.append(result_row)
                
                # 更新进度
                progress_bar.progress((i + 1) / len(uploaded_files))
                
            except Exception as e:
                result_row = {
                    "文件名": uploaded_file.name,
                    "金额": 0,
                    "公司名": '-',
                    "日期": '-',
                    "发票代码": '-',
                    "发票号码": '-',
                    "状态": f"❌ 失败：{str(e)}"
                }
                results.append(result_row)
        
        # 显示结果
        if results:
            st.markdown("### ✅ 解析结果汇总")
            results_df = pd.DataFrame(results)
            
            # 金额格式化
            results_df['金额'] = results_df['金额'].apply(
                lambda x: f"¥{x:,.2f}" if isinstance(x, (int, float)) and x > 0 else '-'
            )
            
            st.dataframe(results_df, use_container_width=True, hide_index=True)
            
            # 统计信息
            st.markdown("### 📊 统计信息")
            col1, col2, col3 = st.columns(3)
            
            success_count = len([r for r in results if '✅' in r['状态']])
            total_amount = sum([r['金额'] for r in results if isinstance(r['金额'], (int, float))])
            
            with col1:
                st.metric("成功解析", f"{success_count}/{len(results)}")
            with col2:
                st.metric("失败数量", f"{len(results) - success_count}")
            with col3:
                st.metric("总金额", f"¥{total_amount:,.2f}")
            
            # 导出功能
            csv = results_df.to_csv(index=False, encoding='utf-8-sig')
            st.download_button(
                label="📥 导出为 CSV",
                data=csv,
                file_name="批量文档解析结果.csv",
                mime='text/csv'
            )

st.markdown("---")

st.info("""
💡 **使用提示**

1. 可一次选择多个文件（支持 Ctrl/Shift 多选）
2. 系统会自动识别文件类型并解析
3. 解析完成后显示汇总表格
4. 支持导出为 CSV 格式
5. 支持查看每个文件的详细解析结果
""")
