"""
FinCopilot - 合规检查器
规则引擎实现报销预审/合规检查
"""
import re
from typing import Dict, List, Any


def check_reimbursement(expense: Dict[str, Any]) -> List[Dict]:
    """
    报销预审检查
    
    参数:
        expense: 报销单字典，包含：
            - amount: 金额
            - type: 费用类型
            - date: 日期
            - receipts: 发票列表
    
    返回:
        问题列表
    """
    issues = []
    
    # 检查金额是否超标（示例：差旅费上限 5000）
    if expense.get('type') == '差旅' and expense.get('amount', 0) > 5000:
        issues.append({
            'type': '超标',
            'message': f"差旅费 {expense['amount']} 超过上限 5000"
        })
    
    # 检查连号发票
    receipts = expense.get('receipts', [])
    if len(receipts) >= 2:
        invoice_numbers = [r.get('invoice_number', '') for r in receipts]
        
        # 检查是否有连号
        for i in range(len(invoice_numbers) - 1):
            num1 = invoice_numbers[i]
            num2 = invoice_numbers[i + 1]
            
            if num1 and num2 and is_consecutive_numbers(num1, num2):
                issues.append({
                    'type': '连号',
                    'message': f"发票连号风险：{num1} 和 {num2}"
                })
    
    return issues


def is_consecutive_numbers(num1: str, num2: str) -> bool:
    """
    检查两个号码是否连续
    """
    try:
        # 提取数字部分
        digits1 = re.sub(r'\D', '', num1)
        digits2 = re.sub(r'\D', '', num2)
        
        if len(digits1) >= 6 and len(digits2) >= 6:
            n1 = int(digits1[-6:])
            n2 = int(digits2[-6:])
            return abs(n1 - n2) == 1
    except:
        pass
    
    return False


def validate_invoice(invoice: Dict[str, Any]) -> List[Dict]:
    """
    发票验证
    
    参数:
        invoice: 发票信息字典
    
    返回:
        问题列表
    """
    issues = []
    
    # 检查必填字段
    required_fields = ['amount', 'date', 'company']
    for field in required_fields:
        if not invoice.get(field):
            issues.append({
                'type': '缺失',
                'message': f"缺少必要字段：{field}"
            })
    
    # 检查金额格式
    amount = invoice.get('amount')
    if amount and amount <= 0:
        issues.append({
            'type': '金额异常',
            'message': f"金额 {amount} 无效"
        })
    
    return issues


def check_expense_trend(expenses: List[Dict[str, Any]], months: int = 6) -> Dict[str, Any]:
    """
    费用趋势分析
    检测异常波动
    
    参数:
        expenses: 费用列表，每项包含 month 和 amount
        months: 分析月数
    
    返回:
        分析报告
    """
    if len(expenses) < 2:
        return {'status': '数据不足'}
    
    # 计算平均值
    total = sum(e.get('amount', 0) for e in expenses)
    avg = total / len(expenses)
    
    # 检测异常
    anomalies = []
    for expense in expenses:
        amount = expense.get('amount', 0)
        if amount > avg * 2:  # 超过平均值 2 倍
            anomalies.append({
                'month': expense.get('month'),
                'amount': amount,
                'ratio': amount / avg
            })
    
    return {
        'total': total,
        'average': avg,
        'anomalies': anomalies
    }
