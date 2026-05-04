"""
⚠️ 风险预警 - 页面 09
"""
import streamlit as st
import pandas as pd

st.set_page_config(page_title="风险预警", page_icon="⚠️", layout="wide")

st.title("⚠️ 风险预警")

if st.session_state.financial_data:
    from utils.ratios import calculate_profitability_ratios, calculate_solvency_ratios, calculate_efficiency_ratios, calculate_cash_flow_ratios
    
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
    
    # 风险检测
    warnings = []
    
    # 1. 现金流风险
    operating_cash = cash_flow.get('经营活动现金流净额', 0)
    net_profit = income_stmt.get('净利润', 0)
    
    if net_profit > 0 and operating_cash < 0:
        warnings.append({
            "风险类型": "🔴 高风险",
            "指标": "现金流",
            "问题": "净利润为正但经营现金流为负",
            "说明": "可能存在利润虚增或应收账款大量积压",
            "建议": "重点核查应收账款质量和收入确认政策"
        })
    
    # 2. 流动比率过低
    current_ratio = solvency_ratios.get('流动比率', 0)
    if current_ratio < 1:
        warnings.append({
            "风险类型": "🔴 高风险",
            "指标": "流动比率",
            "问题": f"流动比率仅 {current_ratio:.2f}",
            "说明": "短期偿债能力严重不足",
            "建议": "立即补充流动资金，优化债务结构"
        })
    elif current_ratio < 1.5:
        warnings.append({
            "风险类型": "🟡 中风险",
            "指标": "流动比率",
            "问题": f"流动比率 {current_ratio:.2f} 偏低",
            "说明": "短期偿债能力较弱",
            "建议": "关注现金流管理，适当增加流动性"
        })
    
    # 3. 资产负债率过高
    debt_ratio = solvency_ratios.get('资产负债率', 0)
    if debt_ratio > 80:
        warnings.append({
            "风险类型": "🔴 高风险",
            "指标": "资产负债率",
            "问题": f"资产负债率高达 {debt_ratio:.1f}%",
            "说明": "财务杠杆过高，偿债压力大",
            "建议": "控制负债规模，考虑股权融资"
        })
    elif debt_ratio > 70:
        warnings.append({
            "风险类型": "🟡 中风险",
            "指标": "资产负债率",
            "问题": f"资产负债率 {debt_ratio:.1f}% 偏高",
            "说明": "负债水平较高",
            "建议": "审慎举债，优化资本结构"
        })
    
    # 4. 存货周转率过低
    inventory_turnover = efficiency_ratios.get('存货周转率', 0)
    if inventory_turnover < 3:
        warnings.append({
            "风险类型": "🟡 中风险",
            "指标": "存货周转率",
            "问题": f"存货周转率仅 {inventory_turnover:.2f}次",
            "说明": "存货积压严重，资金占用高",
            "建议": "加强库存管理，促销去库存"
        })
    
    # 5. 应收账款周转率过低
    receivables_turnover = efficiency_ratios.get('应收账款周转率', 0)
    if receivables_turnover < 3:
        warnings.append({
            "风险类型": "🟡 中风险",
            "指标": "应收账款周转率",
            "问题": f"应收账款周转率仅 {receivables_turnover:.2f}次",
            "说明": "回款速度慢，资金占用高",
            "建议": "加强应收账款催收，严格信用政策"
        })
    
    # 6. 毛利率异常
    gross_margin = profit_ratios.get('毛利率', 0)
    net_margin = profit_ratios.get('净利润率', 0)
    if gross_margin > 50 and net_margin < 5:
        warnings.append({
            "风险类型": "🟡 中风险",
            "指标": "利润率结构",
            "问题": "毛利率高但净利润率很低",
            "说明": "期间费用过高侵蚀利润",
            "建议": "分析费用结构，控制销售/管理费用"
        })
    
    # 7. ROE 过低
    roe = profit_ratios.get('ROE', 0)
    if roe < 5 and roe >= 0:
        warnings.append({
            "风险类型": "🟢 低风险",
            "指标": "ROE",
            "问题": f"ROE 仅 {roe:.1f}%",
            "说明": "股东回报率偏低",
            "建议": "提升盈利能力或优化资产结构"
        })
    elif roe < 0:
        warnings.append({
            "风险类型": "🔴 高风险",
            "指标": "ROE",
            "问题": f"ROE 为负 ({roe:.1f}%)",
            "说明": "公司处于亏损状态",
            "建议": "深入分析亏损原因，制定扭亏方案"
        })
    
    # 显示预警
    if warnings:
        st.markdown(f"### 共发现 {len(warnings)} 项风险")
        
        # 按风险等级排序
        risk_order = {"🔴 高风险": 0, "🟡 中风险": 1, "🟢 低风险": 2}
        warnings.sort(key=lambda x: risk_order.get(x["风险类型"], 3))
        
        # 高风险
        high_risks = [w for w in warnings if "🔴" in w["风险类型"]]
        if high_risks:
            st.error(f"**高风险 ({len(high_risks)}项)**")
            for w in high_risks:
                with st.expander(f"{w['指标']}: {w['问题']}", expanded=True):
                    st.markdown(f"**说明**: {w['说明']}")
                    st.markdown(f"**建议**: {w['建议']}")
        
        # 中风险
        medium_risks = [w for w in warnings if "🟡" in w["风险类型"]]
        if medium_risks:
            st.warning(f"**中风险 ({len(medium_risks)}项)**")
            for w in medium_risks:
                with st.expander(f"{w['指标']}: {w['问题']}", expanded=False):
                    st.markdown(f"**说明**: {w['说明']}")
                    st.markdown(f"**建议**: {w['建议']}")
        
        # 低风险
        low_risks = [w for w in warnings if "🟢" in w["风险类型"]]
        if low_risks:
            st.info(f"**低风险 ({len(low_risks)}项)**")
            for w in low_risks:
                with st.expander(f"{w['指标']}: {w['问题']}", expanded=False):
                    st.markdown(f"**说明**: {w['说明']}")
                    st.markdown(f"**建议**: {w['建议']}")
    else:
        st.success("✅ 未发现明显财务风险！公司财务状况健康。")
    
    # 完整数据表格
    st.markdown("---")
    st.subheader("📊 完整指标数据")
    
    indicators_data = []
    for name, value in all_ratios.items():
        indicators_data.append({
            "指标": name,
            "数值": f"{value:.2f}" if value < 100 else f"{value:.1f}",
        })
    
    st.dataframe(indicators_data, use_container_width=True, hide_index=True)

else:
    st.warning("⚠️ 请先在首页上传财报文件")
