"""
财务工作台 v2.0 - 手动路由控制（最稳定方案）
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
if 'current_page' not in st.session_state:
    st.session_state.current_page = "首页"


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


def show_home():
    st.title("📊 财务工作台")
    st.markdown(f"欢迎回来，**{st.session_state.username}**！")
    st.markdown("---")
    tabs = st.tabs(["📝 日常核算", "📊 财务分析", "🏭 数据工厂", "💼 决策支持", "🧰 办公工具"])
    with tabs[0]:
        st.markdown("**日常核算**\n\n| 功能 | 说明 |\n|------|------|\n| 📄 发票管理 | 发票录入、查询、认证管理 |\n| 🏦 银行对账 | 银行流水与企业账务智能匹配 |\n| 📝 凭证录入 | 会计凭证录入与审核 |\n| 📋 科目余额表 | 科目余额查询与导出 |\n| 💰 应收应付管理 | 往来账款管理与核销 |\n| 📑 纳税申报 | 税费计算与纳税申报 |")
    with tabs[1]:
        st.markdown("**财务分析**\n\n| 功能 | 说明 |\n|------|------|\n| 📊 财务比率分析 | 偿债、盈利、营运能力分析 |\n| 🏛️ 杜邦分析 | 完整杜邦分析法可视化 |\n| 🏭 行业对标 | 9 大行业标准对比分析 |\n| 💵 资金诊断 | 资金流健康度分析 |\n| 📈 预算分析 | 预算编制与执行对比 |\n| 🎯 智能透视分析 | 多维度数据透视分析 |")
    with tabs[2]:
        st.markdown("**数据工厂**\n\n| 功能 | 说明 |\n|------|------|\n| 📄 文档解析 | PDF/图片提取关键信息 |\n| 📄 批量解析 | 一次上传多个文件批量提取 |\n| 🧹 数据治理 | 供应商名称聚类清洗 |\n| 🛡️ 合规风控 | 报销预审、数据脱敏 |")
    with tabs[3]:
        st.markdown("**决策支持**\n\n| 功能 | 说明 |\n|------|------|\n| 🧮 金融测算 | 折旧/IRR/NPV/年金计算 |\n| 📊 本量利分析 | 成本 - 业务量 - 利润分析 |\n| 📑 报表美化 | PDF 报告自动生成 |")
    with tabs[4]:
        st.markdown("**办公工具**\n\n| 功能 | 说明 |\n|------|------|\n| 📅 财务日历 | 重要日期提醒 |\n| 🧰 快捷工具箱 | 计算器/对比/计时器 |\n| 📋 模板中心 | 16 种财务模板下载 |\n| 🗑️ 缓存管理 | 清理系统缓存和临时文件 |\n| 🚀 增强功能 | 数据导出/导入/备份 |\n| ❓ 帮助中心 | 使用指南与常见问题 |")


def main():
    from utils.database import init_db, create_indexes
    init_db()
    create_indexes()
    
    if not st.session_state.authenticated:
        login()
        return
    
    # 侧边栏
    with st.sidebar:
        st.title("📊 财务工作台")
        
        if st.button("🔓 退出登录", use_container_width=True):
            st.session_state.authenticated = False
            st.session_state.username = None
            st.session_state.current_page = "首页"
            st.rerun()
        
        st.divider()
        
        # 页面路由字典
        PAGES = {
            "首页": show_home,
            "📄 发票管理": lambda: exec(open("pages/10_01_发票管理.py").read(), globals()),
            "🏦 银行对账": lambda: exec(open("pages/10_02_银行对账.py").read(), globals()),
            "📝 凭证录入": lambda: exec(open("pages/10_03_凭证录入.py").read(), globals()),
            "📋 科目余额表": lambda: exec(open("pages/10_04_科目余额表.py").read(), globals()),
            "💰 应收应付管理": lambda: exec(open("pages/10_05_应收应付管理.py").read(), globals()),
            "📑 纳税申报": lambda: exec(open("pages/10_06_纳税申报.py").read(), globals()),
            "📊 财务比率分析": lambda: exec(open("pages/20_01_财务比率分析.py").read(), globals()),
            "🏛️ 杜邦分析": lambda: exec(open("pages/20_02_杜邦分析.py").read(), globals()),
            "🏭 行业对标": lambda: exec(open("pages/20_03_行业对标.py").read(), globals()),
            "💵 资金诊断": lambda: exec(open("pages/20_04_资金诊断.py").read(), globals()),
            "📈 预算分析": lambda: exec(open("pages/20_05_预算分析.py").read(), globals()),
            "🎯 智能透视分析": lambda: exec(open("pages/20_06_智能透视分析.py").read(), globals()),
            "📄 文档解析": lambda: exec(open("pages/30_01_文档解析.py").read(), globals()),
            "📄 批量解析": lambda: exec(open("pages/30_02_批量解析.py").read(), globals()),
            "🧹 数据治理": lambda: exec(open("pages/30_03_数据治理.py").read(), globals()),
            "🛡️ 合规风控": lambda: exec(open("pages/30_04_合规风控.py").read(), globals()),
            "🧮 金融测算": lambda: exec(open("pages/40_01_金融测算.py").read(), globals()),
            "📊 本量利分析": lambda: exec(open("pages/40_02_本量利分析.py").read(), globals()),
            "📑 报表美化": lambda: exec(open("pages/40_03_报表美化.py").read(), globals()),
            "📅 财务日历": lambda: exec(open("pages/50_01_财务日历.py").read(), globals()),
            "🧰 快捷工具箱": lambda: exec(open("pages/50_02_快捷工具箱.py").read(), globals()),
            "📋 模板中心": lambda: exec(open("pages/50_03_模板中心.py").read(), globals()),
            "🗑️ 缓存管理": lambda: exec(open("pages/50_04_缓存管理.py").read(), globals()),
            "🚀 增强功能": lambda: exec(open("pages/50_05_增强功能.py").read(), globals()),
            "❓ 帮助中心": lambda: exec(open("pages/50_06_帮助中心.py").read(), globals()),
        }
        
        # 导航按钮
        if st.button("🏠 首页", use_container_width=True, key="nav_home"):
            st.session_state.current_page = "首页"
            st.rerun()
        
        st.markdown("### 📁 功能模块")
        
        with st.expander("📝 日常核算", expanded=False):
            for name in ["📄 发票管理", "🏦 银行对账", "📝 凭证录入", "📋 科目余额表", "💰 应收应付管理", "📑 纳税申报"]:
                if st.button(name, use_container_width=True, key=f"nav_{name}"):
                    st.session_state.current_page = name
                    st.rerun()
        
        with st.expander("📊 财务分析", expanded=False):
            for name in ["📊 财务比率分析", "🏛️ 杜邦分析", "🏭 行业对标", "💵 资金诊断", "📈 预算分析", "🎯 智能透视分析"]:
                if st.button(name, use_container_width=True, key=f"nav_{name}"):
                    st.session_state.current_page = name
                    st.rerun()
        
        with st.expander("🏭 数据工厂", expanded=False):
            for name in ["📄 文档解析", "📄 批量解析", "🧹 数据治理", "🛡️ 合规风控"]:
                if st.button(name, use_container_width=True, key=f"nav_{name}"):
                    st.session_state.current_page = name
                    st.rerun()
        
        with st.expander("💼 决策支持", expanded=False):
            for name in ["🧮 金融测算", "📊 本量利分析", "📑 报表美化"]:
                if st.button(name, use_container_width=True, key=f"nav_{name}"):
                    st.session_state.current_page = name
                    st.rerun()
        
        with st.expander("🧰 办公工具", expanded=False):
            for name in ["📅 财务日历", "🧰 快捷工具箱", "📋 模板中心", "🗑️ 缓存管理", "🚀 增强功能", "❓ 帮助中心"]:
                if st.button(name, use_container_width=True, key=f"nav_{name}"):
                    st.session_state.current_page = name
                    st.rerun()
        
        st.divider()
        st.info("**财务工作台 v2.0**\n\n2026-05-05")
    
    # 渲染当前页面
    page_func = PAGES.get(st.session_state.current_page)
    if page_func:
        page_func()


if __name__ == "__main__":
    main()
