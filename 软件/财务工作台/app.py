"""
财务工作台 v2.0 - 使用 st.navigation() 官方 API
"""
import streamlit as st
import hashlib

st.set_page_config(
    page_title="财务工作台",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

if 'authenticated' not in st.session_state:
    st.session_state.authenticated = False
if 'username' not in st.session_state:
    st.session_state.username = None


def sha256_hash(password: str) -> str:
    return hashlib.sha256(password.encode()).hexdigest()


def check_user(username: str, password: str) -> bool:
    users = {
        'admin': sha256_hash('703102'),
        'finance': sha256_hash('finance123'),
        'intern': sha256_hash('intern123'),
    }
    return username in users and users[username] == sha256_hash(password)


def login():
    st.title("🔐 用户登录")
    col1, col2 = st.columns([1, 2])
    with col1:
        username = st.text_input("用户名")
        password = st.text_input("密码", type="password")
        if st.button("🔑 登录", type="primary", use_container_width=True):
            if check_user(username, password):
                st.session_state.authenticated = True
                st.session_state.username = username
                st.rerun()
            else:
                st.error("用户名或密码错误")
    with col2:
        st.info("**默认账户**\n\n管理员：admin / 703102\n财务专员：finance / finance123\n实习生：intern / intern123")


def logout():
    if st.sidebar.button("🔓 退出登录", use_container_width=True):
        st.session_state.authenticated = False
        st.session_state.username = None
        st.rerun()


def show_home():
    st.title("📊 财务工作台")
    if st.session_state.username:
        st.markdown(f"欢迎回来，**{st.session_state.username}**！")
    st.markdown("---")
    st.markdown("""
### 📋 功能模块

**📝 日常核算** - 发票管理、银行对账、凭证录入等

**📊 财务分析** - 财务比率、杜邦分析、行业对标等

**🏭 数据工厂** - 文档解析、批量解析、数据治理等

**💼 决策支持** - 金融测算、本量利分析、报表美化等

**🧰 办公工具** - 财务日历、快捷工具箱、模板中心等

---
**请从左侧导航栏选择具体功能页面**
""")


def main():
    from utils.database import init_db, create_indexes
    init_db()
    create_indexes()
    
    if not st.session_state.authenticated:
        login()
        return
    
    logout()
    
    # 使用 st.navigation 管理页面导航
    pg = st.navigation(
        [
            st.Page(show_home, title="🏠 首页", icon="🏠"),
            st.Page("pages/10_01_发票管理.py", title="📄 发票管理", icon="📄"),
            st.Page("pages/10_02_银行对账.py", title="🏦 银行对账", icon="🏦"),
            st.Page("pages/10_03_凭证录入.py", title="📝 凭证录入", icon="📝"),
            st.Page("pages/10_04_科目余额表.py", title="📋 科目余额表", icon="📋"),
            st.Page("pages/10_05_应收应付管理.py", title="💰 应收应付管理", icon="💰"),
            st.Page("pages/10_06_纳税申报.py", title="📑 纳税申报", icon="📑"),
            st.Page("pages/20_01_财务比率分析.py", title="📊 财务比率分析", icon="📊"),
            st.Page("pages/20_02_杜邦分析.py", title="🏛️ 杜邦分析", icon="🏛️"),
            st.Page("pages/20_03_行业对标.py", title="🏭 行业对标", icon="🏭"),
            st.Page("pages/20_04_资金诊断.py", title="💵 资金诊断", icon="💵"),
            st.Page("pages/20_05_预算分析.py", title="📈 预算分析", icon="📈"),
            st.Page("pages/20_06_智能透视分析.py", title="🎯 智能透视分析", icon="🎯"),
            st.Page("pages/30_01_文档解析.py", title="📄 文档解析", icon="📄"),
            st.Page("pages/30_02_批量解析.py", title="📄 批量解析", icon="📄"),
            st.Page("pages/30_03_数据治理.py", title="🧹 数据治理", icon="🧹"),
            st.Page("pages/30_04_合规风控.py", title="🛡️ 合规风控", icon="🛡️"),
            st.Page("pages/40_01_金融测算.py", title="🧮 金融测算", icon="🧮"),
            st.Page("pages/40_02_本量利分析.py", title="📊 本量利分析", icon="📊"),
            st.Page("pages/40_03_报表美化.py", title="📑 报表美化", icon="📑"),
            st.Page("pages/50_01_财务日历.py", title="📅 财务日历", icon="📅"),
            st.Page("pages/50_02_快捷工具箱.py", title="🧰 快捷工具箱", icon="🧰"),
            st.Page("pages/50_03_模板中心.py", title="📋 模板中心", icon="📋"),
            st.Page("pages/50_05_增强功能.py", title="🚀 增强功能", icon="🚀"),
            st.Page("pages/50_06_帮助中心.py", title="❓ 帮助中心", icon="❓"),
        ],
        position="sidebar"
    )
    pg.run()


if __name__ == "__main__":
    main()
