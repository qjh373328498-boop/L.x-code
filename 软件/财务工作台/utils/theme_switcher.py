"""
FinCopilot - 主题切换工具
"""
import streamlit as st


def set_theme(theme: str = "light"):
    """
    设置主题
    
    参数:
        theme: 'light' 或 'dark'
    """
    st.session_state.theme = theme
    
    # 注入 CSS
    if theme == "dark":
        st.markdown("""
        <style>
        .main {
            background-color: #1e1e1e;
            color: #e0e0e0;
        }
        .stButton>button {
            background-color: #3498db;
            color: white;
        }
        .stTextInput>div>div>input {
            background-color: #2d2d2d;
            color: #e0e0e0;
        }
        </style>
        """, unsafe_allow_html=True)


def theme_switcher():
    """主题切换器"""
    if 'theme' not in st.session_state:
        st.session_state.theme = 'light'
    
    sidebar = st.sidebar
    
    with sidebar:
        theme_choice = st.radio(
            "🎨 主题",
            ["浅色", "深色"],
            index=0 if st.session_state.theme == 'light' else 1
        )
        
        if theme_choice == "浅色":
            set_theme('light')
        else:
            set_theme('dark')
