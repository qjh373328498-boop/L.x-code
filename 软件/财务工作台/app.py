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
        'admin': sha256_hash('703102'),
        'finance': sha256_hash('finance123'),
        'intern': sha256_hash('intern123'),
    }
    return username in users and users[username] == sha256_hash(password)


def get_user_role(username: str) -> str:
    """获取用户角色"""
    if username == 'admin':
        return 'admin'
    elif username == 'finance':
        return 'finance'
    return 'intern'


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
        st.session_state.role = 'guest'
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
        **财务分析** - 财务经理、CFO使用，每周/每月
        
        | 功能 | 说明 |
        |------|------|
        | 📊 财务比率分析 | 偿债、盈利、营运能力分析 |
        | 🏛️ 杜邦分析 | 完整杜邦分析法可视化 |
        | 🏭 行业对标 | 4 大行业标准对比分析 |
        | 💵 资金诊断 | 资金流健康度分析 |
        | 📈 预算分析 | 预算编制与执行对比 |
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
        | 📜 历史记录 | 查看之前的计算记录 |
        """)
    
    # 统计信息
    st.markdown("---")
    st.subheader("📈 平台统计")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("功能模块", "22 个")
    with col2:
        st.metric="核心算法"
    with col3:
        st.metric("支持行业", "4 大行业")


def main():
    """主函数"""
    # 主题切换
    theme_switcher()
    
    # 未登录状态
    if not st.session_state.authenticated:
        login()
        return
    
    # 已登录状态
    logout()
    
    # 侧边栏
    st.sidebar.title("📊 财务工作台")
    st.sidebar.markdown(f"👤 {st.session_state.username} | 角色：{st.session_state.role}")
    st.sidebar.markdown("---")
    
    # 主导航
    main_menu = st.sidebar.selectbox(
        "📋 主菜单",
        ["🏠 首页", "📝 日常核算", "📊 财务分析", "🏭 数据工厂", "💼 决策支持", "🧰 办公工具"]
    )
    
    # 子菜单
    if main_menu == "🏠 首页":
        show_dashboard()
    elif main_menu == "📝 日常核算":
        sub_menu = st.sidebar.radio(
            "日常核算",
            ["📄 发票管理", "🏦 银行对账", "📝 凭证录入", "📋 科目余额表", "💰 应收应付管理", "📑 纳税申报"]
        )
        st.sidebar.info("提示：在左侧选择具体功能页面\n\n页面将在主区域打开")
    elif main_menu == "📊 财务分析":
        sub_menu = st.sidebar.radio(
            "财务分析",
            ["📊 财务比率分析", "🏛️ 杜邦分析", "🏭 行业对标", "💵 资金诊断", "📈 预算分析"]
        )
        st.sidebar.info("提示：在左侧选择具体功能页面\n\n页面将在主区域打开")
    elif main_menu == "🏭 数据工厂":
        sub_menu = st.sidebar.radio(
            "数据工厂",
            ["📄 文档解析", "📄 批量解析", "🧹 数据治理", "🛡️ 合规风控"]
        )
        st.sidebar.info("提示：在左侧选择具体功能页面\n\n页面将在主区域打开")
    elif main_menu == "💼 决策支持":
        sub_menu = st.sidebar.radio(
            "决策支持",
            ["🧮 金融测算", "📊 本量利分析", "📑 报表美化"]
        )
        st.sidebar.info("提示：在左侧选择具体功能页面\n\n页面将在主区域打开")
    elif main_menu == "🧰 办公工具":
        sub_menu = st.sidebar.radio(
            "办公工具",
            ["📅 财务日历", "🧰 快捷工具箱", "📋 模板中心", "📜 历史记录"]
        )
        st.sidebar.info("提示：在左侧选择具体功能页面\n\n页面将在主区域打开")
    
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
