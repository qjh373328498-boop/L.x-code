"""
财务工作台 - 行业对标页面
使用 2025-2026 年权威行业数据进行对比分析

性能优化：行业数据查询缓存（24 小时）
"""
import streamlit as st
import plotly.graph_objects as go
import sys
sys.path.append('/workspace/软件/财务工作台')
# init_page disabled
from utils.industry_2025 import INDUSTRY_STANDARDS, INDUSTRY_KEYWORDS
from utils.constants import CacheTTL

# init_page disabled

st.title("🏭 行业对标分析")

# ========== 性能优化：行业数据缓存 ==========
@st.cache_data(ttl=CacheTTL.INDUSTRY_DATA)  # 24 小时缓存
def get_industry_data_cached(industry_name: str):
    """获取行业数据（带缓存）"""
    if industry_name in INDUSTRY_STANDARDS:
        return INDUSTRY_STANDARDS[industry_name]
    return None

st.markdown("""
**功能说明**：选择所属行业，系统将企业财务指标与行业平均水平对比

**数据来源**：
- 国家统计局 2025 年规模以上工业企业财务数据
- 国务院国资委企业绩效评价标准值 2025
- 上市公司 2025 年年报统计
""")

# 行业选择
selected_industry = st.selectbox(
    "选择行业",
    list(INDUSTRY_STANDARDS.keys())
)

st.info(f"📊 当前对比行业：**{selected_industry}**")

# 企业数据输入
st.subheader("🏢 企业财务数据")

col1, col2, col3 = st.columns(3)

with col1:
    st.markdown("**盈利能力**")
    company_gross_margin = st.number_input("毛利率 (%)", min_value=0.0, value=30.0, step=0.1)
    company_net_margin = st.number_input("净利润率 (%)", min_value=0.0, value=10.0, step=0.1)
    company_roe = st.number_input("净资产收益率 (%)", min_value=0.0, value=15.0, step=0.1)

with col2:
    st.markdown("**偿债能力**")
    company_current_ratio = st.number_input("流动比率", min_value=0.0, value=2.0, step=0.1)
    company_quick_ratio = st.number_input("速动比率", min_value=0.0, value=1.5, step=0.1)
    company_debt_ratio = st.number_input("资产负债率 (%)", min_value=0.0, value=50.0, step=0.1)

with col3:
    st.markdown("**营运能力**")
    company_ar_turnover = st.number_input("应收账款周转率 (次)", min_value=0.0, value=6.0, step=0.1)
    company_ar_days = st.number_input("应收账款周转天数 (天)", min_value=0.0, value=60.0, step=1.0)
    company_inv_turnover = st.number_input("存货周转率 (次)", min_value=0.0, value=8.0, step=0.1)
    company_inv_days = st.number_input("存货周转天数 (天)", min_value=0.0, value=45.0, step=1.0)

st.markdown("---")

# 对比分析
if st.button("开始对比分析", type="primary"):
    # 性能优化：使用缓存获取行业数据
    industry = get_industry_data_cached(selected_industry)
    
    if not industry:
        st.error(f"未找到 {selected_industry} 的行业数据")
        st.stop()
    
    # 指标对比（使用五档评价）
    st.subheader("📊 指标对比")
    
    # 定义指标映射（中文名称 -> 数据键名）
    indicator_mapping = {
        '毛利率': ('毛利率', company_gross_margin),
        '净利润率': ('净利润率', company_net_margin),
        '净资产收益率': ('净资产收益率', company_roe),
        '流动比率': ('流动比率', company_current_ratio),
        '速动比率': ('速动比率', company_quick_ratio),
        '资产负债率': ('资产负债率', company_debt_ratio),
        '应收账款周转天数': ('应收账款周转天数', company_ar_days),
        '存货周转天数': ('存货周转天数', company_inv_days),
    }
    
    # 表格对比
    compare_data = []
    for name, (key, company_value) in indicator_mapping.items():
        if key in industry:
            std = industry[key]
            # 确定企业所在位置
            if company_value >= std['excellent']:
                level = "优秀"
                level_en = 'excellent'
            elif company_value >= std['good']:
                level = "良好"
                level_en = 'good'
            elif company_value >= std['average']:
                level = "平均"
                level_en = 'average'
            elif company_value >= std['low']:
                level = "较低"
                level_en = 'low'
            else:
                level = "较差"
                level_en = 'poor'
            
            diff = company_value - std['average']
            # 判断好坏（资产负债率和周转天数越低越好）
            lower_is_better = key in ['资产负债率', '应收账款周转天数', '存货周转天数']
            
            if lower_is_better:
                status = "✅ 优于行业" if diff < 0 else "⚠️ 低于行业"
            else:
                status = "✅ 优于行业" if diff > 0 else "⚠️ 低于行业"
            
            compare_data.append({
                "指标": name,
                "企业值": f"{company_value:.2f}" + ("%" if '率' in name else "天" if '天数' in name else "次"),
                "行业平均": f"{std['average']:.2f}" + ("%" if '率' in name else "天" if '天数' in name else "次"),
                "行业五档": f"优秀≥{std['excellent']:.1f} | 良好≥{std['good']:.1f} | 平均≥{std['average']:.1f} | 较低≥{std['low']:.1f} | 较差<{std['low']:.1f}",
                "企业水平": level,
                "差异": f"{diff:+.2f}",
                "评价": status
            })
    
    if compare_data:
        compare_df = __import__('pandas').DataFrame(compare_data)
        st.dataframe(compare_df, use_container_width=True, hide_index=True)
    
    # 雷达图对比
    st.subheader("🕸️ 雷达图对比")
    
    categories = ['毛利率', '净利润率', '净资产收益率', '流动比率', '资产负债率']
    
    # 归一化处理
    def normalize(value, key, industry_data):
        if key not in industry_data:
            return 50
        std = industry_data[key]
        # 将五档评价映射到 0-100 分
        if value >= std['excellent']:
            return min(100, 95 + (value - std['excellent']) / std['excellent'] * 10)
        elif value >= std['good']:
            return 80 + (value - std['good']) / (std['excellent'] - std['good']) * 15 if std['excellent'] != std['good'] else 80
        elif value >= std['average']:
            return 60 + (value - std['average']) / (std['good'] - std['average']) * 20 if std['good'] != std['average'] else 60
        elif value >= std['low']:
            return 40 + (value - std['low']) / (std['average'] - std['low']) * 20 if std['average'] != std['low'] else 40
        else:
            return max(0, 40 * value / std['low'])
    
    company_values = [
        normalize(company_gross_margin, '毛利率', industry),
        normalize(company_net_margin, '净利润率', industry),
        normalize(company_roe, '净资产收益率', industry),
        normalize(company_current_ratio, '流动比率', industry),
        normalize(100 - company_debt_ratio, '资产负债率', {
            '资产负债率': {
                'excellent': 100 - industry.get('资产负债率', {}).get('excellent', 40),
                'good': 100 - industry.get('资产负债率', {}).get('good', 50),
                'average': 100 - industry.get('资产负债率', {}).get('average', 57),
                'low': 100 - industry.get('资产负债率', {}).get('low', 65),
                'poor': 100 - industry.get('资产负债率', {}).get('poor', 75)
            }
        })
    ]
    
    # 行业平均水平（平均档对应 60 分）
    industry_values = [60, 60, 60, 60, 60]
    
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
        title='企业与行业对比雷达图（满分 100 分）'
    )
    
    st.plotly_chart(fig, use_container_width=True)
    
    # 分析总结
    st.subheader("📋 分析总结")
    
    analysis = []
    for name, (key, company_value) in indicator_mapping.items():
        if key in industry:
            std = industry[key]
            lower_is_better = key in ['资产负债率', '应收账款周转天数', '存货周转天数']
            
            if company_value >= std['excellent']:
                level = "优秀"
            elif company_value >= std['good']:
                level = "良好"
            elif company_value >= std['average']:
                level = "平均"
            elif company_value >= std['low']:
                level = "较低"
            else:
                level = "较差"
            
            diff = company_value - std['average']
            
            if lower_is_better:
                if diff < 0:
                    analysis.append(f"✅ {name}：{company_value:.1f}，{level}，低于行业平均{abs(diff):.1f}，表现优秀")
                else:
                    analysis.append(f"⚠️ {name}：{company_value:.1f}，{level}，高于行业平均{diff:.1f}，需要改善")
            else:
                if diff > 0:
                    analysis.append(f"✅ {name}：{company_value:.1f}，{level}，优于行业平均{diff:.1f}")
                else:
                    analysis.append(f"⚠️ {name}：{company_value:.1f}，{level}，低于行业平均{abs(diff):.1f}")
    
    for item in analysis:
        st.info(item)

st.markdown("---")

st.info("""
💡 **使用说明**

1. 选择企业所属行业
2. 输入企业实际财务指标
3. 系统自动对比行业五档标准值（优秀/良好/平均/较低/较差）
4. 雷达图直观展示企业在各维度的得分
5. 提供详细的分析总结

**行业数据来源**：
- 国家统计局 2025 年规模以上工业企业财务数据
- 国务院国资委《企业绩效评价标准值2025》
- 上市公司2025年年报统计数据
- 新浪财经鹰眼预警行业对比数据

**数据更新**：2026 年 5 月（最新版）
""")
