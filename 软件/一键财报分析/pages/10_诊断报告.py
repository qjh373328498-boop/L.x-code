"""
📋 诊断报告 - 页面 10
"""
import streamlit as st
import pandas as pd
from datetime import datetime

st.set_page_config(page_title="诊断报告", page_icon="📋", layout="wide")

st.title("📋 智能诊断报告")

if st.session_state.financial_data:
    from utils.ratios import (
        calculate_profitability_ratios, calculate_solvency_ratios,
        calculate_efficiency_ratios, calculate_cash_flow_ratios,
        calculate_duPont_analysis
    )
    from utils.industry import evaluate_ratio
    
    data = st.session_state.financial_data
    income_stmt = data.get("income_stmt", {})
    balance_sheet = data.get("balance_sheet", {})
    cash_flow = data.get("cash_flow", {})
    
    # 计算所有指标
    profit_ratios = calculate_profitability_ratios({**income_stmt, **balance_sheet})
    solvency_ratios = calculate_solvency_ratios(balance_sheet)
    efficiency_ratios = calculate_efficiency_ratios(income_stmt, balance_sheet)
    cashflow_ratios = calculate_cash_flow_ratios(cash_flow, income_stmt)
    
    all_ratios = {**profit_ratios, **solvency_ratios, **efficiency_ratios, **cashflow_ratios}
    duPont = calculate_duPont_analysis(all_ratios)
    
    # 综合评分计算
    def calculate_score(ratios):
        score = 0
        max_score = 100
        
        # 盈利能力 (30 分)
        if ratios.get('ROE', 0) > 15:
            score += 30
        elif ratios.get('ROE', 0) > 10:
            score += 20
        elif ratios.get('ROE', 0) > 5:
            score += 10
        
        # 偿债能力 (25 分)
        current_ratio = ratios.get('流动比率', 0)
        if 1.5 <= current_ratio <= 2.5:
            score += 15
        elif current_ratio > 1:
            score += 8
        
        debt_ratio = ratios.get('资产负债率', 0)
        if 30 <= debt_ratio <= 60:
            score += 10
        elif debt_ratio <= 70:
            score += 5
        
        # 运营效率 (20 分)
        if ratios.get('总资产周转率', 0) > 1:
            score += 20
        elif ratios.get('总资产周转率', 0) > 0.5:
            score += 10
        
        # 现金流 (25 分)
        profit_cash_ratio = ratios.get('盈利现金比率', 0)
        if profit_cash_ratio >= 1:
            score += 25
        elif profit_cash_ratio >= 0.8:
            score += 15
        elif profit_cash_ratio >= 0.5:
            score += 8
        
        return min(score, max_score)
    
    score = calculate_score(all_ratios)
    
    # 评级
    if score >= 80:
        rating = "优秀"
        color = "🟢"
        st.success(f"综合评分：{score}分 - {color}{rating}")
    elif score >= 60:
        rating = "良好"
        color = "🔵"
        st.info(f"综合评分：{score}分 - {color}{rating}")
    elif score >= 40:
        rating = "一般"
        color = "🟡"
        st.warning(f"综合评分：{score}分 - {color}{rating}")
    else:
        rating = "较差"
        color = "🔴"
        st.error(f"综合评分：{score}分 - {color}{rating}")
    
    st.markdown("---")
    
    # 报告内容
    st.subheader("📊 核心指标总览")
    
    cols = st.columns(5)
    metrics = [
        ("毛利率", profit_ratios.get('毛利率', 0), "%"),
        ("净利润率", profit_ratios.get('净利润率', 0), "%"),
        ("ROE", profit_ratios.get('ROE', 0), "%"),
        ("资产负债率", solvency_ratios.get('资产负债率', 0), "%"),
        ("总资产周转率", efficiency_ratios.get('总资产周转率', 0), "次"),
    ]
    
    for i, (name, value, unit) in enumerate(metrics):
        with cols[i]:
            st.metric(name, f"{value:.1f}{unit}")
    
    st.markdown("---")
    
    # 杜邦分析
    st.subheader("🔍 杜邦分析")
    
    col1, col2 = st.columns([2, 1])
    with col1:
        st.markdown(f"""
        **ROE = 净利率 × 总资产周转率 × 权益乘数**
        
        | 指标 | 数值 |
        |------|------|
        | 净利率 | {duPont['净利率']:.2f}% |
        | 总资产周转率 | {duPont['总资产周转率']:.2f}次 |
        | 权益乘数 | {duPont['权益乘数']:.2f} |
        | **ROE** | **{duPont['ROE']:.2f}%** |
        """)
    
    with col2:
        st.markdown(f"""
        **分析结论**:
        - 盈利驱动：{"高利润模式" if duPont['净利率'] > 15 else "薄利多销" if duPont['总资产周转率'] > 1 else "一般"}
        - 杠杆水平：{"高杠杆" if duPont['权益乘数'] > 2.5 else "稳健" if duPont['权益乘数'] < 2 else "适中"}
        """)
    
    st.markdown("---")
    
    # 优势与劣势
    st.subheader("📈 优势与劣势")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### ✅ 优势")
        strengths = []
        if profit_ratios.get('毛利率', 0) > 30:
            strengths.append("毛利率高于 30%，产品竞争力强")
        if profit_ratios.get('ROE', 0) > 15:
            strengths.append("ROE 高于 15%，股东回报优秀")
        if solvency_ratios.get('流动比率', 0) > 2:
            strengths.append("流动比率>2，短期偿债能力强")
        if efficiency_ratios.get('总资产周转率', 0) > 1:
            strengths.append("总资产周转率>1，资产利用效率高")
        if cashflow_ratios.get('盈利现金比率', 0) > 1:
            strengths.append("盈利现金比率>1，利润质量高")
        
        if strengths:
            for s in strengths:
                st.markdown(f"- {s}")
        else:
            st.markdown("- 暂无明显优势")
    
    with col2:
        st.markdown("### ⚠️ 需改进")
        weaknesses = []
        if profit_ratios.get('净利润率', 0) < 10:
            weaknesses.append("净利润率偏低，需提升盈利能力")
        if solvency_ratios.get('资产负债率', 0) > 70:
            weaknesses.append("资产负债率偏高，需优化资本结构")
        if efficiency_ratios.get('存货周转率', 0) < 5:
            weaknesses.append("存货周转慢，需加强库存管理")
        if cashflow_ratios.get('盈利现金比率', 0) < 0.8:
            weaknesses.append("盈利现金比率低，利润质量待提升")
        
        if weaknesses:
            for w in weaknesses:
                st.markdown(f"- {w}")
        else:
            st.markdown("- 整体表现良好")
    
    st.markdown("---")
    
    # 行业对比
    if st.session_state.industry:
        st.subheader(f"🏭 行业位置（{st.session_state.industry}）")
        
        from utils.industry import get_industry_standard
        
        indicators = ["毛利率", "净利润率", "ROE", "资产负债率"]
        position_data = []
        
        for ind in indicators:
            value = all_ratios.get(ind, 0)
            std = get_industry_standard(st.session_state.industry, ind)
            
            if value >= std["max"]:
                position = "前 20%"
            elif value >= std["avg"]:
                position = "前 50%"
            else:
                position = "后 50%"
            
            position_data.append({
                "指标": ind,
                "公司值": f"{value:.2f}",
                "行业平均": f"{std['avg']:.2f}",
                "行业位置": position,
            })
        
        st.dataframe(position_data, use_container_width=True, hide_index=True)
    
    st.markdown("---")
    
    # 导出报告
    st.subheader("📥 导出报告")
    
    report_text = f"""
# 财务诊断报告
生成时间：{datetime.now().strftime('%Y-%m-%d %H:%M')}
公司名称：{st.session_state.company_info.get('name', '未填写')}
所属行业：{st.session_state.industry or '未分类'}

## 综合评分
评分：{score}/100
评级：{rating}

## 核心指标
- 毛利率：{profit_ratios.get('毛利率', 0):.1f}%
- 净利润率：{profit_ratios.get('净利润率', 0):.1f}%
- ROE: {profit_ratios.get('ROE', 0):.1f}%
- 资产负债率：{solvency_ratios.get('资产负债率', 0):.1f}%
- 总资产周转率：{efficiency_ratios.get('总资产周转率', 0):.2f}次

## 杜邦分析
- 净利率：{duPont['净利率']:.2f}%
- 总资产周转率：{duPont['总资产周转率']:.2f}次
- 权益乘数：{duPont['权益乘数']:.2f}
- ROE: {duPont['ROE']:.2f}%
"""
    
    st.download_button(
        label="📥 下载文字报告",
        data=report_text,
        file_name=f"财务诊断报告_{datetime.now().strftime('%Y%m%d')}.md",
        mime="text/markdown"
    )

else:
    st.warning("⚠️ 请先在首页上传财报文件")
