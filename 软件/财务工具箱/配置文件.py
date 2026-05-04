# -*- coding: utf-8 -*-
"""
配置文件 - 首次运行自动安装
用于初始化虚拟环境和安装依赖
"""
import os
import sys
import subprocess
from pathlib import Path

class Colors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'

def print_header():
    print(f"\n{Colors.HEADER}{'=' * 60}{Colors.ENDC}")
    print(f"{Colors.BOLD}        配置文件 - 首次运行初始化{Colors.ENDC}")
    print(f"{Colors.HEADER}{'=' * 60}{Colors.ENDC}\n")

def get_software_dir():
    """获取软件目录路径"""
    return Path(__file__).parent

def check_python():
    """检查 Python 版本"""
    version = sys.version_info
    if version.major < 3 or (version.major == 3 and version.minor < 8):
        print(f"{Colors.FAIL}❌ Python 版本过低，需要 3.8+{Colors.ENDC}")
        print(f"当前版本：{version.major}.{version.minor}.{version.micro}")
        return False
    print(f"{Colors.OKGREEN}✅ Python {version.major}.{version.minor}.{version.micro} 已就绪{Colors.ENDC}")
    return True

def setup_venv():
    """创建虚拟环境"""
    software_dir = get_software_dir()
    venv_path = software_dir / "venv"
    
    if venv_path.exists():
        print(f"{Colors.OKCYAN}ℹ️  虚拟环境已存在，跳过创建{Colors.ENDC}")
        return True
    
    print(f"{Colors.OKBLUE}正在创建虚拟环境...{Colors.ENDC}")
    try:
        subprocess.run([sys.executable, "-m", "venv", str(venv_path)], check=True)
        print(f"{Colors.OKGREEN}✅ 虚拟环境创建成功{Colors.ENDC}")
        return True
    except Exception as e:
        print(f"{Colors.FAIL}❌ 创建失败：{e}{Colors.ENDC}")
        return False

def install_deps():
    """安装依赖"""
    software_dir = get_software_dir()
    requirements = software_dir / "requirements.txt"
    
    if not requirements.exists():
        print(f"{Colors.OKCYAN}ℹ️  无 requirements.txt，跳过{Colors.ENDC}")
        return True
    
    # 确定 pip 路径
    if os.name == 'nt':
        pip_path = software_dir / "venv" / "Scripts" / "pip.exe"
    else:
        pip_path = software_dir / "venv" / "bin" / "pip"
    
    print(f"{Colors.OKBLUE}正在安装依赖（使用清华镜像源）...{Colors.ENDC}")
    
    cmd = [
        str(pip_path),
        "install",
        "-r", str(requirements),
        "-i", "https://pypi.tuna.tsinghua.edu.cn/simple"
    ]
    
    try:
        subprocess.run(cmd, check=True)
        print(f"{Colors.OKGREEN}✅ 依赖安装完成{Colors.ENDC}")
        return True
    except Exception as e:
        print(f"{Colors.WARNING}⚠️  安装警告：{e}{Colors.ENDC}")
        return True

def mark_initialized():
    """标记已初始化"""
    software_dir = get_software_dir()
    marker_file = software_dir / ".initialized"
    marker_file.touch()
    print(f"{Colors.OKGREEN}✅ 初始化完成{Colors.ENDC}")

def main():
    """主函数"""
    print_header()
    
    print(f"{Colors.BOLD}当前目录：{get_software_dir()}{Colors.ENDC}\n")
    
    # 1. 检查 Python
    if not check_python():
        input(f"\n按回车退出...")
        return False
    
    # 2. 创建虚拟环境
    if not setup_venv():
        input(f"\n按回车退出...")
        return False
    
    # 3. 安装依赖
    install_deps()
    
    # 4. 标记已初始化
    mark_initialized()
    
    print(f"\n{Colors.OKGREEN}{'=' * 60}{Colors.ENDC}")
    print(f"{Colors.BOLD}✨ 初始化完成！下次运行请使用：启动.py{Colors.ENDC}")
    print(f"{Colors.OKGREEN}{'=' * 60}{Colors.ENDC}\n")
    
    return True

if __name__ == "__main__":
    try:
        success = main()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print(f"\n{Colors.WARNING}初始化已中断{Colors.ENDC}")
        sys.exit(1)
    except Exception as e:
        print(f"\n{Colors.FAIL}异常：{e}{Colors.ENDC}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
