"""
财务工作台 v2.0
统一财务核算、分析、数据管理的综合平台

整合自：
- 财务工具箱 v1.5（日常核算 + 财务管理）
- FinCopilot v1.0（数据采集 + 专业工具）
"""
import streamlit as st
import hashlib
from datetime import datetime
from utils.constants import UI, DefaultAccounts, Roles

# 页面配置
st.set_page_config(
    page_title="财务工作台",
    page_icon=UI.DEFAULT_ICON,
    layout=UI.DEFAULT_LAYOUT,
    initial_sidebar_state="expanded"
)

# 用户认证初始化
if 'authenticated' not in st.session_state:
    st.session_state.authenticated = False
if 'username' not in st.session_state:
    st.session_state.username = None
if 'role' not in st.session_state:
    st.session_state.role = 'guest'


# ========== 用户认证 ==========#
def sha256_hash(password: str) -> str:
    """SHA256 密码哈希"""
    return hashlib.sha256(password.encode()).hexdigest()


def check_user(username: str, password: str) -> bool:
    """
    用户认证
    默认账户：
    - admin / 703102 (管理员)
    - finance / finance123 (财务专员)
    - intern / intern123 (实习生)
    """
    users = {
        DefaultAccounts.ADMIN['username']: sha256_hash(DefaultAccounts.ADMIN['password']),
        DefaultAccounts.FINANCE['username']: sha256_hash(DefaultAccounts.FINANCE['password']),
        DefaultAccounts.INTERN['username']: sha256_hash(DefaultAccounts.INTERN['password']),
    }
    return username in users and users[username] == sha256_hash(password)


def get_user_role(username: str) -> str:
    """获取用户角色"""
    if username == DefaultAccounts.ADMIN['username']:
        return Roles.ADMIN
    elif username == DefaultAccounts.FINANCE['username']:
        return Roles.FINANCE
    return Roles.INTERN


def login():
    """登录页面"""
    st.title("🔐 财务工作台 - 用户登录")
    
    col1, col2 = st.columns([1, 2])
    with col1:
        username = st.text_input("用户名", key="login_username")
        password = st.text_input("密码", type="password", key="login_password")
        
        if st.button("登录", type="primary", use_container_width=True):
            if check_user(username, password):
                st.session_state.authenticated = True
                st.session_state.username = username
                st.session_state.role = get_user_role(username)
                st.rerun()
            else:
                st.error("用户名或密码错误")
    
    with col2:
        st.info("""
        💡 **默认账户**
        
        **管理员**：
        - 用户名：admin
        - 密码：703102
        - 权限：全部功能
        
        **财务专员**：
        - 用户名：finance
        - 密码：finance123
        - 权限：日常核算 + 财务分析
        
        **实习生**：
        - 用户名：intern
        - 密码：intern123
        - 权限：基础功能
        """)


def logout():
    """退出登录"""
    if st.sidebar.button("🔓 退出登录"):
        st.session_state.authenticated = False
        st.session_state.username = None
        st.session_state.role = Roles.GUEST
        st.rerun()


# ========== 主题切换 ==========#
def set_theme(theme: str = "light"):
    """设置主题"""
    st.session_state.theme = theme
    
    if theme == "dark":
        st.markdown("""
        <style>
        .main { background-color: #1e1e1e; color: #e0e0e0; }
        .stButton>button { background-color: #3498db; color: white; }
        .stTextInput>div>div>input { background-color: #2d2d2d; color: #e0e0e0; }
        </style>
        """, unsafe_allow_html=True)


def theme_switcher():
    """主题切换器"""
    if 'theme' not in st.session_state:
        st.session_state.theme = 'light'
    
    with st.sidebar:
        theme_choice = st.radio(
            "🎨 主题",
            ["浅色", "深色"],
            index=0 if st.session_state.theme == 'light' else 1
        )
        
        if theme_choice == "浅色":
            set_theme('light')
        else:
            set_theme('dark')


# ========== 主函数 ==========#
def show_dashboard():
    """首页仪表盘"""
    st.title("📊 财务工作台")
    st.markdown(f"欢迎回来，**{st.session_state.username}**！角色：{st.session_state.role}")
    st.markdown("---")
    
    # 快捷入口
    st.subheader("⚡ 快捷入口")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown("""
        ### 📝 发票管理
        发票录入、查询、认证
        
        [前往 →](?page=invoice)
        """)
    
    with col2:
        st.markdown("""
        ### 🏦 银行对账
        银行流水与企业账务匹配
        
        [前往 →](?page=bank)
        """)
    
    with col3:
        st.markdown("""
        ### 📊 财务分析
        比率分析、杜邦分析、行业对标
        
        [前往 →](?page=analysis)
        """)
    
    with col4:
        st.markdown("""
        ### 🏭 文档解析
        PDF/图片批量提取
        
        [前往 →](?page=ocr)
        """)
    
    # 功能模块导航
    st.markdown("---")
    st.subheader("📋 功能模块")
    
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "📝 日常核算",
        "📊 财务分析",
        "🏭 数据工厂",
        "💼 决策支持",
        "🧰 办公工具"
    ])
    
    with tab1:
        st.markdown("""
        **日常核算** - 财务会计、出纳使用，每天
        
        | 功能 | 说明 |
        |------|------|
        | 📄 发票管理 | 发票录入、查询、认证管理 |
        | 🏦 银行对账 | 银行流水与企业账务智能匹配 |
        | 📝 凭证录入 | 会计凭证录入与审核 |
        | 📋 科目余额表 | 科目余额查询与导出 |
        | 💰 应收应付管理 | 往来账款管理与核销 |
        | 📑 纳税申报 | 税费计算与纳税申报 |
        """)
    
    with tab2:
        st.markdown("""
        **财务分析** - 财务经理、CFO 使用，每周/每月
        
        | 功能 | 说明 |
        |------|------|
        | 📊 财务比率分析 | 偿债、盈利、营运能力分析 |
        | 🏛️ 杜邦分析 | 完整杜邦分析法可视化 |
        | 🏭 行业对标 | 9 大行业标准对比分析（2025 权威数据） |
        | 💵 资金诊断 | 资金流健康度分析 |
        | 📈 预算分析 | 预算编制与执行对比 |
        | 🎯 智能透视分析 | 多维度数据透视分析 |
        """)
    
    with tab3:
        st.markdown("""
        **数据工厂** - 财务助理、实习生使用，按需
        
        | 功能 | 说明 |
        |------|------|
        | 📄 文档解析 | PDF/图片提取关键信息 |
        | 📄 批量解析 | 一次上传多个文件批量提取 |
        | 🧹 数据治理 | 供应商名称聚类清洗 |
        | 🛡️ 合规风控 | 报销预审、数据脱敏 |
        """)
    
    with tab4:
        st.markdown("""
        **决策支持** - CFO、投资经理使用，按需
        
        | 功能 | 说明 |
        |------|------|
        | 🧮 金融测算 | 折旧/IRR/NPV/年金计算 |
        | 📊 本量利分析 | 成本 - 业务量 - 利润分析 |
        | 📑 报表美化 | PDF 报告自动生成 |
        """)
    
    with tab5:
        st.markdown("""
        **办公工具** - 全员使用，每天
        
        | 功能 | 说明 |
        |------|------|
        | 📅 财务日历 | 重要日期提醒 |
        | 🧰 快捷工具箱 | 计算器/对比/计时器 |
        | 📋 模板中心 | 16 种财务模板下载 |
        | 🚀 增强功能 | 数据导出/导入/备份/高级分析 |
        | ❓ 帮助中心 | 使用指南与常见问题 |
        """)
    
    # 统计信息
    st.markdown("---")
    st.subheader("📈 平台统计")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("功能模块", "25 个")
    with col2:
        st.metric("核心算法", "15 个")
    with col3:
        st.metric("支持行业", "9 大行业")


def main():
    """主函数"""
    # 初始化数据库和索引
    from utils.database import init_db, create_indexes
    init_db()
    create_indexes()  # 创建数据库索引，优化查询性能
    
    # 主题切换
    theme_switcher()
    
    # 未登录状态
    if not st.session_state.authenticated:
        login()
        return
    
    # 已登录状态
    logout()
    
    # 侧边栏导航 - 折叠菜单风格
    st.sidebar.title("📊 财务工作台")
    st.sidebar.markdown(f"👤 {st.session_state.username} | 角色：{st.session_state.role}")
    st.sidebar.markdown("---")
    
    # 使用 expander 实现折叠菜单效果
    if st.sidebar.button("🏠 返回首页", use_container_width=True):
        st.switch_page("app.py")
    
    st.sidebar.markdown("### 📁 功能模块")
    
    # 模块 1: 日常核算
    with st.sidebar.expander("📝 日常核算", expanded=False):
        if st.button("📄 发票管理", key="nav_invoice", use_container_width=True):
            st.switch_page("pages/10_01_发票管理.py")
        if st.button("🏦 银行对账", key="nav_bank", use_container_width=True):
            st.switch_page("pages/10_02_银行对账.py")
        if st.button("📝 凭证录入", key="nav_voucher", use_container_width=True):
            st.switch_page("pages/10_03_凭证录入.py")
        if st.button("📋 科目余额表", key="nav_balance", use_container_width=True):
            st.switch_page("pages/10_04_科目余额表.py")
        if st.button("💰 应收应付管理", key="nav_arap", use_container_width=True):
            st.switch_page("pages/10_05_应收应付管理.py")
        if st.button("📑 纳税申报", key="nav_tax", use_container_width=True):
            st.switch_page("pages/10_06_纳税申报.py")
    
    # 模块 2: 财务分析
    with st.sidebar.expander("📊 财务分析", expanded=False):
        if st.button("📊 财务比率分析", key="nav_ratios", use_container_width=True):
            st.switch_page("pages/20_01_财务比率分析.py")
        if st.button("🏛️ 杜邦分析", key="nav_dupont", use_container_width=True):
            st.switch_page("pages/20_02_杜邦分析.py")
        if st.button("🏭 行业对标", key="nav_industry", use_container_width=True):
            st.switch_page("pages/20_03_行业对标.py")
        if st.button("💵 资金诊断", key="nav_cashflow", use_container_width=True):
            st.switch_page("pages/20_04_资金诊断.py")
        if st.button("📈 预算分析", key="nav_budget", use_container_width=True):
            st.switch_page("pages/20_05_预算分析.py")
        if st.button("🎯 智能透视分析", key="nav_pivot", use_container_width=True):
            st.switch_page("pages/20_06_智能透视分析.py")
    
    # 模块 3: 数据工厂
    with st.sidebar.expander("🏭 数据工厂", expanded=False):
        if st.button("📄 文档解析", key="nav_docparse", use_container_width=True):
            st.switch_page("pages/30_01_文档解析.py")
        if st.button("📄 批量解析", key="nav_batch", use_container_width=True):
            st.switch_page("pages/30_02_批量解析.py")
        if st.button("🧹 数据治理", key="nav_governance", use_container_width=True):
            st.switch_page("pages/30_03_数据治理.py")
        if st.button("🛡️ 合规风控", key="nav_compliance", use_container_width=True):
            st.switch_page("pages/30_04_合规风控.py")
    
    # 模块 4: 决策支持
    with st.sidebar.expander("💼 决策支持", expanded=False):
        if st.button("🧮 金融测算", key="nav_finance", use_container_width=True):
            st.switch_page("pages/40_01_金融测算.py")
        if st.button("📊 本量利分析", key="nav_cvp", use_container_width=True):
            st.switch_page("pages/40_02_本量利分析.py")
        if st.button("📑 报表美化", key="nav_beautify", use_container_width=True):
            st.switch_page("pages/40_03_报表美化.py")
    
    # 模块 5: 办公工具
    with st.sidebar.expander("🧰 办公工具", expanded=False):
        if st.button("📅 财务日历", key="nav_calendar", use_container_width=True):
            st.switch_page("pages/50_01_财务日历.py")
        if st.button("🧰 快捷工具箱", key="nav_tools", use_container_width=True):
            st.switch_page("pages/50_02_快捷工具箱.py")
        if st.button("📋 模板中心", key="nav_template", use_container_width=True):
            st.switch_page("pages/50_03_模板中心.py")
        if st.button("🚀 增强功能", key="nav_enhanced", use_container_width=True):
            st.switch_page("pages/50_05_增强功能.py")
        if st.button("❓ 帮助中心", key="nav_help", use_container_width=True):
            st.switch_page("pages/50_06_帮助中心.py")
    
    # 侧边栏底部信息
    st.sidebar.markdown("---")
    st.sidebar.info("""
    **财务工作台 v2.0**
    
    整合自：
    - 财务工具箱 v1.5
    - FinCopilot v1.0
    
    最后更新：2026-05-05
    """)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        st.warning("程序已中断")
    except Exception as e:
        st.error(f"异常：{e}")
        import traceback
        traceback.print_exc()
