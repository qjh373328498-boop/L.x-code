"""
FinCopilot - 文档解析页面
"""
import streamlit as st
import os
import tempfile
from core.extractor import extract_from_pdf, extract_from_image

from utils.page_helper import init_page

init_page("文档解析", "📄")

st.title("📄 文档解析")

st.markdown("""
**功能说明**：上传 PDF 或图片格式的合同/发票/回单，系统自动提取以下信息：
- 💰 金额
- 🏢 公司名
- 📅 日期
- 🧾 发票代码/号码
""")

uploaded_file = st.file_uploader(
    "上传 PDF 或图片文件",
    type=["pdf", "png", "jpg", "jpeg"],
    help="支持 PDF、PNG、JPG 格式"
)

if uploaded_file:
    st.success(f"已上传：{uploaded_file.name}")
    
    # 保存到临时文件
    with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as tmp:
        tmp.write(uploaded_file.getvalue())
        tmp_path = tmp.name
    
    try:
        # 解析文档
        with st.spinner("正在解析文档..."):
            result = extract_from_pdf(tmp_path)
        
        if result:
            st.markdown("### ✅ 提取结果")
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.metric("💰 金额", f"¥{result.get('amount', 0):,.2f}")
                st.metric("🏢 公司名", result.get('company', '未提取'))
            
            with col2:
                st.metric("📅 日期", result.get('date', '未提取'))
                st.metric("🧾 发票代码", result.get('invoice_code', '未提取'))
            
            # 显示原始文本
            with st.expander("📃 查看原始文本"):
                st.text(result.get('text', '')[:5000])
        else:
            st.warning("未能提取到有效信息")
    
    finally:
        # 清理临时文件
        os.unlink(tmp_path)

st.markdown("---")

st.info("""
💡 **使用提示**

1. 上传清晰的 PDF 或图片文件
2. 系统会自动识别并提取关键信息
3. 如果提取失败，请检查文件清晰度
""")
