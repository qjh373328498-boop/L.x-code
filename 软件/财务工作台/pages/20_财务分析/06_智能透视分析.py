"""
财务工作台 - 智能透视分析
多维度数据透视分析
"""
import streamlit as st
import pandas as pd
import plotly.express as px
from utils.database import get_connection, init_db

st.set_page_config(page_title="智能透视分析", page_icon="🎯", layout="wide")
init_db()

st.title("🎯 智能透视分析")

st.sidebar.header("选择数据源")
data_source = st.sidebar.selectbox(
    "数据源",
    ["发票数据", "银行流水", "企业账务", "应收应付"]
)

st.sidebar.header("透视设置")

conn = get_connection()

if data_source == "发票数据":
    df = pd.read_sql_query("SELECT * FROM invoice", conn)
    available_cols = df.columns.tolist()
elif data_source == "银行流水":
    df = pd.read_sql_query("SELECT * FROM bank_statement", conn)
    available_cols = df.columns.tolist()
elif data_source == "企业账务":
    df = pd.read_sql_query("SELECT * FROM company_statement", conn)
    available_cols = df.columns.tolist()
else:
    df = pd.read_sql_query("SELECT * FROM ar_ap", conn)
    available_cols = df.columns.tolist()

conn.close()

if df.empty:
    st.info("暂无数据")
else:
    row_col = st.selectbox("行字段", available_cols)
    col_col = st.selectbox("列字段", available_cols, index=1 if len(available_cols) > 1 else 0)
    val_col = st.selectbox("值字段", [c for c in available_cols if c != 'id'], index=2 if len(available_cols) > 2 else 1)
    
    agg_func = st.selectbox("汇总方式", ["sum", "count", "mean", "min", "max"])
    
    # 确保值列是数值类型
    if val_col in df.columns:
        df[val_col] = pd.to_numeric(df[val_col], errors='coerce')
    
    pivot_table = pd.pivot_table(
        df,
        index=row_col,
        columns=col_col,
        values=val_col,
        aggfunc=agg_func,
        fill_value=0.0,
        margins=True,
        margins_name="合计"
    )
    
    st.subheader(f"{data_source}透视表")
    st.dataframe(pivot_table, use_container_width=True)
    
    st.subheader("可视化")
    chart_type = st.selectbox("图表类型", ["柱状图", "条形图", "折线图", "面积图"])
    
    df_chart = pivot_table.drop("合计", axis=0, errors='ignore').drop("合计", axis=1, errors='ignore')
    
    if chart_type == "柱状图":
        fig = px.bar(df_chart, title=f"{row_col} x {col_col} - {val_col}")
    elif chart_type == "条形图":
        fig = px.bar(df_chart, orientation='h', title=f"{row_col} x {col_col} - {val_col}")
    elif chart_type == "折线图":
        fig = px.line(df_chart, title=f"{row_col} x {col_col} - {val_col}")
    else:
        fig = px.area(df_chart, title=f"{row_col} x {col_col} - {val_col}")
    
    fig.update_layout(height=500)
    st.plotly_chart(fig, use_container_width=True)
