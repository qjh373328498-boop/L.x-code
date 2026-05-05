"""
财务工作台 v2.0 - 使用 st.navigation() 自定义导航
"""
import streamlit as st
import hashlib
from datetime import datetime
from pathlib import Path

# 页面配置
st.set_page_config(
    page_title="财务工作台",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 用户认证初始化
if 'authenticated' not in st.session_state:
    st.session_state.authenticated = False
if 'username' not in st.session_state:
    st.session_state.username = None
if 'role' not in st.session_state:
    st.session_state.role = 'guest'


def sha256_hash(password: str) -> str:
    """SHA256 密码哈希"""
    return hashlib.sha256(password.encode()).hexdigest()


def check_user(username: str, password: str) -> bool:
    """用户认证"""
    users = {
        'admin': sha256_hash('703102'),
        'finance': sha256_hash('finance123'),
        'intern': sha256_hash('intern123'),
    }
    return username in users and users[username] == sha256_hash(password)


def get_user_role(username: str) -> str:
    """获取用户角色"""
    roles = {'admin': 'admin', 'finance': 'finance'}
    return roles.get(username, 'intern')


def login():
    """登录页面"""
    st.title("🔐 财务工作台 - 用户登录")
    col1, col2 = st.columns([1, 2])
    with col1:
        username = st.text_input("用户名", key="login_username")
        password = st.text_input("密码", type="password", key="login_password")
        if st.button("🔑 登录", type="primary", use_container_width=True):
            if check_user(username, password):
                st.session_state.authenticated = True
                st.session_state.username = username
                st.session_state.role = get_user_role(username)
                st.rerun()
            else:
                st.error("用户名或密码错误")
    with col2:
        st.info("**默认账户**\n\n管理员：admin / 703102\n财务专员：finance / finance123\n实习生：intern / intern123")


def logout():
    """退出登录"""
    if st.sidebar.button("🔓 退出登录", use_container_width=True):
        st.session_state.authenticated = False
        st.session_state.username = None
        st.session_state.role = 'guest'
        st.rerun()


def show_dashboard():
    """首页仪表盘"""
    st.title("📊 财务工作台")
    st.markdown(f"欢迎回来，**{st.session_state.username}**！")
    st.markdown("---")
    
    tabs = st.tabs(["📝 日常核算", "📊 财务分析", "🏭 数据工厂", "💼 决策支持", "🧰 办公工具"])
    
    with tabs[0]:
        st.markdown("""
        **日常核算** - 财务会计、出纳使用
        | 功能 | 说明 |
        |------|------|
        | 📄 发票管理 | 发票录入、查询、认证管理 |
        | 🏦 银行对账 | 银行流水与企业账务智能匹配 |
        | 📝 凭证录入 | 会计凭证录入与审核 |
        | 📋 科目余额表 | 科目余额查询与导出 |
        | 💰 应收应付管理 | 往来账款管理与核销 |
        | 📑 纳税申报 | 税费计算与纳税申报 |
        """)
    
    with tabs[1]:
        st.markdown("""
        **财务分析** - 财务经理、CFO 使用
        | 功能 | 说明 |
        |------|------|
        | 📊 财务比率分析 | 偿债、盈利、营运能力分析 |
        | 🏛️ 杜邦分析 | 完整杜邦分析法可视化 |
        | 🏭 行业对标 | 9 大行业标准对比分析 |
        | 💵 资金诊断 | 资金流健康度分析 |
        | 📈 预算分析 | 预算编制与执行对比 |
        | 🎯 智能透视分析 | 多维度数据透视分析 |
        """)
    
    with tabs[2]:
        st.markdown("""
        **数据工厂** - 财务助理、实习生使用
        | 功能 | 说明 |
        |------|------|
        | 📄 文档解析 | PDF/图片提取关键信息 |
        | 📄 批量解析 | 一次上传多个文件批量提取 |
        | 🧹 数据治理 | 供应商名称聚类清洗 |
        | 🛡️ 合规风控 | 报销预审、数据脱敏 |
        """)
    
    with tabs[3]:
        st.markdown("""
        **决策支持** - CFO、投资经理使用
        | 功能 | 说明 |
        |------|------|
        | 🧮 金融测算 | 折旧/IRR/NPV/年金计算 |
        | 📊 本量利分析 | 成本 - 业务量 - 利润分析 |
        | 📑 报表美化 | PDF 报告自动生成 |
        """)
    
    with tabs[4]:
        st.markdown("""
        **办公工具** - 全员使用
        | 功能 | 说明 |
        |------|------|
        | 📅 财务日历 | 重要日期提醒 |
        | 🧰 快捷工具箱 | 计算器/对比/计时器 |
        | 📋 模板中心 | 16 种财务模板下载 |
        | 🚀 增强功能 | 数据导出/导入/备份 |
        | ❓ 帮助中心 | 使用指南与常见问题 |
        """)


def create_nav_pages():
    """创建导航页面结构"""
    pages_dir = Path(__file__).parent / "pages"
    
    sections = {
        "日常核算": [],
        "财务分析": [],
        "数据工厂": [],
        "决策支持": [],
        "办公工具": []
    }
    
    section_map = {
        "10_": "日常核算",
        "20_": "财务分析",
        "30_": "数据工厂",
        "40_": "决策支持",
        "50_": "办公工具"
    }
    
    for page_file in sorted(pages_dir.glob("*.py")):
        filename = page_file.name
        if filename.startswith("00_"):
            continue
        
        for prefix, section in section_map.items():
            if filename.startswith(prefix):
                page_name = filename.replace(".py", "").split("_", 2)[-1].replace("_", " ")
                sections[section].append(st.Page(str(page_file), title=page_name, icon="📄"))
                break
    
    return sections


def main():
    """主函数"""
    from utils.database import init_db, create_indexes
    init_db()
    create_indexes()
    
    if not st.session_state.authenticated:
        login()
        return
    
    logout()
    
    st.sidebar.title("📊 财务工作台")
    st.sidebar.markdown(f"👤 {st.session_state.username} | 角色：{st.session_state.role}")
    st.sidebar.markdown("---")
    
    if st.sidebar.button("🏠 返回首页", use_container_width=True, key="home_btn"):
        st.session_state.current_page = "home"
        st.rerun()
    
    sections = create_nav_pages()
    
    for section_name, pages in sections.items():
        if pages:
            with st.sidebar.expander(f"📁 {section_name}", expanded=False):
                for page in pages:
                    if st.button(f"📄 {page.title}", key=f"nav_{page.title}", use_container_width=True):
                        page.run()
    
    st.sidebar.markdown("---")
    st.sidebar.info("**财务工作台 v2.0**\n\n2026-05-05")
    
    if st.session_state.get('current_page', 'home') == 'home':
        show_dashboard()


if __name__ == "__main__":
    main()
