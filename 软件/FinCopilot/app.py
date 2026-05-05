"""
FinCopilot - 财务实习生副驾驶
主入口 - 带用户认证
"""
import streamlit as st
import hashlib
from datetime import datetime

# 页面配置
st.set_page_config(
    page_title="FinCopilot",
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
    """
    用户认证
    默认账户：
    - admin / 703102 (管理员)
    - intern / intern123 (实习生)
    """
    users = {
        'admin': sha256_hash('703102'),
        'intern': sha256_hash('intern123'),
    }
    return username in users and users[username] == sha256_hash(password)


def get_user_role(username: str) -> str:
    """获取用户角色"""
    if username == 'admin':
        return 'admin'
    return 'intern'


def login():
    """登录页面"""
    st.title("🔐 FinCopilot 用户登录")
    
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
        
        管理员：
        - 用户名：admin
        - 密码：703102
        
        实习生：
        - 用户名：intern
        - 密码：intern123
        """)


def logout():
    """退出登录"""
    if st.sidebar.button("🔓 退出登录"):
        st.session_state.authenticated = False
        st.session_state.username = None
        st.session_state.role = 'guest'
        st.rerun()


def main():
    """主函数"""
    # 未登录状态
    if not st.session_state.authenticated:
        login()
        return
    
    # 已登录状态
    logout()
    
    # 侧边栏导航
    st.sidebar.title("📊 FinCopilot")
    st.sidebar.markdown(f"👤 {st.session_state.username} | 角色：{st.session_state.role}")
    st.sidebar.markdown("---")
    
    menu = st.sidebar.radio(
        "导航",
        [
            "🏠 首页",
            "📄 文档解析",
            "🧮 金融测算",
            "🧹 数据治理",
            "🛡️ 合规风控",
            "🔗 关联匹配",
            "📊 报表美化",
            "❓ 帮助中心",
        ]
    )
    
    st.sidebar.markdown("---")
    st.sidebar.info("""
    **FinCopilot** v1.0
    
    纯本地、零 API 的财务实习生副驾驶
    
    最后更新：2026-05-05
    """)
    
    # 页面路由
    if menu == "🏠 首页":
        show_home()
    elif menu == "📄 文档解析":
        show_document_parser()
    elif menu == "🧮 金融测算":
        show_financial_calculator()
    elif menu == "🧹 数据治理":
        show_data_governance()
    elif menu == "🛡️ 合规风控":
        show_compliance()
    elif menu == "🔗 关联匹配":
        show_matching()
    elif menu == "📊 报表美化":
        show_report_beautifier()
    elif menu == "❓ 帮助中心":
        show_help()


def show_home():
    """首页"""
    st.title("📊 FinCopilot 财务实习生副驾驶")
    
    st.markdown("""
    ### 功能亮点
    - ✅ **文档解析**：合同/发票/回单关键信息提取
    - ✅ **金融测算**：折旧/IRR/年金计算
    - ✅ **数据治理**：文本聚类清洗
    - ✅ **合规风控**：报销预审/数据脱敏
    - ✅ **关联匹配**：回单 - 发票智能勾稽
    - ✅ **报表美化**：PDF 报告自动生成
    
    ### 核心特性
    - 🔒 **纯本地**：所有数据不离本地
    - 🚫 **零 API**：不依赖任何 AI 接口
    - 💪 **硬核算法**：正则+FuzzyWuzzy+numpy-financial
    
    ### 快速开始
    在左侧菜单选择功能模块开始使用
    """)
    
    # 显示快捷入口
    st.markdown("### ⚡ 快捷入口")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("""
        **📄 文档解析**
        
        上传 PDF/图片，自动提取金额、公司名、日期
        """)
    
    with col2:
        st.markdown("""
        **🧮 金融测算**
        
        直线折旧、双倍余额递减法、IRR/NPV计算
        """)
    
    with col3:
        st.markdown("""
        **🔗 关联匹配**
        
        银行回单与发票智能匹配
        """)


def show_document_parser():
    """文档解析页面"""
    st.title("📄 文档解析")
    st.info("🚧 页面开发中...")
    
    uploaded_file = st.file_uploader(
        "上传 PDF 或图片文件",
        type=["pdf", "png", "jpg", "jpeg"],
        help="支持 PDF、PNG、JPG 格式"
    )
    
    if uploaded_file:
        st.success(f"已上传：{uploaded_file.name}")
        st.markdown("**提取结果**：")
        st.markdown("- 金额：待提取")
        st.markdown("- 公司名：待提取")
        st.markdown("- 日期：待提取")


def show_financial_calculator():
    """金融测算页面"""
    st.title("🧮 金融测算")
    st.info("🚧 页面开发中...")
    
    calc_type = st.selectbox(
        "选择计算类型",
        ["直线折旧", "双倍余额递减法", "IRR 计算", "NPV 计算", "年金计算"]
    )
    
    if calc_type == "直线折旧":
        st.markdown("### 直线折旧计算")
        cost = st.number_input("原值", min_value=0.0)
        salvage = st.number_input("残值", min_value=0.0)
        life = st.number_input("使用年限", min_value=1, step=1)
        
        if st.button("计算"):
            depreciation = (cost - salvage) / life
            st.metric("年折旧额", f"{depreciation:,.2f}")


def show_data_governance():
    """数据治理页面"""
    st.title("🧹 数据治理")
    st.info("🚧 页面开发中...")


def show_compliance():
    """合规风控页面"""
    st.title("🛡️ 合规风控")
    st.info("🚧 页面开发中...")


def show_matching():
    """关联匹配页面"""
    st.title("🔗 关联匹配")
    st.info("🚧 页面开发中...")


def show_report_beautifier():
    """报表美化页面"""
    st.title("📊 报表美化")
    st.info("🚧 页面开发中...")


def show_help():
    """帮助中心"""
    st.title("❓ 帮助中心")
    
    st.markdown("""
    ### 使用说明
    
    **1. 文档解析**
    - 上传 PDF 或图片格式的合同/发票/回单
    - 系统自动提取关键信息（金额、公司名、日期等）
    
    **2. 金融测算**
    - 支持直线折旧、双倍余额递减法
    - 支持 IRR、NPV、年金计算
    
    **3. 数据治理**
    - 上传 CSV 文件
    - 自动聚类相似供应商名称
    
    **4. 合规风控**
    - 报销预审：检查超标、连号
    - 数据脱敏：手机号、身份证掩码
    
    **5. 关联匹配**
    - 上传银行回单和发票 Excel
    - 智能匹配未勾稽项
    
    **6. 报表美化**
    - 生成 PDF 格式报告
    - 包含杜邦分析、优势总结
    
    ### 技术支持
    
    - 纯本地运行，无需联网
    - 不依赖任何 AI API
    - 所有数据保存在本地
    
    ### 默认账户
    
    | 角色 | 用户名 | 密码 |
    |------|--------|------|
    | 管理员 | admin | 703102 |
    | 实习生 | intern | intern123 |
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
