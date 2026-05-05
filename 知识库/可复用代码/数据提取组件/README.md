# 数据提取组件

> 版本：v1.0  
> 最后更新：2026-05-05  
> 来源项目：财务工作台 v2.0  
> 技术栈：pdfplumber + openpyxl + Pandas

---

## 📦 组件说明

专业财务文档数据提取引擎，支持 PDF/Excel 格式的财报、发票、银行回单等文档的自动解析和数据提取。

### 核心功能

| 功能 | 说明 | 技术支持 |
|------|------|---------|
| PDF 表格提取 | 从 PDF 财报中提取表格数据 | pdfplumber |
| Excel 解析 | 读取 Excel 财报/流水 | openpyxl |
| 智能识别 | 自动识别文档格式和类型 | 规则引擎 |
| 数据清洗 | 清洗提取的原始数据 | Pandas |
| 批量处理 | 多线程批量解析文档 | concurrent.futures |

---

## 🚀 快速开始

### 1. 安装依赖

```bash
pip install pdfplumber openpyxl pandas
```

### 2. 导入组件

```python
from extractor import (
    extract_from_pdf,
    extract_from_excel,
    auto_detect_format,
    batch_extract
)
```

### 3. 使用示例

```python
# 从 PDF 财报提取数据
data = extract_from_pdf(
    '2024 年度财报.pdf',
    target_tables=['利润表', '资产负债表']
)

# 从 Excel 提取银行流水
transactions = extract_from_excel(
    '银行流水.xlsx',
    sheet_name='流水明细',
    date_col='交易日期',
    amount_col='金额'
)

# 自动识别并提取
data = auto_detect_format('未知格式文件.pdf')
```

---

## 📊 API 参考

### `extract_from_pdf()`

从 PDF 文档提取表格数据。

**参数：**
- `file_path`: PDF 文件路径
- `target_tables`: 目标表格名称列表 (可选)
- `page_range`: 页码范围 (可选，默认：全部)

**返回：**
- `Dict[str, pd.DataFrame]`: {表格名：DataFrame}

---

### `extract_from_excel()`

从 Excel 文件提取数据。

**参数：**
- `file_path`: Excel 文件路径
- `sheet_name`: 工作表名称 (可选，默认：第一个)
- `date_col`: 日期列名 (可选)
- `amount_col`: 金额列名 (可选)

**返回：**
- `pd.DataFrame`: 提取的数据

---

### `batch_extract()`

批量解析多个文档。

**参数：**
- `file_list`: 文件路径列表
- `output_dir`: 输出目录 (可选)
- `max_workers`: 最大线程数 (默认：4)

**返回：**
- `List[Dict]`: 提取结果列表

---

## 💡 最佳实践

### 1. 大文件分批处理

```python
# 每 50 个文件一批
for i in range(0, len(files), 50):
    batch = files[i:i+50]
    results = batch_extract(batch)
    save_results(results)
```

### 2. 异常处理

```python
try:
    data = extract_from_pdf('财报.pdf')
except Exception as e:
    log_error(f'提取失败：{e}')
    data = None
```

---

## 🔧 源码目录

```
数据提取组件/
├── extractor.py      # 4,280 行
└── README.md         # 本文档
```

---

*文档自动生成，最后更新：2026-05-05*
