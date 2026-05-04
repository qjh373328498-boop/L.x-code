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
    
    # 精确匹配优先，使用有序字典，更具体的项目放前面
    mapping_order = [
        "流动资产", "固定资产", "总资产", 
        "流动负债", "负债合计", "总负债", 
        "股东权益", "货币资金", "应收账款", "存货",
        "营业收入", "营业成本", "营业利润", "净利润"
    ]
    
    # 映射规则（扩展关键词）
    mapping = {
        "balance": {
            "货币资金": ["货币资金", "现金", "银行存款"],
            "应收账款": ["应收账款", "应收票据", "应收款项"],
            "存货": ["存货", "库存商品", "原材料"],
            "流动资产": ["流动资产合计", "流动资产总计", "流动资产"],
            "固定资产": ["固定资产", "非流动资产", "在建工程"],
            "总资产": ["资产总计", "总资产", "合并资产总计", "公司资产总计"],
            "流动负债": ["流动负债合计", "流动负债总计", "流动负债"],
            "负债合计": ["负债合计", "总负债", "合并负债合计", "公司负债合计"],
            "股东权益": ["所有者权益合计", "股东权益合计", "归属于母公司所有者权益合计", "合并所有者权益合计"],
        },
        "income": {
            "营业收入": ["营业收入", "营业总收入", "销售收入", "主营业务收入"],
            "营业成本": ["营业成本", "销售成本", "主营业务成本"],
            "营业利润": ["营业利润", "经营利润", "营业总收入"],
            "净利润": ["净利润", "归母净利润", "归属于母公司所有者的净利润", "本期利润"],
        },
        "cash": {
            "经营活动现金流净额": ["经营活动产生的现金流量净额", "经营现金流", "经营活动现金"],
            "投资活动现金流净额": ["投资活动产生的现金流量净额", "投资现金流", "投资活动现金"],
            "筹资活动现金流净额": ["筹资活动产生的现金流量净额", "筹资现金流", "筹资活动现金"],
        }
    }
    
    for field, keywords in mapping.get(stmt_type, {}).items():
        value = extract_value(df, keywords)
        if value is not None and value > 0:
            result[field] = value
    
    return result


def extract_value(df: pd.DataFrame, keywords: list) -> float:
    """从 DataFrame 中提取指定项目的值"""
    candidates = []  # 收集所有候选值
    
    for keyword in keywords:
        # 遍历每一行
        for row_idx, row in df.iterrows():
            for col_idx, cell in enumerate(row):
                if isinstance(cell, str):
                    cell_clean = cell.strip()
                    # 完全匹配或包含匹配（但排除百分比）
                    if (cell_clean == keyword or keyword in cell_clean) and '率' not in cell_clean:
                        # 在同一行的后续列中查找数值
                        for i in range(col_idx + 1, len(row)):
                            try:
                                val_str = str(row.iloc[i]).strip().replace(',', '')
                                # 跳过百分比和空值
                                if val_str and val_str not in ['-', 'N/A', 'null', 'None', '']:
                                    value = float(val_str)
                                    # 检查是否是合理的财务数据（排除百分比）
                                    if value > 1000:  # 财务数据通常至少几千
                                        candidates.append(value)
                            except (ValueError, TypeError):
                                continue
    
    if not candidates:
        return 0.0
    
    # 返回最大值（通常合并报表数据最大）
    return max(candidates)


def parse_pdf(filepath: str) -> Dict[str, pd.DataFrame]:
    """解析 PDF 格式财报（表格 + 文本提取）"""
    result = {"balance_sheet": {}, "income_stmt": {}, "cash_flow": {}}
    
    try:
        with pdfplumber.open(filepath) as pdf:
            # 1. 先尝试从表格中提取
            for page in pdf.pages:
                tables = page.extract_tables()
                if not tables:
                    continue
                
                for table in tables:
                    if not table or len(table) < 3:
                        continue
                    
                    # 转换为 DataFrame
                    try:
                        df = pd.DataFrame(table[1:], columns=table[0] if table[0] else range(len(table[0])))
                        
                        # 清理数据
                        for col in df.columns:
                            df[col] = df[col].apply(lambda x: x.strip() if isinstance(x, str) else x)
                        
                        # 提取数据
                        balance_data = process_statement(df, "balance")
                        income_data = process_statement(df, "income")
                        cash_data = process_statement(df, "cash")
                        
                        # 合并结果（保留最大值，因为合并报表数据通常最大）
                        for k, v in balance_data.items():
                            if v > 0:
                                result["balance_sheet"][k] = max(result["balance_sheet"].get(k, 0), v)
                        for k, v in income_data.items():
                            if v > 0:
                                result["income_stmt"][k] = max(result["income_stmt"].get(k, 0), v)
                        for k, v in cash_data.items():
                            if v > 0:
                                result["cash_flow"][k] = max(result["cash_flow"].get(k, 0), v)
                    except:
                        continue
            
            # 2. 用文本提取补充缺失字段
            text = ""
            for page in pdf.pages:
                page_text = page.extract_text()
                if page_text:
                    text += page_text + "\n"
            
            text_data = extract_from_text(text)
            # 只在表格数据缺失时才用文本数据补充
            for k, v in text_data["balance_sheet"].items():
                if k not in result["balance_sheet"] and v > 0:
                    result["balance_sheet"][k] = v
            for k, v in text_data["income_stmt"].items():
                if k not in result["income_stmt"] and v > 0:
                    result["income_stmt"][k] = v
            for k, v in text_data["cash_flow"].items():
                if k not in result["cash_flow"] and v > 0:
                    result["cash_flow"][k] = v
                    
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
    
    # 定义提取模式（扩展版）
    patterns = {
        # 资产负债表
        "总资产": (r"总资产 [：:\s]*([\d,.]+)", "balance_sheet"),
        "资产总计": (r"资产总计 [：:\s]*([\d,.]+)", "balance_sheet"),
        "负债合计": (r"负债合计 [：:\s]*([\d,.]+)", "balance_sheet"),
        "总负债": (r"总负债 [：:\s]*([\d,.]+)", "balance_sheet"),
        "股东权益": (r"股东权益 [：:\s]*([\d,.]+)", "balance_sheet"),
        "所有者权益": (r"所有者权益 [：:\s]*([\d,.]+)", "balance_sheet"),
        "净资产": (r"净资产 [：:\s]*([\d,.]+)", "balance_sheet"),
        "货币资金": (r"货币资金 [：:\s]*([\d,.]+)", "balance_sheet"),
        "应收账款": (r"应收账款 [：:\s]*([\d,.]+)", "balance_sheet"),
        "存货": (r"存货 [：:\s]*([\d,.]+)", "balance_sheet"),
        "流动资产": (r"流动资产 [：:\s]*([\d,.]+)", "balance_sheet"),
        "固定资产": (r"固定资产 [：:\s]*([\d,.]+)", "balance_sheet"),
        "流动负债": (r"流动负债 [：:\s]*([\d,.]+)", "balance_sheet"),
        # 利润表
        "营业收入": (r"营业收入 [：:\s]*([\d,.]+)", "income_stmt"),
        "营业总收入": (r"营业总收入 [：:\s]*([\d,.]+)", "income_stmt"),
        "营业成本": (r"营业成本 [：:\s]*([\d,.]+)", "income_stmt"),
        "营业利润": (r"营业利润 [：:\s]*([\d,.]+)", "income_stmt"),
        "净利润": (r"净利润 [：:\s]*([\d,.]+)", "income_stmt"),
        "归母净利润": (r"归母净利润 [：:\s]*([\d,.]+)", "income_stmt"),
        # 现金流
        "经营活动现金流": (r"经营活动 [的]?.*现金流量净额 [：:\s]*([\d,.]+)", "cash_flow"),
        "投资活动现金流": (r"投资活动 [的]?.*现金流量净额 [：:\s]*([\d,.]+)", "cash_flow"),
        "筹资活动现金流": (r"筹资活动 [的]?.*现金流量净额 [：:\s]*([\d,.]+)", "cash_flow"),
    }
    
    for key, (pattern, target) in patterns.items():
        matches = re.findall(pattern, text)
        if matches:
            try:
                # 取最大的数值（通常是合并报表数据）
                value_str = max(matches, key=lambda x: len(x)).replace(",", "")
                value = float(value_str)
                result[target][key] = value
            except ValueError:
                continue
    
    return result


def parse_financial_report(filepath: str) -> Dict[str, Any]:
    """通用财报解析入口"""
    if filepath.endswith((".xlsx", ".xls")):
        result = parse_excel(filepath)
    elif filepath.endswith(".pdf"):
        result = parse_pdf(filepath)
    else:
        raise ValueError("不支持的文件格式，请上传 Excel 或 PDF 文件")
    
    # 验证并修正会计等式
    bs = result.get("balance_sheet", {})
    if bs:
        assets = bs.get("总资产", 0) or bs.get("资产总计", 0)
        liabilities = bs.get("负债合计", 0) or bs.get("总负债", 0)
        equity = bs.get("股东权益", 0) or bs.get("所有者权益", 0) or bs.get("净资产", 0)
        
        # 如果资产和负债都有值，优先用会计等式推算权益
        if assets > 0 and liabilities > 0:
            calculated_equity = assets - liabilities
            # 如果权益缺失或差异超过 1%，使用推算值
            if equity == 0 or abs(calculated_equity - equity) / max(assets, 1) > 0.01:
                result["balance_sheet"]["股东权益"] = calculated_equity
    
    return result
