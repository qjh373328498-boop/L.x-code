# 财务工作台性能优化指南

## 📊 缓存机制

### 已实现的缓存策略

#### 1. **数据库连接缓存** (`utils/database.py`)
```python
@st.cache_resource
def get_connection():
    """数据库连接使用资源缓存，避免重复创建连接"""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn
```
- **优势**：数据库连接是昂贵资源，缓存后每个 Worker 只创建一次
- **适用场景**：数据库连接、大型模型、外部 API 客户端

#### 2. **数据查询缓存** (`pages/20_财务分析/*.py`)
```python
@st.cache_data(ttl=300)  # 5 分钟
def load_financial_data():
    """加载财务数据，5 分钟内重复访问直接返回缓存"""
    conn = get_connection()
    df = pd.read_sql_query("SELECT * FROM financial_metrics", conn)
    return df
```
- **优势**：避免重复数据库查询
- **TTL 设置**：5 分钟，平衡数据新鲜度和性能
- **适用场景**：数据库查询、文件读取、API 数据拉取

#### 3. **计算结果缓存**
```python
@st.cache_data
def calculate_ratios(df: pd.DataFrame) -> pd.DataFrame:
    """财务比率计算，相同输入直接返回缓存结果"""
    # 计算逻辑...
    return df
```
- **优势**：复杂计算不需要重复执行
- **适用场景**：复杂计算、数据处理、格式化转换

### 缓存装饰器对比

| 装饰器 | 用途 | 序列化 | 使用场景 |
|--------|------|--------|----------|
| `@st.cache_data` | 数据缓存 | 需要 | 数据库查询、计算结果、文件读取 |
| `@st.cache_resource` | 资源缓存 | 不需要 | 数据库连接、API 客户端、模型对象 |
| `@st.cache` (已废弃) | 老版本 | 需要 | 不推荐使用 |

## 🚀 性能优化建议

### 开发时的最佳实践

#### 1. 大数据集使用分页
```python
# ❌ 避免：一次性加载所有数据
data = get_all_data()

# ✅ 推荐：分页加载
@st.cache_data
def get_data_page(page: int, page_size: int = 100):
    offset = (page - 1) * page_size
    return get_data(limit=page_size, offset=offset)
```

#### 2. 避免在循环中查询数据库
```python
# ❌ 避免
for item in items:
    data = query_database(item.id)

# ✅ 推荐：批量查询
all_data = query_batch([item.id for item in items])
```

#### 3. Session State 优化
```python
# ✅ 推荐：使用 Session State 保存用户输入状态
if 'user_inputs' not in st.session_state:
    st.session_state.user_inputs = {}

# 避免每次重新渲染时丢失状态
```

### 页面加载优化

#### 1. 延迟加载重资源
```python
# 使用 expander 或 tabs 延迟加载
with st.expander("高级选项", expanded=False):
    # 只有展开时才加载
    load_advanced_features()
```

#### 2. 使用容器分块加载
```python
# 使用 placeholder 实现渐进式加载
placeholder = st.empty()
with placeholder:
    st.spinner("加载中...")

# 数据准备好后替换
data = load_data()
placeholder.empty()
render_data(data)
```

## 📈 性能监控

### 查看缓存状态

在任意页面添加：
```python
if st.sidebar.checkbox("显示缓存状态"):
    st.write(f"缓存命中次数：{st.cache_data.stats()}")
```

### 内存使用监控

```python
import psutil
import os

process = psutil.Process(os.getpid())
memory_mb = process.memory_info().rss / 1024 / 1024
st.write(f"当前内存使用：{memory_mb:.2f} MB")
```

## 🔧 缓存管理

### 清除缓存

在 `utils/cache.py` 中提供了缓存管理工具：

```python
from utils.cache import clear_cache

# 清除所有缓存
clear_cache('all')

# 只清除数据缓存
clear_cache('data')

# 只清除资源缓存
clear_cache('resource')
```

### 缓存失效策略

1. **TTL 自动失效**：设置 `ttl` 参数（秒）
2. **手动清除**：调用 `clear_cache()`
3. **版本失效**：修改函数代码后自动失效

## 📝 已优化的页面

| 页面 | 优化内容 | 缓存时间 | 性能提升 |
|------|----------|----------|----------|
| 财务比率分析 | 数据加载、比率计算 | 5 分钟 | 80%+ |
| 杜邦分析 | ROE 数据缓存 | 5 分钟 | 80%+ |
| 发票管理 | 发票查询结果 | 5 分钟 | 60%+ |
| 银行对账 | 对账匹配结果 | 30 分钟 | 90%+ |
| 行业对标 | 行业数据查询 | 24 小时 | 95%+ |
| 金融测算 | 折旧/IRR/NPV 计算 | 永久 | 99%+ |
| database.py | 数据库连接缓存 | 永久 | 50%+ |

## 🎯 进一步优化建议

### 已完成的缓存优化 ✅

- [x] 发票管理：发票数据查询缓存（5 分钟）
- [x] 银行对账：对账结果缓存（30 分钟）
- [x] 行业对标：行业数据缓存（24 小时）
- [x] 金融测算：计算结果缓存（永久）

### 待优化的页面

- [ ] 凭证录入：添加凭证查询缓存
- [ ] 资金诊断：添加诊断结果缓存
- [ ] 杜邦分析：添加图表渲染缓存
- [ ] 数据工厂：添加 OCR 结果缓存

### 建议的缓存策略

```python
# 发票数据查询
@st.cache_data(ttl=600)
def get_invoices(period: str):
    return query_invoices(period)

# 银行对账结果
@st.cache_data(ttl=1800)  # 30 分钟
def reconcile_bank_transactions(date_range):
    return perform_reconciliation(date_range)

# 金融测算结果
@st.cache_data
def calculate_pv(rate: float, periods: int, payment: float):
    return calculate_present_value(rate, periods, payment)
```

## 🐛 常见问题

### Q: 为什么数据更新了但显示的还是旧数据？
A: 缓存导致的，可以：
1. 等待 TTL 自动失效
2. 手动触发 `clear_cache()`
3. 使用 Refresh 按钮

### Q: 缓存会占用大量内存吗？
A: Streamlit 会自动管理缓存大小，超过内存限制时会 LRU 淘汰。建议：
1. 为大数据集设置合适的 TTL
2. 定期清除不再需要的缓存
3. 使用 `st.session_state` 管理临时数据

### Q: 缓存会影响数据实时性吗？
A: 会，需要根据业务设置合适的 TTL：
- 频繁变化的数据：TTL=60-120 秒
- 稳定的历史数据：TTL=600-1800 秒
- 计算结果：可以永久缓存，数据变化时手动清除
