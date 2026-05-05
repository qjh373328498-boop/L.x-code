"""
FinCopilot - 合规风控页面
"""
import streamlit as st
from core.compliance import check_reimbursement, validate_invoice
from core.desensitizer import desensitize_phone, desensitize_id_card, desensitize_text

# init_page disabled

# init_page disabled

st.title("🛡️ 合规风控")

# 选项卡
tab1, tab2 = st.tabs(["报销预审", "数据脱敏"])

# 报销预审
with tab1:
    st.markdown("### 报销预审检查")
    
    st.info("输入报销单信息，系统自动检查是否超标、连号等风险")
    
    col1, col2 = st.columns(2)
    
    with col1:
        expense_type = st.selectbox(
            "费用类型",
            ["差旅", "招待", "办公", "交通", "其他"]
        )
        amount = st.number_input("金额", min_value=0.0, value=1000.0)
    
    with col2:
        date = st.date_input("日期")
        receipt_count = st.number_input("发票数量", min_value=1, step=1, value=1)
    
    invoice_numbers = []
    for i in range(receipt_count):
        num = st.text_input(f"发票号码 {i+1}", key=f"inv_{i}")
        if num:
            invoice_numbers.append(num)
    
    if st.button("检查"):
        expense = {
            'type': expense_type,
            'amount': amount,
            'date': str(date),
            'receipts': [{'invoice_number': num} for num in invoice_numbers]
        }
        
        issues = check_reimbursement(expense)
        
        if issues:
            st.warning(f"发现 {len(issues)} 个问题")
            for issue in issues:
                st.markdown(f"- **{issue['type']}**: {issue['message']}")
        else:
            st.success("✅ 未发现明显问题")

# 数据脱敏
with tab2:
    st.markdown("### 数据脱敏")
    
    st.info("输入文本或数据，系统自动脱敏敏感信息")
    
    text = st.text_area(
        "输入文本",
        height=200,
        placeholder="请输入包含手机号、身份证、银行卡号等的文本"
    )
    
    if st.button("脱敏处理"):
        if text:
            # 脱敏处理
            desensitized = desensitize_text(text)
            
            st.markdown("### ✅ 脱敏结果")
            st.text_area("脱敏后文本", value=desensitized, height=200)
        else:
            st.warning("请输入文本")
    
    # 示例
    with st.expander("📋 查看示例"):
        st.code("""
原始文本:
张三，手机号：13812345678
身份证：110101199001011234
银行卡：6222020800001234567

脱敏后:
张三，手机号：138****5678
身份证：110101********1234
银行卡：6222 **** **** 4567
        """)

st.markdown("---")

st.info("""
💡 **使用提示**

**报销预审**
- 自动检查金额超标
- 自动检测连号发票
- 提供风险提示

**数据脱敏**
- 手机号中间 4 位掩码
- 身份证号中间 8 位掩码
- 银行卡号中间掩码
""")
