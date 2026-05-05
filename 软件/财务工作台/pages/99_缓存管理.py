"""
🛠️ 缓存管理 - 查看和管理系统缓存
"""
import streamlit as st
import psutil
import os
from utils.cache import clear_cache, show_cache_status

from utils.page_helper import init_page

init_page("缓存管理", "🛠️")

st.title("🛠️ 缓存管理")

st.markdown("""
**功能说明**：查看系统缓存状态、内存使用情况，管理缓存数据
""")

# ========== 系统资源监控 ==========
st.subheader("📊 系统资源监控")

process = psutil.Process(os.getpid())
memory_info = process.memory_info()
cpu_percent = psutil.cpu_percent(interval=1)

col1, col2, col3 = st.columns(3)

with col1:
    st.metric(
        label="内存使用",
        value=f"{memory_info.rss / 1024 / 1024:.2f} MB",
        delta=f"{memory_info.rss / 1024 / 1024:.1f} MB"
    )

with col2:
    st.metric(
        label="CPU 使用率",
        value=f"{cpu_percent}%",
        delta=f"{cpu_percent:.1f}%"
    )

with col3:
    st.metric(
        label="缓存策略",
        value="TTL=5 分钟",
        delta="自动清理"
    )

st.progress(min(memory_info.rss / 1024 / 1024 / 512, 1.0))
st.caption("内存使用进度（总限制 512MB）")

# ========== 缓存管理 ==========
st.subheader("📦 缓存管理")

st.info("""
**缓存说明**：
- **数据缓存**：数据库查询结果、计算结果、文件读取
- **资源缓存**：数据库连接、API 客户端
- **TTL**：数据缓存默认 5 分钟自动失效
""")

col1, col2 = st.columns(2)

with col1:
    if st.button("🗑️ 清除数据缓存", use_container_width=True, key="clear_data_cache"):
        clear_cache('data')
        st.success("数据缓存已清除！")
        st.rerun()

with col2:
    if st.button("🗑️ 清除所有缓存", use_container_width=True, key="clear_all_cache"):
        clear_cache('all')
        st.success("所有缓存已清除！")
        st.rerun()

st.divider()

# ========== 缓存统计 ==========
st.subheader("📈 缓存统计")

try:
    cache_stats = st.cache_data.stats()
    if cache_stats:
        st.json({
            "缓存命中率": f"{cache_stats.get('cache_hits', {'count': 0})['count']}",
            "缓存未命中": f"{cache_stats.get('cache_misses', {'count': 0})['count']}",
            "平均命中时间": f"{cache_stats.get('avg_cache_hit_time', 0):.3f} ms",
            "平均未命中时间": f"{cache_stats.get('avg_cache_miss_time', 0):.3f} ms"
        })
    else:
        st.write("暂无缓存统计数据")
except Exception as e:
    st.write(f"无法获取缓存统计：{e}")

st.divider()

# ========== 性能建议 ==========
st.subheader("💡 性能优化建议")

with st.expander("查看性能优化建议"):
    st.markdown("""
    **已实现的优化**：
    - ✅ 数据库连接缓存（`@st.cache_resource`）
    - ✅ 财务数据查询缓存（TTL=300 秒）
    - ✅ 计算结果缓存（永久缓存，数据变化时清除）
    
    **建议**：
    1. 对于频繁访问的数据页面，系统会自动缓存结果
    2. 如果发现数据未更新，可以点击"清除数据缓存"按钮
    3. 大额计算（如杜邦分析、行业对标）会自动缓存计算结果
    
    **最佳实践**：
    - 数据录入后建议清除缓存以确保数据最新
    - 定期清理缓存可以释放内存
    - 缓存会在应用重启后自动重建
    """)
