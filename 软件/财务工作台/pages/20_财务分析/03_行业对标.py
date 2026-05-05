"""
FinCopilot - 行业对标页面
复用《一键财报分析》industry.py 进行行业对比
"""
import streamlit as st
import plotly.graph_objects as go

st.set_page_config(page_title="行业对标", page_icon="🏭", layout="wide")

st.title("🏭 行业对标分析")

st.markdown("""
**功能说明**：选择所属行业，系统将企业财务指标与行业平均水平对比
""")

# 行业定义
INDUSTRY_STANDARDS = {
    "制造业": {
        "gross_margin": 25.0,  # 毛利率
        "net_margin": 8.0,     # 净利率
        "roe": 12.0,           # ROE
        "current_ratio": 1.8,  # 流动比率
        "debt_ratio": 55.0,    # 资产负债率
        "inventory_turnover": 6.0,  # 存货周转率
    },
    "科技/互联网": {
        "gross_margin": 45.0,
        "net_margin": 15.0,
        "roe": 18.0,
        "current_ratio": 2.5,
        "debt_ratio": 40.0,
        "inventory_turnover": 10.0,
    },
    "零售业": {
        "gross_margin": 30.0,
        "net_margin": 5.0,
        "roe": 15.0,
        "current_ratio": 1.5,
        "debt_ratio": 60.0,
        "inventory_turnover": 8.0,
    },
    "服务业": {
        "gross_margin": 35.0,
        "net_margin": 12.0,
        "roe": 20.0,
        "current_ratio": 2.0,
        "debt_ratio": 45.0,
        "inventory_turnover": 15.0,
    },
}

# 行业选择
selected_industry = st.selectbox(
    "选择行业",
    list(INDUSTRY_STANDARDS.keys())
)

st.info(f"📊 当前对比行业：**{selected_industry}**")

# 企业数据输入
st.subheader("🏢 企业财务数据")

col1, col2 = st.columns(2)

with col1:
    st.markdown("**盈利能力**")
    company_gross_margin = st.number_input("毛利率 (%)", min_value=0.0, value=30.0, step=0.1)
    company_net_margin = st.number_input("净利率 (%)", min_value=0.0, value=10.0, step=0.1)
    company_roe = st.number_input("ROE (%)", min_value=0.0, value=15.0, step=0.1)

with col2:
    st.markdown("**偿债能力**")
    company_current_ratio = st.number_input("流动比率", min_value=0.0, value=2.0, step=0.1)
    company_debt_ratio = st.number_input("资产负债率 (%)", min_value=0.0, value=50.0, step=0.1)

st.markdown("---")

# 对比分析
if st.button("开始对比分析", type="primary"):
    industry = INDUSTRY_STANDARDS[selected_industry]
    
    # 指标对比
    st.subheader("📊 指标对比")
    
    indicators = {
        '毛利率': (company_gross_margin, industry['gross_margin']),
        '净利率': (company_net_margin, industry['net_margin']),
        'ROE': (company_roe, industry['roe']),
        '流动比率': (company_current_ratio, industry['current_ratio']),
        '资产负债率': (company_debt_ratio, industry['debt_ratio']),
    }
    
    # 表格对比
    compare_data = []
    for name, (company, ind_std) in indicators.items():
        diff = company - ind_std
        status = "✅ 优于行业" if (diff > 0 and name != '资产负债率') or (diff < 0 and name == '资产负债率') else "⚠️ 低于行业"
        compare_data.append({
            "指标": name,
            "企业值": f"{company:.2f}" + ("%" if name != '流动比率' else ""),
            "行业平均": f"{ind_std:.2f}" + ("%" if name != '流动比率' else ""),
            "差异": f"{diff:+.2f}" + ("%" if name != '流动比率' else ""),
            "评价": status
        })
    
    compare_df = __import__('pandas').DataFrame(compare_data)
    st.dataframe(compare_df, use_container_width=True, hide_index=True)
    
    # 雷达图
    st.subheader("🕸️ 雷达图对比")
    
    categories = ['毛利率', '净利率', 'ROE', '流动比率', '资产负债率']
    
    # 数据归一化（简单处理）
    company_values = [
        company_gross_margin / 50 * 100,
        company_net_margin / 30 * 100,
        company_roe / 30 * 100,
        min(company_current_ratio / 3 * 100, 100),
        100 - company_debt_ratio  # 资产负债率越低越好
    ]
    
    industry_values = [
        industry['gross_margin'] / 50 * 100,
        industry['net_margin'] / 30 * 100,
        industry['roe'] / 30 * 100,
        min(industry['current_ratio'] / 3 * 100, 100),
        100 - industry['debt_ratio']
    ]
    
    fig = go.Figure()
    
    fig.add_trace(go.Scatterpolar(
        r=company_values,
        theta=categories,
        fill='toself',
        name='企业'
    ))
    
    fig.add_trace(go.Scatterpolar(
        r=industry_values,
        theta=categories,
        fill='toself',
        name='行业平均'
    ))
    
    fig.update_layout(
        polar=dict(
            radialaxis=dict(
                visible=True,
                range=[0, 100]
            )),
        showlegend=True,
        title='企业与行业对比雷达图'
    )
    
    st.plotly_chart(fig, use_container_width=True)
    
    # 分析总结
    st.subheader("📋 分析总结")
    
    analysis = []
    
    for name, (company, ind_std) in indicators.items():
        diff = company - ind_std
        if name == '资产负债率':
            if diff < 0:
                analysis.append(f"✅ {name}：{company:.1f}%，低于行业{abs(diff):.1f}%，财务风险较小")
            else:
                analysis.append(f"⚠️ {name}：{company:.1f}%，高于行业{diff:.1f}%，注意偿债风险")
        else:
            if diff > 0:
                analysis.append(f"✅ {name}：{company:.1f}%，优于行业{diff:.1f}%")
            else:
                analysis.append(f"⚠️ {name}：{company:.1f}%，低于行业{abs(diff):.1f}%")
    
    for item in analysis:
        st.info(item)

st.markdown("---")

st.info("""
💡 **使用说明**

1. 选择企业所属行业
2. 输入企业实际财务指标
3. 系统自动对比行业平均水平
4. 雷达图直观展示优劣势
5. 提供改进建议

**行业数据来源**：
- 制造业：参考 A 股制造业上市公司平均
- 科技/互联网：参考纳斯达克科技公司平均
- 零售业：参考连锁零售企业平均
- 服务业：参考服务业上市公司平均
""")
