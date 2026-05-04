"""
📁 财报上传 - 页面 02
"""
import streamlit as st
import os

st.set_page_config(page_title="财报上传", page_icon="📁", layout="wide")

st.title("📁 财报上传与解析")

if hasattr(st.session_state, "uploaded_file") and st.session_state.uploaded_file:
    st.success(f"✅ 已加载：{st.session_state.uploaded_file.name}")
    if st.button("🗑️ 重新上传"):
        st.session_state.uploaded_file = None
        st.session_state.financial_data = None
        st.session_state.company_info = {}
        st.session_state.industry = None
        st.rerun()
    st.markdown("---")
else:
    from utils.parser import parse_financial_report
    from utils.industry import detect_industry
    
    uploaded_file = st.file_uploader(
        "上传财报文件",
        type=["xlsx", "xls", "pdf"],
        help="支持 Excel 和 PDF 格式",
    )
    
    company_name = st.text_input(
        "公司名称（可选）", 
        placeholder="用于自动识别行业",
        help="输入公司名称可以帮助系统自动识别所属行业"
    )
    
    business_desc = st.text_area(
        "业务范围描述（可选）",
        placeholder="简要描述公司主营业务，有助于更准确地识别行业",
        help="例如：从事软件开发和互联网服务"
    )
    
    if uploaded_file and st.button("开始解析", type="primary"):
        with st.spinner("正在解析财报，请稍候..."):
            try:
                # 保存到临时文件
                import tempfile
                temp_dir = tempfile.gettempdir()
                filepath = os.path.join(temp_dir, uploaded_file.name)
                with open(filepath, "wb") as f:
                    f.write(uploaded_file.getbuffer())
                
                # 解析财报
                data = parse_financial_report(filepath)
                
                # 计算置信度
                bs = data.get('balance_sheet', {})
                ic = data.get('income_stmt', {})
                cf = data.get('cash_flow', {})
                
                assets = bs.get('总资产', 0) or bs.get('资产总计', 0)
                liabilities = bs.get('负债合计', 0) or bs.get('总负债', 0)
                equity = bs.get('股东权益', 0) or bs.get('所有者权益', 0)
                
                diff = abs(assets - liabilities - equity) / max(assets, 1) * 100 if assets > 0 else 100
                
                # 置信度评分
                score = 0
                score += min(4, len(bs) / 10 * 4)  # 资产负债表 4 分
                score += min(3, len(ic) / 5 * 3)    # 利润表 3 分
                score += min(2, len(cf) / 3 * 2)    # 现金流 2 分
                score += 1 if diff < 1 else 0       # 会计等式 1 分
                
                confidence = score * 10
                
                st.session_state.uploaded_file = uploaded_file
                st.session_state.financial_data = data
                st.session_state.parse_confidence = confidence
                st.session_state.parse_diff = diff
                st.session_state.company_info["name"] = company_name
                
                # 显示置信度评估
                if confidence >= 90:
                    st.success(f"✅ 解析置信度：**{confidence:.1f}%** (会计等式差异 {diff:.2f}%)")
                elif confidence >= 70:
                    st.warning(f"⚠️ 解析置信度：**{confidence:.1f}%** (会计等式差异 {diff:.2f}%)")
                else:
                    st.error(f"❌ 解析置信度：**{confidence:.1f}%** (会计等式差异 {diff:.2f}%)")
                
                # 显示提取的字段统计
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("资产负债表", f"{len(bs)} 个字段")
                with col2:
                    st.metric("利润表", f"{len(ic)} 个字段")
                with col3:
                    st.metric("现金流量表", f"{len(cf)} 个字段")
                
                # 行业识别
                if company_name or business_desc:
                    st.session_state.industry = detect_industry(
                        company_name or "", 
                        business_desc or ""
                    )
                
                st.success("✅ 解析成功！")
                st.info("📊 已跳转到数据预览")
                st.rerun()
                
            except Exception as e:
                st.error(f"❌ 解析失败：{str(e)}")
                st.markdown("""
                **可能的原因**：
                - 文件格式不支持
                - 财报格式不标准
                - 文件损坏
                
                **建议**：
                - 确保上传的是标准财务报表
                - Excel 文件应包含：资产负债表、利润表、现金流量表
                - 如持续失败，请联系技术支持
                """)
    
    # 使用说明
    st.markdown("---")
    st.markdown("""
    ### 📖 使用说明
    
    **支持格式**：
    - ✅ Excel (.xlsx, .xls) - 推荐
    - ✅ PDF (.pdf)
    
    **Excel 格式要求**：
    -  Sheet 名称包含："资产"、"利润"、"现金流"等关键词
    -  或：Sheet 名称为 "balance"、"income"、"cash"
    
    **数据格式**：
    -  第一列：项目名称（如"货币资金"、"营业收入"）
    -  第二列：本期金额
    -  第三列：上期金额（可选）
    
    **行业标准值**：
    系统内置 8 大行业的财务指标标准值，上传后自动对标分析。
    """)

# 数据预览
if st.session_state.financial_data:
    st.markdown("### 📊 数据预览")
    
    data = st.session_state.financial_data
    
    balance_sheet = data.get("balance_sheet", {})
    income_stmt = data.get("income_stmt", {})
    cash_flow = data.get("cash_flow", {})
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("**资产负债表**")
        if balance_sheet:
            for k, v in balance_sheet.items():
                st.text(f"{k}: {v:,.0f}")
        else:
            st.warning("未解析到数据")
    
    with col2:
        st.markdown("**利润表**")
        if income_stmt:
            for k, v in income_stmt.items():
                st.text(f"{k}: {v:,.0f}")
        else:
            st.warning("未解析到数据")
    
    with col3:
        st.markdown("**现金流量表**")
        if cash_flow:
            for k, v in cash_flow.items():
                st.text(f"{k}: {v:,.0f}")
        else:
            st.warning("未解析到数据")
