"""
FinCopilot - 文档提取器
正则 + PyMuPDF 提取合同/发票/回单关键信息
"""
import re
import fitz  # PyMuPDF
from typing import Dict, Any, List


def extract_from_pdf(filepath: str) -> Dict[str, Any]:
    """
    从 PDF 中提取关键信息
    支持：金额、公司名、日期、发票代码等
    """
    result = {
        "amount": None,
        "company": None,
        "date": None,
        "invoice_code": None,
        "invoice_number": None,
        "text": ""
    }
    
    try:
        # 打开 PDF
        doc = fitz.open(filepath)
        text = ""
        
        # 提取所有页面文本
        for page in doc:
            text += page.get_text()
        
        result["text"] = text
        
        # 正则提取金额
        amount_patterns = [
            r'(?i)(?:金额 | 合计|总计|总额)[:：]?\s*¥?\s*([\d,]+\.?\d*)',
            r'(?i)(?:小写 | 大写)[:：]?\s*¥?\s*([\d,]+\.?\d*)',
            r'(?i)RMB\s*([\d,]+\.?\d*)',
        ]
        
        for pattern in amount_patterns:
            match = re.search(pattern, text)
            if match:
                amount_str = match.group(1).replace(',', '')
                try:
                    result["amount"] = float(amount_str)
                    break
                except:
                    continue
        
        # 提取公司名（简化版，实际需更复杂规则）
        company_patterns = [
            r'(?i)(?:购买方 | 销售方)[:：]?\s*([\u4e00-\u9fa5]+(?:公司 | 企业 | 厂 | 店))',
            r'(?i)(?:客户 | 供应商)[:：]?\s*([\u4e00-\u9fa5]+(?:公司 | 企业 | 厂 | 店))',
        ]
        
        for pattern in company_patterns:
            match = re.search(pattern, text)
            if match:
                result["company"] = match.group(1)
                break
        
        # 提取日期
        date_patterns = [
            r'(\d{4}[-/年]\d{1,2}[-/月]\d{1,2}日?)',
            r'(\d{4}[-/.]\d{1,2}[-/.]\d{1,2})',
        ]
        
        for pattern in date_patterns:
            match = re.search(pattern, text)
            if match:
                result["date"] = match.group(1)
                break
        
        # 提取发票代码
        invoice_code_match = re.search(
            r'(?i)发票代码[:：]?\s*(\d{10,12})',
            text
        )
        if invoice_code_match:
            result["invoice_code"] = invoice_code_match.group(1)
        
        # 提取发票号码
        invoice_num_match = re.search(
            r'(?i)发票号码[:：]?\s*(\d{8})',
            text
        )
        if invoice_num_match:
            result["invoice_number"] = invoice_num_match.group(1)
        
        doc.close()
        
    except Exception as e:
        result["error"] = str(e)
    
    return result


def extract_from_image(filepath: str) -> Dict[str, Any]:
    """
    从图片中提取关键信息（OCR）
    使用 PyMuPDF 的 OCR 功能或调用系统 OCR
    """
    import fitz
    
    try:
        # 打开图片
        doc = fitz.open(filepath)
        text = ""
        
        # 提取文本
        for page in doc:
            text += page.get_text()
        
        doc.close()
        
        # 使用与 PDF 相同的提取逻辑
        result = {
            "amount": None,
            "company": None,
            "date": None,
            "invoice_code": None,
            "invoice_number": None,
            "text": text
        }
        
        # 正则提取（与 extract_from_pdf 相同）
        import re
        
        # 提取金额
        amount_patterns = [
            r'(?i)(?:金额 | 合计 | 总计 | 总额)[:：]?\s*¥?\s*([\d,]+\.?\d*)',
        ]
        for pattern in amount_patterns:
            match = re.search(pattern, text)
            if match:
                result["amount"] = float(match.group(1).replace(',', ''))
                break
        
        return result
        
    except Exception as e:
        return {"error": str(e), "text": ""}


def clean_text(text: str) -> str:
    """清理文本"""
    # 去除多余空白
    text = re.sub(r'\s+', ' ', text)
    # 去除特殊字符
    text = re.sub(r'[^\w\s\u4e00-\u9fa5.,;:()$¥]', '', text)
    return text.strip()
