"""
FinCopilot - 文件 IO 辅助工具
参考《财务工具箱》数据导入导出功能
"""
import pandas as pd
from typing import Dict, Any
import os


def read_excel_file(filepath: str, sheet_name: str = None) -> Dict[str, pd.DataFrame]:
    """
    读取 Excel 文件
    
    参数:
        filepath: 文件路径
        sheet_name: Sheet 名称，None 则读取所有
    
    返回:
        DataFrame 字典
    """
    if sheet_name:
        return {sheet_name: pd.read_excel(filepath, sheet_name=sheet_name)}
    else:
        return pd.read_excel(filepath, sheet_name=None)


def read_csv_file(filepath: str) -> pd.DataFrame:
    """
    读取 CSV 文件
    
    参数:
        filepath: 文件路径
    
    返回:
        DataFrame
    """
    return pd.read_csv(filepath)


def write_excel_file(df: pd.DataFrame, filepath: str, index: bool = False) -> bool:
    """
    写入 Excel 文件
    
    参数:
        df: DataFrame
        filepath: 文件路径
        index: 是否写入索引
    
    返回:
        是否成功
    """
    try:
        df.to_excel(filepath, index=index)
        return True
    except Exception as e:
        print(f"写入 Excel 失败：{e}")
        return False


def write_csv_file(df: pd.DataFrame, filepath: str, index: bool = False) -> bool:
    """
    写入 CSV 文件
    
    参数:
        df: DataFrame
        filepath: 文件路径
        index: 是否写入索引
    
    返回:
        是否成功
    """
    try:
        df.to_csv(filepath, index=index, encoding='utf-8-sig')
        return True
    except Exception as e:
        print(f"写入 CSV 失败：{e}")
        return False


def normalize_column_names(df: pd.DataFrame) -> pd.DataFrame:
    """
    标准化列名
    去除空格、统一小写
    
    参数:
        df: DataFrame
    
    返回:
        DataFrame
    """
    df = df.copy()
    df.columns = df.columns.str.strip().str.lower().str.replace(' ', '_')
    return df


def detect_encoding(filepath: str) -> str:
    """
    检测文件编码
    
    参数:
        filepath: 文件路径
    
    返回:
        编码格式
    """
    encodings = ['utf-8', 'gbk', 'gb2312', 'utf-8-sig']
    
    for encoding in encodings:
        try:
            with open(filepath, 'r', encoding=encoding) as f:
                f.read()
            return encoding
        except:
            continue
    
    return 'utf-8'
