"""
FinCopilot - 快捷工具箱
快速计算、批量对比、比赛计时器
"""
import streamlit as st
from datetime import datetime, timedelta

from utils.page_helper import init_page

init_page("快捷工具箱", "🧰")

st.title("🧰 快捷工具箱")

# 工具选择
tool = st.selectbox(
    "选择工具",
    ["🧮 快速计算器", "📊 批量对比", "⏱️ 计时器", "📝 快速备忘录"]
)

# 快速计算器
if tool == "🧮 快速计算器":
    st.subheader("🧮 快速计算器")
    
    calc_type = st.selectbox(
        "计算类型",
        ["加减乘除", "百分比计算", "税额计算", "小写转大写金额"]
    )
    
    if calc_type == "加减乘除":
        col1, col2, col3 = st.columns(3)
        with col1:
            num1 = st.number_input("数字 1", value=0.0)
            op = st.selectbox("运算符", ["+", "-", "×", "÷"])
        with col2:
            num2 = st.number_input("数字 2", value=0.0)
        with col3:
            if st.button("=", type="primary"):
                if op == "+":
                    result = num1 + num2
                elif op == "-":
                    result = num1 - num2
                elif op == "×":
                    result = num1 * num2
                elif op == "÷":
                    result = num1 / num2 if num2 != 0 else "错误：除数为 0"
                st.metric("结果", result)
    
    elif calc_type == "百分比计算":
        col1, col2 = st.columns(2)
        with col1:
            base = st.number_input("基数", value=100.0)
            percent = st.number_input("百分比 (%)", value=10.0)
        with col2:
            if st.button("计算百分比"):
                result = base * (percent / 100)
                st.metric("结果", result)
    
    elif calc_type == "税额计算":
        col1, col2 = st.columns(2)
        with col1:
            amount = st.number_input("金额", value=1000.0)
            tax_rate = st.selectbox("税率", [0.03, 0.06, 0.09, 0.13, 0.17])
        with col2:
            if st.button("计算税额"):
                tax = amount * tax_rate
                total = amount + tax
                st.metric("税额", f"¥{tax:,.2f}")
                st.metric("含税总额", f"¥{total:,.2f}")
    
    elif calc_type == "小写转大写金额":
        amount = st.number_input("小写金额", value=12345.67)
        
        def num_to_cn_upper(num):
            """数字转中文大写"""
            cn_upper_map = {'0': '零', '1': '壹', '2': '贰', '3': '叁', '4': '肆',
                           '5': '伍', '6': '陆', '7': '柒', '8': '捌', '9': '玖'}
            unit = '分角元拾佰仟万拾佰仟亿拾佰仟'
            
            num_str = f"{num:.2f}"
            result = ""
            unit_index = 0
            
            for digit in num_str.replace('.', '').replace('-', ''):
                if digit in cn_upper_map:
                    result += cn_upper_map[digit] + unit[unit_index]
                    unit_index += 1
            
            return result + "整"
        
        if st.button("转换"):
            cn_amount = num_to_cn_upper(amount)
            st.text_area("大写金额", value=cn_amount, height=100)

# 批量对比
elif tool == "📊 批量对比":
    st.subheader("📊 批量对比")
    st.info("输入多组数据进行对比")
    
    data_input = st.text_area(
        "输入数据（每行一组，逗号分隔）",
        placeholder="例如：\n2024 年，1000,200,50\n2025 年，1200,250,60\n2026 年，1500,300,75"
    )
    
    if data_input:
        lines = data_input.strip().split('\n')
        data = [line.split(',') for line in lines]
        
        import pandas as pd
        df = pd.DataFrame(data)
        st.dataframe(df, use_container_width=True)
        
        # 导出
        csv = df.to_csv(index=False, encoding='utf-8-sig')
        st.download_button(
            label="📥 导出为 CSV",
            data=csv,
            file_name="批量对比数据.csv",
            mime='text/csv'
        )

# 计时器
elif tool == "⏱️ 计时器":
    st.subheader("⏱️ 计时器")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        hours = st.number_input("小时", min_value=0, max_value=23, value=0)
    with col2:
        minutes = st.number_input("分钟", min_value=0, max_value=59, value=5)
    with col3:
        seconds = st.number_input("秒", min_value=0, max_value=59, value=0)
    
    total_seconds = hours * 3600 + minutes * 60 + seconds
    
    if st.button("▶️ 开始倒计时"):
        if total_seconds > 0:
            progress_bar = st.progress(0)
            timer_text = st.empty()
            
            remaining = total_seconds
            while remaining > 0:
                mins, secs = divmod(remaining, 60)
                hrs, mins = divmod(mins, 60)
                timer_text.text(f"剩余时间：{hrs:02d}:{mins:02d}:{secs:02d}")
                progress_bar.progress(1 - remaining / total_seconds)
                
                import time
                time.sleep(1)
                remaining -= 1
            
            timer_text.text("⏰ 时间到！")
            st.balloons()

# 快速备忘录
elif tool == "📝 快速备忘录":
    st.subheader("📝 快速备忘录")
    
    notes = st.text_area(
        "输入备忘内容",
        height=300,
        placeholder="在此记录重要事项..."
    )
    
    if notes:
        st.download_button(
            label="💾 保存为文本文件",
            data=notes,
            file_name=f"备忘录_{datetime.now().strftime('%Y%m%d_%H%M')}.txt",
            mime='text/plain'
        )

st.markdown("---")

st.info("""
💡 **工具箱功能**

- **快速计算器**：基础运算、百分比、税额、大写金额
- **批量对比**：多组数据快速对比
- **计时器**：倒计时功能
- **快速备忘录**：临时记录
""")
