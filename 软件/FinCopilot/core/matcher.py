"""
FinCopilot - 智能匹配器
Pandas Merge + Difflib 实现回单 - 发票勾稽
"""
import pandas as pd
import difflib
from typing import Dict, List, Tuple


def match_by_amount_and_date(
    receipts: pd.DataFrame,
    invoices: pd.DataFrame,
    amount_col_receipt: str = 'amount',
    amount_col_invoice: str = 'amount',
    date_col_receipt: str = 'date',
    date_col_invoice: str = 'date',
    tolerance_days: int = 3
) -> Tuple[pd.DataFrame, pd.DataFrame]:
    """
    按金额和日期匹配
    
    参数:
        receipts: 银行回单 DataFrame
        invoices: 发票 DataFrame
        tolerance_days: 日期容差天数
    
    返回:
        (匹配结果，未匹配项)
    """
    # 复制数据
    receipts = receipts.copy()
    invoices = invoices.copy()
    
    matched = []
    unmatched_receipts = []
    unmatched_invoices = invoices.copy()
    
    # 遍历回单
    for idx, receipt in receipts.iterrows():
        matched_flag = False
        
        # 查找金额接近的发票
        amount_diff = (invoices[amount_col_invoice] - receipt[amount_col_receipt]).abs()
        candidates = invoices[amount_diff < 0.01]  # 金额差异小于 0.01
        
        for inv_idx, candidate in candidates.iterrows():
            # 检查日期
            try:
                from datetime import datetime, timedelta
                receipt_date = pd.to_datetime(receipt[date_col_receipt])
                invoice_date = pd.to_datetime(candidate[date_col_invoice])
                
                if abs((receipt_date - invoice_date).days) <= tolerance_days:
                    # 匹配成功
                    matched.append({
                        'receipt_id': receipt.get('id', idx),
                        'invoice_id': candidate.get('id', inv_idx),
                        'amount': receipt[amount_col_receipt],
                        'match_type': '金额 + 日期'
                    })
                    
                    # 从未匹配发票中移除
                    unmatched_invoices = unmatched_invoices[unmatched_invoices.index != inv_idx]
                    matched_flag = True
                    break
            except:
                continue
        
        if not matched_flag:
            unmatched_receipts.append(receipt)
    
    return (pd.DataFrame(matched), pd.DataFrame(unmatched_receipts))


def match_by_description(
    receipts: pd.DataFrame,
    invoices: pd.DataFrame,
    desc_col_receipt: str = 'description',
    desc_col_invoice: str = 'company',
    threshold: float = 0.8
) -> pd.DataFrame:
    """
    按摘要匹配（模糊匹配）
    
    参数:
        threshold: 匹配置信度阈值
    """
    matched = []
    
    for idx, receipt in receipts.iterrows():
        receipt_desc = str(receipt.get(desc_col_receipt, ''))
        
        # 使用 difflib 查找最相似的
        best_match = None
        best_score = 0
        
        for inv_idx, invoice in invoices.iterrows():
            invoice_desc = str(invoice.get(desc_col_invoice, ''))
            similarity = difflib.SequenceMatcher(None, receipt_desc, invoice_desc).ratio()
            
            if similarity > best_score and similarity >= threshold:
                best_score = similarity
                best_match = inv_idx
        
        if best_match is not None:
            matched.append({
                'receipt_id': receipt.get('id', idx),
                'invoice_id': best_match,
                'similarity': best_score,
                'match_type': '摘要模糊匹配'
            })
    
    return pd.DataFrame(matched)


def smart_match(receipts_df: pd.DataFrame, invoices_df: pd.DataFrame) -> Dict[str, pd.DataFrame]:
    """
    智能匹配：组合多种匹配策略
    
    返回:
        匹配结果字典
    """
    # 策略 1：金额 + 日期匹配
    matched1, unmatched_receipts = match_by_amount_and_date(receipts_df, invoices_df)
    
    # 策略 2：摘要模糊匹配（针对未匹配的）
    if not unmatched_receipts.empty:
        remaining_invoices = invoices_df[~invoices_df.index.isin(matched1['invoice_id'])]
        matched2 = match_by_description(unmatched_receipts, remaining_invoices)
        matched_all = pd.concat([matched1, matched2], ignore_index=True)
    else:
        matched_all = matched1
    
    # 统计
    total_receipts = len(receipts_df)
    total_invoices = len(invoices_df)
    matched_count = len(matched_all)
    
    return {
        'matched': matched_all,
        'unmatched_receipts_count': total_receipts - matched_count,
        'unmatched_invoices_count': total_invoices - matched_count,
        'match_rate': matched_count / max(total_receipts, total_invoices) if max(total_receipts, total_invoices) > 0 else 0
    }
