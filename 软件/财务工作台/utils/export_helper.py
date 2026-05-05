"""
FinCopilot - 数据导出工具
支持导出为 Excel/CSV
"""
import pandas as pd
import streamlit as st
from typing import Dict, Any


def export_to_excel(data: Dict[str, pd.DataFrame], filename: str) -> str:
    """
    导出多个 DataFrame 到 Excel 的不同 Sheet
    
    参数:
        data: DataFrame 字典 {sheet_name: df}
        filename: 输出文件名
    
    返回:
        文件路径
    """
    import tempfile
    import os
    
    temp_dir = tempfile.gettempdir()
    filepath = os.path.join(temp_dir, filename)
    
    try:
        with pd.ExcelWriter(filepath, engine='xlsxwriter') as writer:
            for sheet_name, df in data.items():
                # 清理 sheet 名称（不能超过 31 字符）
                clean_name = sheet_name[:31].replace('/', '-').replace('\\', '-')
                df.to_excel(writer, sheet_name=clean_name, index=False)
        
        return filepath
    except Exception as e:
        st.error(f"导出失败：{e}")
        return None


def export_dataframe_to_csv(df: pd.DataFrame, filename: str) -> str:
    """
    导出单个 DataFrame 为 CSV
    
    参数:
        df: DataFrame
        filename: 输出文件名
    
    返回:
        文件路径
    """
    import tempfile
    import os
    
    temp_dir = tempfile.gettempdir()
    filepath = os.path.join(temp_dir, filename)
    
    try:
        df.to_csv(filepath, index=False, encoding='utf-8-sig')
        return filepath
    except Exception as e:
        st.error(f"导出失败：{e}")
        return None


def create_download_button(data: Any, filename: str, label: str = "📥 下载", key: str = None):
    """
    创建下载按钮
    
    参数:
        data: 要下载的数据（CSV 格式字符串或字节）
        filename: 文件名
        label: 按钮文本
        key: 按钮唯一 key
    
    返回:
        Streamlit 下载按钮
    """
    if isinstance(data, pd.DataFrame):
        # DataFrame 转为 CSV
        csv = data.to_csv(index=False, encoding='utf-8-sig').encode('utf-8')
        return st.download_button(
            label=label,
            data=csv,
            file_name=filename,
            mime='text/csv',
            key=key
        )
    else:
        # 其他类型
        return st.download_button(
            label=label,
            data=data,
            file_name=filename,
            key=key
        )


def export_matching_result(matched_df: pd.DataFrame, receipts_df: pd.DataFrame, invoices_df: pd.DataFrame) -> str:
    """
    导出关联匹配结果
    
    参数:
        matched_df: 匹配结果
        receipts_df: 银行回单
        invoices_df: 发票记录
    
    返回:
        Excel 文件路径
    """
    data = {
        '匹配结果': matched_df,
        '银行回单': receipts_df,
        '发票记录': invoices_df
    }
    
    return export_to_excel(data, '关联匹配结果.xlsx')
