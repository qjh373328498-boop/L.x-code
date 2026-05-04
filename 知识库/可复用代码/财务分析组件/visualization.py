"""
可视化组件库
来源：一键财报分析、财务工具箱、学创杯辅助软件
功能：雷达图、趋势图、指标卡片、对比图
"""

import plotly.express as px
import plotly.graph_objects as go
import streamlit as st
from typing import List, Dict, Optional, Any


def create_radar_chart(
    metrics: List[str],
    values: List[float],
    industry_avg: Optional[List[float]] = None,
    title: str = "能力雷达图",
    max_value: float = 100
) -> go.Figure:
    """
    创建多维能力雷达图（支持行业对比）
    
    Args:
        metrics: 指标名称列表
        values: 指标值列表
        industry_avg: 行业平均值（可选）
        title: 图表标题
        max_value: 最大值（用于标准化）
    
    Returns:
        Plotly Figure 对象
    """
    fig = go.Figure()
    
    # 添加数据
    fig.add_trace(go.Scatterpolar(
        r=values,
        theta=metrics,
        fill='toself',
        name='当前值',
        line=dict(color='rgba(41, 128, 185, 0.8)'),
        fillcolor='rgba(41, 128, 185, 0.3)'
    ))
    
    # 添加行业对比（可选）
    if industry_avg:
        fig.add_trace(go.Scatterpolar(
            r=industry_avg,
            theta=metrics,
            fill='toself',
            name='行业平均',
            line=dict(color='rgba(231, 76, 60, 0.8)', dash='dash'),
            fillcolor='rgba(231, 76, 60, 0.1)'
        ))
    
    fig.update_layout(
        polar=dict(
            radialaxis=dict(
                visible=True,
                range=[0, max_value]
            )
        ),
        showlegend=True,
        title=title,
        height=600
    )
    
    return fig


def create_trend_chart(
    df,
    x_col: str,
    y_cols: List[str],
    title: str = "趋势分析",
    chart_type: str = "line"
) -> go.Figure:
    """
    创建趋势图表（支持折线图/柱状图）
    
    Args:
        df: pandas DataFrame
        x_col: X 轴列名
        y_cols: Y 轴列名列表
        title: 图表标题
        chart_type: 图表类型 ('line' 或 'bar')
    
    Returns:
        Plotly Figure 对象
    """
    fig = go.Figure()
    
    for col in y_cols:
        if chart_type == "line":
            fig.add_trace(go.Scatter(
                x=df[x_col],
                y=df[col],
                name=col,
                mode='lines+markers'
            ))
        else:  # bar
            fig.add_trace(go.Bar(
                x=df[x_col],
                y=df[col],
                name=col
            ))
    
    fig.update_layout(
        title=title,
        xaxis_title=x_col,
        yaxis_title="数值",
        hovermode='x unified',
        height=500
    )
    
    return fig


def create_metric_card(
    title: str,
    value: Any,
    delta: Optional[float] = None,
    delta_color: str = "normal",
    help_text: str = ""
) -> None:
    """
    渲染统一风格的指标卡片
    
    Args:
        title: 指标名称
        value: 指标值
        delta: 变化值（可选）
        delta_color: 颜色模式 ('normal', 'inverse', 'off')
        help_text: 帮助文本
    """
    st.metric(
        label=title,
        value=value,
        delta=delta,
        delta_color=delta_color,
        help=help_text
    )


def create_comparison_chart(
    categories: List[str],
    series: Dict[str, List[float]],
    title: str = "对比分析",
    orientation: str = "v"
) -> go.Figure:
    """
    创建多系列对比图
    
    Args:
        categories: 分类标签
        series: 系列数据 {'系列名': [值 1, 值 2, ...]}
        title: 图表标题
        orientation: 方向 ('v' 垂直 或 'h' 水平)
    
    Returns:
        Plotly Figure 对象
    """
    fig = go.Figure()
    
    for name, values in series.items():
        if orientation == "v":
            fig.add_trace(go.Bar(
                x=categories,
                y=values,
                name=name
            ))
        else:  # horizontal
            fig.add_trace(go.Bar(
                y=categories,
                x=values,
                name=name,
                orientation='h'
            ))
    
    fig.update_layout(
        title=title,
        barmode='group',
        height=500,
        showlegend=True
    )
    
    return fig


def create_gauge_chart(
    value: float,
    min_val: float = 0,
    max_val: float = 100,
    title: str = "完成度",
    thresholds: Optional[Dict[str, float]] = None
) -> go.Figure:
    """
    创建仪表盘图表
    
    Args:
        value: 当前值
        min_val: 最小值
        max_val: 最大值
        title: 图表标题
        thresholds: 阈值配置 {'warning': 60, 'danger': 30}
    
    Returns:
        Plotly Figure 对象
    """
    fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=value,
        domain={'x': [0, 1], 'y': [0, 1]},
        title={'text': title},
        gauge={
            'axis': {'range': [min_val, max_val]},
            'bar': {'color': "darkblue"},
            'steps': [
                {'range': [min_val, max_val * 0.3], 'color': "#ffebee"},
                {'range': [max_val * 0.3, max_val * 0.7], 'color': "#fff3e0"},
                {'range': [max_val * 0.7, max_val], 'color': "#e8f5e9"}
            ],
        }
    ))
    
    fig.update_layout(height=400)
    return fig


def create_waterfall_chart(
    labels: List[str],
    values: List[float],
    title: str = "瀑布图分析"
) -> go.Figure:
    """
    创建瀑布图（用于财务分析）
    
    Args:
        labels: 标签列表
        values: 数值列表（正负值）
        title: 图表标题
    
    Returns:
        Plotly Figure 对象
    """
    fig = go.Figure(go.Waterfall(
        name="财务状况",
        orientation="v",
        measure=["relative"] * len(values),
        x=labels,
        y=values,
        textposition="outside",
        connector={"line": {"color": "rgb(63, 63, 63)"}}
    ))
    
    fig.update_layout(
        title=title,
        showlegend=False,
        height=500
    )
    
    return fig


# Streamlit 缓存装饰器
@st.cache_data
def load_chart_data(file_path: str) -> Any:
    """
    缓存加载图表数据
    """
    import pandas as pd
    return pd.read_csv(file_path)
