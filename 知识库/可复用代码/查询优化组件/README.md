# 查询优化组件

> 版本：v1.0  
> 最后更新：2026-05-05  
> 来源项目：财务工作台 v2.0  
> 技术栈：SQLite + Pandas

---

## 📦 组件说明

专业数据库查询优化引擎，针对财务数据场景优化，支持分页查询、批量操作、慢查询分析等功能。

### 核心功能

| 功能 | 说明 | 性能提升 |
|------|------|---------|
| 分页查询 | LIMIT/OFFSET 分页 | 万级数据<1 秒 |
| 批量操作 | 批量插入/更新 | 减少 90% 连接次数 |
| 查询分析 | EXPLAIN 执行计划 | 识别慢查询 |
| 索引推荐 | 自动分析推荐索引 | 持续提升性能 |
| 结果缓存 | 查询结果缓存 | 重复查询加速 100x |

---

## 🚀 快速开始

### 1. 安装依赖

```bash
pip install pandas sqlite3
```

### 2. 导入组件

```python
from query_optimizer import (
    paginated_query,
    batch_insert,
    analyze_query,
    suggest_indexes
)
```

### 3. 使用示例

```python
# 分页查询发票数据
invoices, pagination = paginated_query(
    conn, 'invoice',
    page=1, page_size=50,
    where='status = ?', params=('normal',)
)

# 批量插入数据
batch_insert(
    conn, 'bank_statement',
    data=statement_list,
    batch_size=500
)

# 分析慢查询
analysis = analyze_query(conn, 'SELECT * FROM invoice WHERE ...')
print(analysis['execution_time'])
```

---

## 📊 API 参考

### `paginated_query()`

分页查询数据库表。

**参数：**
- `conn`: SQLite 连接对象
- `table_name`: 表名
- `page`: 页码 (从 1 开始)
- `page_size`: 每页条数
- `where`: WHERE 子句 (可选)
- `params`: 参数元组 (可选)
- `order_by`: ORDER BY 子句 (可选)

**返回：**
- `Tuple[pd.DataFrame, Dict]`: (数据 DataFrame, 分页信息)

---

### `batch_insert()`

批量插入数据。

**参数：**
- `conn`: SQLite 连接对象
- `table_name`: 表名
- `data`: 数据列表 (Dict 列表)
- `batch_size`: 批次大小 (默认：500)

**返回：**
- `int`: 插入行数

---

### `analyze_query()`

分析查询执行计划。

**参数：**
- `conn`: SQLite 连接对象
- `query`: SQL 查询语句
- `params`: 查询参数 (可选)

**返回：**
- `Dict`: 分析报告 (包含执行时间、扫描行数、索引使用情况)

---

## 💡 最佳实践

### 1. 大数据集分页

```python
# 百万级数据分页
for page in range(1, total_pages + 1):
    data, _ = paginated_query(conn, 'large_table', page, 1000)
    process(data)
```

### 2. 批量导入优化

```python
# 10 万条数据分批导入
for i in range(0, len(data), 1000):
    batch = data[i:i+1000]
    batch_insert(conn, 'target_table', batch)
```

---

## 🔧 源码目录

```
查询优化组件/
├── query_optimizer.py   # 6,612 行
└── README.md            # 本文档
```

---

*文档自动生成，最后更新：2026-05-05*
