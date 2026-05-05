# 工具组件库

> 版本：v1.0  
> 最后更新：2026-05-05  
> 来源项目：财务工作台 v2.0

---

## 📦 组件清单

| 组件 | 文件 | 行数 | 复用价值 | 说明 |
|------|------|------|----------|------|
| **常量配置** | `constants.py` | 3,117 | ⭐⭐⭐⭐ | 统一常量定义 |
| **缓存管理** | `cache.py` | 4,088 | ⭐⭐⭐ | Streamlit 缓存封装 |
| **历史记录** | `history_manager.py` | 6,870 | ⭐⭐⭐⭐ | 用户操作历史管理 |
| **导出助手** | `export_helper.py` | 2,934 | ⭐⭐⭐ | 数据导出工具 |

**总计**：17,009 行工具代码

---

## 1. 常量配置 (`constants.py`)

### 功能
- 发票类型定义
- 用户角色常量
- 缓存 TTL 配置
- 默认账户配置
- UI 样式常量

### 使用示例

```python
from constants import InvoiceType, UserRoles, CacheTTL

# 使用发票类型常量
invoice_type = InvoiceType.SPECIAL

# 使用缓存 TTL
@st.cache_data(ttl=CacheTTL.INDUSTRY_DATA)
def get_industry_data():
    ...
```

---

## 2. 缓存管理 (`cache.py`)

### 功能
- Streamlit 缓存装饰器封装
- 缓存清理工具
- 缓存状态监控

### 使用示例

```python
from cache import (
    cached_resource,
    cached_data,
    clear_all_caches,
    get_cache_stats
)

@cached_data(ttl=3600)
def get_data():
    return fetch_from_api()
```

---

## 3. 历史记录 (`history_manager.py`)

### 功能
- 用户操作日志记录
- 历史记录查询
- 历史版本对比

### 使用示例

```python
from history_manager import (
    log_operation,
    get_history,
    compare_versions
)

# 记录操作
log_operation('invoice_add', user_id=1, data=invoice_data)

# 查询历史
history = get_history(
    operation_type='invoice_add',
    limit=50
)
```

---

## 4. 导出助手 (`export_helper.py`)

### 功能
- Excel 导出
- CSV 导出
- 数据格式转换

### 使用示例

```python
from export_helper import (
    export_to_excel,
    export_to_csv,
    format_for_export
)

# 导出 Excel
export_to_excel(
    df,
    'output.xlsx',
    sheet_name='数据'
)
```

---

## 📝 更新日志

| 日期 | 版本 | 更新内容 |
|------|------|----------|
| 2026-05-05 | v1.0 | 初始版本，从财务工作台 v2.0 提取 |

---

*文档自动生成，最后更新：2026-05-05*
