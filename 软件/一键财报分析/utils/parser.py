"""
一键财报分析 - 财报解析器
支持 PDF 和 Excel 格式
"""
import pandas as pd
import pdfplumber
import re
from typing import Dict, Any


def parse_excel(filepath: str) -> Dict[str, pd.DataFrame]:
    """解析 Excel 格式财报"""
    result = {
        "balance_sheet": {},
        "income_stmt": {},
        "cash_flow": {}
    }
    
    try:
        # 读取所有 sheet
        excel_file = pd.ExcelFile(filepath, engine='openpyxl')
        sheets = excel_file.sheet_names
        
        for sheet in sheets:
            try:
                df = pd.read_excel(filepath, sheet_name=sheet, engine='openpyxl')
                sheet_lower = sheet.lower()
                
                if any(k in sheet_lower for k in ["资产", "balance"]):
                    result["balance_sheet"] = process_statement(df, "balance")
                elif any(k in sheet_lower for k in ["利润", "income", "损益"]):
                    result["income_stmt"] = process_statement(df, "income")
                elif any(k in sheet_lower for k in ["现金流", "cash"]):
                    result["cash_flow"] = process_statement(df, "cash")
            except Exception as e:
                print(f"读取 Sheet '{sheet}' 失败：{e}")
                continue
    except Exception as e:
        print(f"读取 Excel 文件失败：{e}")
        # 尝试作为单 sheet 文件读取
        try:
            df = pd.read_excel(filepath, engine='openpyxl')
            result = flatten_parse(df)
        except:
            pass
    
    return result


def flatten_parse(df: pd.DataFrame) -> Dict[str, Dict[str, float]]:
    """解析扁平化 Excel（单 sheet）"""
    result = {
        "balance_sheet": {},
        "income_stmt": {},
        "cash_flow": {}
    }
    
    # 尝试从第一列和第二列提取
    if len(df.columns) >= 2:
        for _, row in df.iterrows():
            try:
                name = str(row.iloc[0])
                value = float(row.iloc[1])
                
                if any(k in name for k in ["资产", "负债", "权益"]):
                    result["balance_sheet"][name] = value
                elif any(k in name for k in ["收入", "成本", "利润"]):
                    result["income_stmt"][name] = value
                elif "现金流" in name:
                    result["cash_flow"][name] = value
            except:
                continue
    
    return result


def process_statement(df: pd.DataFrame, stmt_type: str) -> Dict[str, float]:
    """处理财务报表，提取关键项目"""
    result = {}
    
    # 映射规则
    mapping = {
        "balance": {
            "货币资金": ["货币资金", "现金", "银行存款"],
            "应收账款": ["应收账款", "应收票据"],
            "存货": ["存货", "库存商品"],
            "流动资产": ["流动资产合计", "流动资产总计"],
            "固定资产": ["固定资产", "非流动资产"],
            "总资产": ["资产总计", "总资产"],
            "流动负债": ["流动负债合计", "流动负债总计"],
            "总负债": ["负债合计", "总负债"],
            "股东权益": ["所有者权益", "股东权益合计"],
        },
        "income": {
            "营业收入": ["营业收入", "营业总收入", "销售收入"],
            "营业成本": ["营业成本", "销售成本"],
            "毛利": ["毛利", "毛利润"],
            "营业利润": ["营业利润", "经营利润"],
            "净利润": ["净利润", "归母净利润"],
        },
        "cash": {
            "经营活动现金流净额": ["经营活动产生的现金流量净额", "经营现金流"],
            "投资活动现金流净额": ["投资活动产生的现金流量净额", "投资现金流"],
            "筹资活动现金流净额": ["筹资活动产生的现金流量净额", "筹资现金流"],
        }
    }
    
    for field, keywords in mapping.get(stmt_type, {}).items():
        value = extract_value(df, keywords)
        if value is not None:
            result[field] = value
    
    return result


def extract_value(df: pd.DataFrame, keywords: list) -> float:
    """从 DataFrame 中提取指定项目的值"""
    for keyword in keywords:
        # 尝试匹配行
        for _, row in df.iterrows():
            for cell in row:
                if isinstance(cell, str) and keyword in cell:
                    # 找到对应的数值（通常是下一列或同一行的其他列）
                    idx = row.tolist().index(cell)
                    for i in range(idx + 1, len(row)):
                        try:
                            val = float(row.iloc[i])
                            return val
                        except (ValueError, TypeError):
                            continue
    
    # 尝试从第二列提取（常见格式：项目名称 | 本期金额 | 上期金额）
    if len(df.columns) >= 2:
        for _, row in df.iterrows():
            try:
                return float(row.iloc[1])
            except (ValueError, TypeError):
                continue
    
    return 0.0


def parse_pdf(filepath: str) -> Dict[str, pd.DataFrame]:
    """解析 PDF 格式财报（简化版）"""
    result = {"balance_sheet": {}, "income_stmt": {}, "cash_flow": {}}
    
    try:
        with pdfplumber.open(filepath) as pdf:
            text = ""
            for page in pdf.pages:
                page_text = page.extract_text()
                if page_text:
                    text += page_text
            
            # 提取关键数字（简化解析）
            result = extract_from_text(text)
    except Exception as e:
        print(f"PDF 解析失败：{e}")
    
    return result


def extract_from_text(text: str) -> Dict[str, Dict[str, float]]:
    """从 PDF 文本中提取财务数据"""
    result = {
        "balance_sheet": {},
        "income_stmt": {},
        "cash_flow": {}
    }
    
    # 定义提取模式
    patterns = {
        "营业收入": r"营业收入 [：:\s]*([\d,.]+)",
        "净利润": r"净利润 [：:\s]*([\d,.]+)",
        "总资产": r"总资产 [：:\s]*([\d,.]+)",
        "总负债": r"总负债 [：:\s]*([\d,.]+)",
    }
    
    for key, pattern in patterns.items():
        match = re.search(pattern, text)
        if match:
            value_str = match.group(1).replace(",", "")
            try:
                value = float(value_str)
                # 判断属于哪个报表
                if key in ["营业收入", "净利润"]:
                    result["income_stmt"][key] = value
                elif key in ["总资产", "总负债"]:
                    result["balance_sheet"][key] = value
            except ValueError:
                continue
    
    return result


def parse_financial_report(filepath: str) -> Dict[str, Any]:
    """通用财报解析入口"""
    if filepath.endswith((".xlsx", ".xls")):
        return parse_excel(filepath)
    elif filepath.endswith(".pdf"):
        return parse_pdf(filepath)
    else:
        raise ValueError("不支持的文件格式，请上传 Excel 或 PDF 文件")
