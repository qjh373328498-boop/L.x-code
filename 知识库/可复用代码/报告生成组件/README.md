# 报告生成组件

> 版本：v1.0  
> 最后更新：2026-05-05  
> 来源项目：财务工作台 v2.0  
> 技术栈：Jinja2 + XlsxWriter + Plotly

---

## 📦 组件说明

专业财务报告生成引擎，支持财务分析报告、诊断报告、审计报告等多种报告类型的自动生成和导出。

### 核心功能

| 功能 | 说明 | 输出格式 |
|------|------|---------|
| 财务分析报告 | 财务比率分析、趋势分析 | PDF/Word/Excel |
| 诊断报告 | 资金健康度诊断、风险预警 | PDF/HTML |
| 审计报告 | 合规性检查报告 | PDF/Word |
| 可视化图表 | 雷达图、趋势图、仪表盘 | PNG/SVG |
| 批量导出 | 批量生成多份报告 | ZIP 压缩包 |

---

## 🚀 快速开始

### 1. 安装依赖

```bash
pip install jinja2 xlsxwriter plotly pandas
```

### 2. 导入组件

```python
from reporter import (
    generate_analysis_report,
    generate_diagnosis_report,
    export_to_excel,
    batch_generate
)
```

### 3. 使用示例

```python
# 生成财务分析报告
report = generate_analysis_report(
    company_name='ABC 公司',
    ratios=financial_ratios,
    industry_avg=industry_benchmarks,
    output_path='分析报告.pdf'
)

# 生成诊断报告
diagnosis = generate_diagnosis_report(
    cash_flow_data=cash_flow,
    risk_indicators=risk_metrics,
    output_path='诊断报告.pdf'
)
```

---

## 📊 API 参考

### `generate_analysis_report()`

生成财务分析报告。

**参数：**
- `company_name`: 公司名称
- `ratios`: 财务比率字典
- `industry_avg`: 行业平均值
- `output_path`: 输出文件路径

**返回：**
- `str`: 生成的报告路径

---

### `generate_diagnosis_report()`

生成资金诊断报告。

**参数：**
- `cash_flow_data`: 现金流数据
- `risk_indicators`: 风险指标
- `output_path`: 输出文件路径

**返回：**
- `str`: 生成的报告路径

---

## 🔧 源码目录

```
报告生成组件/
├── reporter.py       # 4,600 行
└── README.md         # 本文档
```

---

*文档自动生成，最后更新：2026-05-05*
