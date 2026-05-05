"""
财务工作台 - 统一 UI 组件库
常用界面组件封装
"""
import streamlit as st
import pandas as pd
from datetime import datetime
from typing import Optional, List, Dict, Any, Callable


def render_form_section(
    title: str,
    fields: Dict[str, Dict],
    columns: int = 2,
    key_prefix: str = ""
) -> Dict[str, Any]:
    """
    渲染表单区块
    
    Args:
        title: 区块标题
        fields: 字段配置
        columns: 列数
        key_prefix: key 前缀
    
    Returns:
        用户输入值的字典
    """
    st.subheader(title)
    cols = st.columns(columns)
    result = {}
    
    for i, (field_name, config) in enumerate(fields.items()):
        col_idx = i % columns
        with cols[col_idx]:
            field_type = config.get('type', 'text')
            field_key = f"{key_prefix}_{field_name}"
            
            if field_type == 'text':
                result[field_name] = st.text_input(
                    label=config.get('label', field_name),
                    placeholder=config.get('placeholder', ''),
                    key=field_key
                )
            elif field_type == 'number':
                result[field_name] = st.number_input(
                    label=config.get('label', field_name),
                    min_value=config.get('min_value'),
                    max_value=config.get('max_value'),
                    step=config.get('step', 0.01),
                    key=field_key
                )
            elif field_type == 'date':
                result[field_name] = st.date_input(
                    label=config.get('label', field_name),
                    value=config.get('value', datetime.now()),
                    key=field_key
                )
            elif field_type == 'select':
                result[field_name] = st.selectbox(
                    label=config.get('label', field_name),
                    options=config.get('options', []),
                    key=field_key
                )
            elif field_type == 'textarea':
                result[field_name] = st.text_area(
                    label=config.get('label', field_name),
                    placeholder=config.get('placeholder', ''),
                    key=field_key
                )
    
    return result


def render_data_card(
    title: str,
    value: Any,
    subtitle: str = None,
    icon: str = "📊",
    delta: Any = None
):
    """渲染数据卡片"""
    col1, col2 = st.columns([3, 1])
    with col1:
        st.metric(label=f"{icon} {title}", value=value, delta=delta)
    with col2:
        if subtitle:
            st.markdown(f"<div style='text-align: right; color: #888; margin-top: 10px;'>{subtitle}</div>", 
                       unsafe_allow_html=True)


def render_success_message(message: str):
    """渲染成功消息"""
    st.success(f"✅ {message}")


def render_error_message(message: str):
    """渲染错误消息"""
    st.error(f"❌ {message}")


def render_warning_message(message: str):
    """渲染警告消息"""
    st.warning(f"⚠️ {message}")


def render_info_message(message: str):
    """渲染信息消息"""
    st.info(f"💡 {message}")
