"""
FinCopilot - 数据治理页面
"""
import streamlit as st
from core.cleaner import find_similar_names, standardize_name

# init_page disabled

# init_page disabled

st.title("🧹 数据治理")

st.markdown("""
**功能说明**：上传 CSV/Excel 文件，系统自动聚类相似的供应商名称
""")

uploaded_file = st.file_uploader(
    "上传 CSV 或 Excel 文件",
    type=["csv", "xlsx"],
    help="支持 CSV、Excel 格式"
)

if uploaded_file:
    import pandas as pd
    
    try:
        # 读取文件
        if uploaded_file.name.endswith('.csv'):
            df = pd.read_csv(uploaded_file)
        else:
            df = pd.read_excel(uploaded_file)
        
        st.success(f"已加载：{len(df)} 条记录")
        
        # 选择供应商名称列
        columns = df.columns.tolist()
        name_column = st.selectbox(
            "选择供应商名称列",
            columns
        )
        
        if name_column:
            # 提取供应商名称列表
            names = df[name_column].dropna().unique().tolist()
            
            # 查找相似名称
            with st.spinner("正在分析相似名称..."):
                clusters = find_similar_names(names, threshold=80)
            
            if clusters:
                st.markdown(f"### ✅ 发现 {len(clusters)} 组相似名称")
                
                for standard, similars in clusters.items():
                    with st.expander(f"🏢 {standard} ({len(similars)}个相似)"):
                        st.write(f"**标准名称**: {standard}")
                        st.write("**相似名称**:")
                        for s in similars:
                            st.write(f"- {s}")
                        
                        # 提供合并按钮
                        if st.button(f"合并到 \"{standard}\"", key=f"merge_{standard}"):
                            # 更新 DataFrame
                            df[name_column] = df[name_column].apply(
                                lambda x: standard if x in similars else x
                            )
                            st.success(f"已合并 {len(similars)} 条记录")
            else:
                st.info("未发现相似名称")
        
        # 显示数据预览
        with st.expander("📊 查看数据预览"):
            st.dataframe(df.head(100), use_container_width=True)
    
    except Exception as e:
        st.error(f"读取文件失败：{e}")

st.markdown("---")

st.info("""
💡 **使用提示**

1. 上传包含供应商名称的 CSV 或 Excel 文件
2. 系统会自动识别相似的名称（如"阿里"和"阿里巴巴"）
3. 可选择合并相似名称到标准名称
""")
