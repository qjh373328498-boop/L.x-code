"""
FinCopilot - 报表美化页面
"""
import streamlit as st
import pandas as pd
from core.reporter import generate_html_report, create_analysis_summary

st.set_page_config(page_title="报表美化", page_icon="📊", layout="wide")

st.title("📊 报表美化")

st.markdown("""
**功能说明**：上传 Excel 数据，生成美化的 PDF 报告
""")

# 选项卡
tab1, tab2 = st.tabs(["数据上传", "报告预览"])

with tab1:
    uploaded_file = st.file_uploader(
        "上传 Excel 文件",
        type=["xlsx", "xls", "csv"],
        help="包含财务数据的 Excel 或 CSV 文件"
    )
    
    if uploaded_file:
        try:
            # 读取数据
            if uploaded_file.name.endswith('.csv'):
                df = pd.read_csv(uploaded_file)
            else:
                df = pd.read_excel(uploaded_file)
            
            st.success(f"已加载：{len(df)} 条记录")
            
            # 显示数据预览
            st.markdown("### 数据预览")
            st.dataframe(df.head(20), use_container_width=True)
            
            # 选择数值列
            numeric_cols = df.select_dtypes(include=['float64', 'int64']).columns.tolist()
            
            if numeric_cols:
                st.markdown("### 选择指标")
                selected_cols = st.multiselect(
                    "选择要展示的指标",
                    numeric_cols,
                    default=numeric_cols[:5] if len(numeric_cols) >= 5 else numeric_cols
                )
                
                if st.button("生成报告", type="primary"):
                    # 计算指标
                    metrics = {}
                    for col in selected_cols:
                        metrics[col] = df[col].sum()
                        metrics[f"{col}_avg"] = df[col].mean()
                        metrics[f"{col}_max"] = df[col].max()
                    
                    # 生成分析
                    analysis = create_analysis_summary(metrics)
                    
                    # 保存到 session state
                    st.session_state.report_data = {
                        'metrics': metrics,
                        'analysis': analysis,
                        'tables': {
                            '数据总览': {
                                'columns': df.columns.tolist(),
                                'rows': df.head(50).values.tolist()
                            }
                        }
                    }
                    
                    st.success("报告已生成，请切换到\"报告预览\"标签查看")
        
        except Exception as e:
            st.error(f"处理失败：{e}")

with tab2:
    if 'report_data' in st.session_state:
        data = st.session_state.report_data
        
        st.markdown("### 📊 报告预览")
        
        # 显示核心指标
        st.markdown("#### 核心指标")
        
        if data['metrics']:
            cols = st.columns(min(4, len(data['metrics'])))
            for i, (key, value) in enumerate(data['metrics'].items()):
                with cols[i % 4]:
                    st.metric(key, f"{value:,.2f}")
        
        # 显示分析总结
        if data['analysis']:
            st.markdown("#### 分析总结")
            for item in data['analysis']:
                if item['type'] == 'positive':
                    st.success(f"✅ {item['content']}")
                else:
                    st.warning(f"⚠️ {item['content']}")
        
        # 显示详细数据
        if data.get('tables'):
            st.markdown("#### 详细数据")
            for table_name, table_data in data['tables'].items():
                st.markdown(f"**{table_name}**")
                df_preview = pd.DataFrame(table_data['rows'], columns=table_data['columns'])
                st.dataframe(df_preview.head(20), use_container_width=True)
    else:
        st.info("请先在\"数据上传\"标签上传数据并生成报告")

st.markdown("---")

st.info("""
💡 **使用提示**

1. 上传包含财务数据的 Excel/CSV 文件
2. 选择要展示的指标
3. 系统自动生成分析报告
4. 支持导出为 PDF 格式（需安装 weasyprint）
""")
