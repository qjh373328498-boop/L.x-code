"""
缓存管理 - 清理系统缓存和临时数据
"""
import streamlit as st
import os
import shutil
import glob

st.title("🗑️ 缓存管理")

st.markdown("管理并清理系统缓存、临时文件和上传的文件。")

# ========== 缓存统计 ==========
st.subheader("📊 缓存统计")

# 检查缓存目录
cache_dirs = {
    "Streamlit 缓存": os.path.expanduser("~/.streamlit/cache"),
    "临时文件": "/tmp/streamlit*",
    "上传文件": "data/uploads",
}

col1, col2, col3 = st.columns(3)

# 计算 Streamlit 缓存大小
streamlit_cache_size = 0
cache_dir = os.path.expanduser("~/.streamlit/cache")
if os.path.exists(cache_dir):
    for dirpath, dirnames, filenames in os.walk(cache_dir):
        for f in filenames:
            fp = os.path.join(dirpath, f)
            if os.path.exists(fp):
                streamlit_cache_size += os.path.getsize(fp)

col1.metric("Streamlit 缓存", f"{streamlit_cache_size / 1024 / 1024:.2f} MB")

# 计算上传文件大小
upload_size = 0
upload_dir = "data/uploads"
if os.path.exists(upload_dir):
    for dirpath, dirnames, filenames in os.walk(upload_dir):
        for f in filenames:
            fp = os.path.join(dirpath, f)
            if os.path.exists(fp):
                upload_size += os.path.getsize(fp)

col2.metric("上传文件", f"{upload_size / 1024 / 1024:.2f} MB")

# 计算数据库大小
db_size = 0
for db_file in glob.glob("data/*.db"):
    if os.path.exists(db_file):
        db_size += os.path.getsize(db_file)

col3.metric("数据库", f"{db_size / 1024 / 1024:.2f} MB")

st.divider()

# ========== 清理选项 ==========
st.subheader("🧹 清理选项")

clear_cache = st.checkbox("清理 Streamlit 缓存（不影响数据）", value=True)
clear_uploads = st.checkbox("清理上传的临时文件", value=False)
clear_db = st.checkbox("重置数据库（⚠️ 将删除所有业务数据）", value=False)

if st.button("🗑️ 执行清理", type="primary"):
    cleared = []
    
    if clear_cache:
        if os.path.exists(cache_dir):
            shutil.rmtree(cache_dir)
            cleared.append("Streamlit 缓存")
    
    if clear_uploads:
        if os.path.exists(upload_dir):
            shutil.rmtree(upload_dir)
            os.makedirs(upload_dir, exist_ok=True)
            cleared.append("上传文件")
    
    if clear_db:
        for db_file in glob.glob("data/*.db"):
            if os.path.exists(db_file):
                os.remove(db_file)
                cleared.append("数据库")
        st.warning("数据库已重置，页面将在 3 秒后刷新")
        st.rerun()
    
    if cleared:
        st.success(f"已清理：{'、'.join(cleared)}")
        st.rerun()
    else:
        st.warning("未选择任何清理项")

st.divider()

# ========== 上传文件列表 ==========
st.subheader("📁 上传文件管理")

if os.path.exists(upload_dir):
    files = []
    for dirpath, dirnames, filenames in os.walk(upload_dir):
        for f in filenames:
            fp = os.path.join(dirpath, f)
            if os.path.exists(fp):
                size = os.path.getsize(fp)
                files.append({"文件名": f, "大小": f"{size / 1024:.1f} KB", "路径": fp})
    
    if files:
        df_files = st.dataframe(
            files,
            use_container_width=True,
            column_config={"路径": st.column_config.TextColumn("路径", disabled=True, width="large")}
        )
        
        # 批量删除
        selected_files = st.multiselect("选择要删除的文件", [f["文件名"] for f in files])
        if selected_files and st.button("删除选中文件", type="primary"):
            for f in files:
                if f["文件名"] in selected_files:
                    os.remove(f["路径"])
            st.success(f"已删除 {len(selected_files)} 个文件")
            st.rerun()
    else:
        st.info("暂无上传文件")
else:
    st.info("上传目录不存在")
