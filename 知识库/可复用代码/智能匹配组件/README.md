# 智能匹配组件

> 版本：v1.0  
> 最后更新：2026-05-05  
> 来源项目：财务工作台 v2.0  
> 技术栈：Pandas + Difflib

---

## 📦 组件说明

智能匹配算法库，用于银行回单与发票的自动勾稽比对，支持多维度匹配策略。

### 核心功能

| 功能 | 说明 | 算法 |
|------|------|------|
| 金额日期匹配 | 按金额和日期容差匹配 | Pandas Merge |
| 模糊文本匹配 | 客商名称模糊匹配 | Difflib SequenceMatcher |
| 多对多匹配 | 一张回单对应多张发票 | 递归拆分 |
| 置信度评分 | 匹配置信度 0-100 分 | 多因素加权 |

---

## 🚀 快速开始

### 1. 安装依赖

```bash
pip install pandas python-Levenshtein
```

### 2. 导入组件

```python
from matcher import (
    match_by_amount_and_date,
    match_by_fuzzy_text,
    calculate_confidence_score
)
```

### 3. 使用示例

```python
import pandas as pd

# 准备数据
receipts = pd.DataFrame([
    {'date': '2024-01-15', 'amount': 10000.00, 'counterparty': 'ABC 公司'},
    {'date': '2024-01-16', 'amount': 5000.00, 'counterparty': 'XYZ 工厂'}
])

invoices = pd.DataFrame([
    {'date': '2024-01-15', 'amount': 10000.00, 'customer': 'ABC 有限公司'},
    {'date': '2024-01-14', 'amount': 5000.00, 'customer': 'XYZ 制造厂'}
])

# 执行匹配
matched, unmatched = match_by_amount_and_date(
    receipts, invoices,
    tolerance_days=3
)

print(f"匹配成功：{len(matched)} 条")
print(f"未匹配：{len(unmatched)} 条")
```

---

## 📊 API 参考

### `match_by_amount_and_date()`

按金额和日期匹配银行回单与发票。

**参数：**
- `receipts`: 银行回单 DataFrame
- `invoices`: 发票 DataFrame
- `amount_col_receipt`: 回单金额列名 (默认：'amount')
- `amount_col_invoice`: 发票金额列名 (默认：'amount')
- `date_col_receipt`: 回单日期列名 (默认：'date')
- `date_col_invoice`: 发票日期列名 (默认：'date')
- `tolerance_days`: 日期容差天数 (默认：3)

**返回：**
- `Tuple[pd.DataFrame, pd.DataFrame]`: (匹配结果，未匹配项)

---

### `match_by_fuzzy_text()`

按客商名称模糊匹配。

**参数：**
- `receipts`: 银行回单 DataFrame
- `invoices`: 发票 DataFrame
- `text_col_receipt`: 回单客商列名 (默认：'counterparty')
- `text_col_invoice`: 发票客商列名 (默认：'customer')
- `threshold`: 相似度阈值 0-1 (默认：0.6)

**返回：**
- `Tuple[pd.DataFrame, pd.DataFrame]`: (匹配结果，未匹配项)

---

## 💡 最佳实践

### 1. 组合使用多种匹配策略

```python
# 第一步：金额日期精确匹配
matched1, remaining_receipts = match_by_amount_and_date(receipts, invoices)

# 第二步：模糊文本匹配
matched2, remaining = match_by_fuzzy_text(remaining_receipts, remaining_invoices)

# 合并结果
all_matched = pd.concat([matched1, matched2])
```

### 2. 调整容差参数

```python
# 宽松匹配（容差 7 天）
matched = match_by_amount_and_date(receipts, invoices, tolerance_days=7)

# 严格匹配（容差 1 天）
matched = match_by_amount_and_date(receipts, invoices, tolerance_days=1)
```

### 3. 人工复核低置信度匹配

```python
# 筛选置信度低于 70 分的记录
low_confidence = matched[matched['confidence'] < 70]

# 导出人工复核
low_confidence.to_excel('待复核匹配记录.xlsx', index=False)
```

---

## 🔧 源码目录

```
智能匹配组件/
├── matcher.py        # 4,788 行
└── README.md         # 本文档
```

---

## 📝 更新日志

| 日期 | 版本 | 更新内容 |
|------|------|----------|
| 2026-05-05 | v1.0 | 初始版本，从财务工作台 v2.0 提取 |

---

*文档自动生成，最后更新：2026-05-05*
