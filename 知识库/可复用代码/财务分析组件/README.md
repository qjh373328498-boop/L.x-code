# 财务分析可复用代码库

> 版本：v2.0  
> 最后更新：2026-05-05  
> 来源项目：财务工作台 v2.0（整合一键财报分析 v1.1、财务工具箱 v1.5）

---

## 📦 组件清单

| 组件 | 文件 | 行数 | 复用价值 | 说明 |
|------|------|------|----------|------|
| **财务比率计算** | `ratios.py` | 3,949 | ⭐⭐⭐⭐⭐ | 5 大类 15+ 财务指标 |
| **行业标准数据库** | `industry.py` | 14,987 | ⭐⭐⭐⭐⭐ | 8 大行业标准值 |
| **行业标准 2025** | `industry_2025.py` | 13,473 | ⭐⭐⭐⭐⭐ | 2025-2026 权威数据 |
| **财报解析引擎** | `parser.py` | 13,172 | ⭐⭐⭐⭐ | PDF/Excel 财报自动解析 |
| **格式化工具** | `formatters.py` | 1,732 | ⭐⭐⭐ | 货币/百分比/数字格式化 |
| **验证工具** | `validators.py` | 1,903 | ⭐⭐⭐ | 数据验证与表单校验 |
| **数据库工具** | `database.py` | 11,377 | ⭐⭐⭐⭐⭐ | SQLite 数据库管理 (12 张表) |
| **可视化组件** | `visualization.py` | 7,662 | ⭐⭐⭐⭐⭐ | 雷达图/趋势图/仪表盘 |
| **会话管理** | `session_manager.py` | 6,306 | ⭐⭐⭐⭐ | Streamlit 状态管理 |

**总计**：74,561 行可复用代码

---

## 🚀 快速开始

### 1. 安装依赖

```bash
pip install streamlit pandas plotly pdfplumber openpyxl
```

### 2. 导入组件

```python
# 财务计算
from utils.ratios import calculate_profitability_ratios, calculate_solvency_ratios

# 行业对标
from utils.industry import INDUSTRY_STANDARDS, evaluate_ratio

# 可视化
from visualization import create_radar_chart, create_trend_chart

# Session 管理
from session_manager import init_session_state, DataShare
```

### 3. 使用示例

```python
import streamlit as st
from utils.ratios import calculate_all_ratios
from visualization import create_radar_chart

# 初始化
init_session_state({'selected_year': 2024})

# 计算财务比率
ratios = calculate_all_ratios(income_stmt, balance_sheet, cash_flow)

# 绘制雷达图
fig = create_radar_chart(
    metrics=list(ratios.keys()),
    values=list(ratios.values()),
    industry_avg=get_industry_avg('制造业')
)
st.plotly_chart(fig)
```

---

## 📊 核心组件详解

### 1. 财务比率计算 (`ratios.py`)

#### 功能
- **盈利能力**：毛利率、净利率、ROA、ROE
- **偿债能力**：流动比率、速动比率、资产负债率
- **运营效率**：存货周转率、应收账款周转率
- **成长性**：营收增长率、利润增长率
- **现金流**：经营现金流比率、盈利现金比率

#### 使用示例
```python
from utils.ratios import (
    calculate_profitability_ratios,
    calculate_solvency_ratios,
    calculate_efficiency_ratios,
    calculate_growth_ratios
)

# 盈利能力
profit_ratios = calculate_profitability_ratios(income_stmt)
# 输出：{'毛利率': 32.5, '净利率': 12.8, 'ROE': 15.2, ...}

# 偿债能力
solvency_ratios = calculate_solvency_ratios(balance_sheet)

# 运营效率
efficiency_ratios = calculate_efficiency_ratios(income_stmt, balance_sheet)
```

---

### 2. 行业标准数据库 (`industry.py`)

#### 覆盖行业
- 制造业
- 科技/互联网
- 零售业
- 房地产
- 金融业
- 服务业
- 医药行业
- 消费品行业

#### 使用示例
```python
from utils.industry import INDUSTRY_STANDARDS, evaluate_ratio

# 获取制造业标准
standards = INDUSTRY_STANDARDS['制造业']

# 评估财务指标
rating, comment = evaluate_ratio(
    industry='制造业',
    ratio_name='毛利率',
    value=32.5
)
# 输出：('良好', '高于行业平均水平')
```

---

### 3. 财报解析引擎 (`parser.py`)

#### 功能
- 自动识别 Excel/PDF 格式
- 提取三大报表（资产负债表、利润表、现金流量表）
- 会计等式验证
- 数据清洗与标准化

#### 使用示例
```python
from utils.parser import parse_financial_report

# 解析财报
result = parse_financial_report('财报.pdf')

# 访问报表数据
balance_sheet = result['资产负债表']
income_stmt = result['利润表']
cash_flow = result['现金流量表']

# 验证会计等式
assert result['等式验证']['资产负债表平衡']
```

---

### 4. 可视化组件 (`visualization.py`)

#### 图表类型
- **雷达图**：多维能力对比（支持行业对标）
- **趋势图**：折线图/柱状图
- **对比图**：多系列对比
- **仪表盘**：完成度/达标率
- **瀑布图**：财务结构分析

#### 使用示例
```python
from visualization import (
    create_radar_chart,
    create_trend_chart,
    create_gauge_chart
)

# 能力雷达图
fig = create_radar_chart(
    metrics=['盈利能力', '偿债能力', '运营效率', '成长性'],
    values=[85, 70, 90, 75],
    industry_avg=[80, 75, 80, 80]
)
st.plotly_chart(fig)

# 趋势分析
fig = create_trend_chart(df, x_col='年度', y_cols=['营收', '利润'])
st.plotly_chart(fig)
```

---

### 5. 会话管理 (`session_manager.py`)

#### 功能
- Session State 初始化
- 数据缓存（避免重复加载）
- 用户输入持久化
- 跨页面数据共享
- 表单多步骤管理

#### 使用示例
```python
from session_manager import (
    init_session_state,
    get_cached_data,
    DataShare,
    FormManager
)

# 初始化默认值
init_session_state({
    'selected_industry': '制造业',
    'analysis_year': 2024
})

# 缓存数据加载
df = get_cached_data('financial_data', load_expensive_data, ttl=3600)

# 跨页面共享数据
DataShare.set('analysis_result', result)
result = DataShare.get('analysis_result')

# 多步骤表单
form = FormManager('budget_form', total_steps=3)
if st.button("下一步"):
    form.next_step()
```

---

## 🔧 工具函数

### 格式化工具 (`formatters.py`)

```python
from formatters import format_currency, format_percentage, format_number

# 货币格式化
print(format_currency(1234567.89))  # ¥1,234,567.89

# 百分比格式化
print(format_percentage(0.1234))     # 12.34%

# 数字格式化
print(format_number(1234567))       # 1,234,567
```

### 验证工具 (`validators.py`)

```python
from validators import validate_amount, validate_date, validate_required_fields

# 金额验证
assert validate_amount(100.50)

# 日期验证
assert validate_date('2024-01-01')

# 必填字段验证
validate_required_fields(data, ['name', 'amount', 'date'])
```

---

## 📁 数据库工具 (`database.py`)

### 支持的数据库
- SQLite（默认）
- MySQL（可选）
- PostgreSQL（可选）

### 使用示例
```python
from database import (
    get_connection,
    init_db,
    export_to_json,
    import_from_json
)

# 初始化数据库
init_db()

# 导出数据
export_to_json('backup.json')

# 导入数据
import_from_json('backup.json')
```

---

## 🎯 适用场景

| 场景 | 推荐组件 | 节省时间 |
|------|---------|---------|
| **快速搭建财务分析应用** | ratios.py + visualization.py | 4-6 小时 |
| **行业对标分析** | industry.py + ratios.py | 2-3 小时 |
| **财报自动解析** | parser.py | 3-4 小时 |
| **多页面 Streamlit 应用** | session_manager.py | 1-2 小时 |
| **数据持久化** | database.py | 2-3 小时 |

---

## 📝 版本历史

| 版本 | 日期 | 变更内容 |
|------|------|----------|
| v1.0 | 2026-05-04 | 初始版本，整合 3 个项目核心组件 |

---

## 📄 License

MIT © 2026

---

## 🔗 相关文档

- 原始项目：`/workspace/软件/一键财报分析/`
- 原始项目：`/workspace/软件/财务工具箱/`
- 原始项目：`/workspace/软件/学创杯辅助软件/`
