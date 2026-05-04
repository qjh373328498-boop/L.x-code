# -*- coding: utf-8 -*-
"""
配置文件 - 统一入口
首次运行自动选择软件、创建虚拟环境、安装依赖
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

def get_software_list():
    """获取可用软件列表"""
    software_dir = Path(__file__).parent
    software_list = []
    
    for item in software_dir.iterdir():
        if item.is_dir() and (item / "app.py").exists():
            software_list.append({
                "name": item.name,
                "path": item,
                "has_requirements": (item / "requirements.txt").exists()
            })
    
    return sorted(software_list, key=lambda x: x["name"])

def select_software():
    """选择软件"""
    software_list = get_software_list()
    
    if not software_list:
        print(f"{Colors.FAIL}❌ 未找到可用的软件{Colors.ENDC}")
        return None
    
    print(f"{Colors.OKBLUE}发现 {len(software_list)} 个软件：{Colors.ENDC}\n")
    
    for i, software in enumerate(software_list, 1):
        req_icon = "📦" if software["has_requirements"] else "  "
        print(f"  {i}. {software['name']} {req_icon}")
    
    print(f"  0. 退出")
    print()
    
    choice = input(f"{Colors.BOLD}请选择要配置的软件 (0-{len(software_list)}): {Colors.ENDC}").strip()
    
    if choice == "0":
        return None
    
    try:
        index = int(choice) - 1
        if 0 <= index < len(software_list):
            return software_list[index]
        else:
            print(f"{Colors.FAIL}无效的选项！{Colors.ENDC}")
            return None
    except ValueError:
        print(f"{Colors.FAIL}请输入数字！{Colors.ENDC}")
        return None

def check_python():
    """检查 Python 版本"""
    version = sys.version_info
    if version.major < 3 or (version.major == 3 and version.minor < 8):
        print(f"{Colors.FAIL}❌ Python 版本过低，需要 3.8+{Colors.ENDC}")
        print(f"当前版本：{version.major}.{version.minor}.{version.micro}")
        return False
    print(f"{Colors.OKGREEN}✅ Python {version.major}.{version.minor}.{version.micro} 已就绪{Colors.ENDC}")
    return True

def setup_venv(software_path):
    """创建虚拟环境"""
    venv_path = software_path / "venv"
    
    if venv_path.exists():
        print(f"  {Colors.OKCYAN}ℹ️  虚拟环境已存在，跳过创建{Colors.ENDC}")
        return True
    
    print(f"  {Colors.OKBLUE}正在创建虚拟环境...{Colors.ENDC}")
    try:
        subprocess.run([sys.executable, "-m", "venv", str(venv_path)], check=True)
        print(f"  {Colors.OKGREEN}✅ 虚拟环境创建成功{Colors.ENDC}")
        return True
    except Exception as e:
        print(f"  {Colors.FAIL}❌ 创建失败：{e}{Colors.ENDC}")
        return False

def install_deps(software_path):
    """安装依赖"""
    requirements = software_path / "requirements.txt"
    
    if not requirements.exists():
        print(f"  {Colors.OKCYAN}ℹ️  无 requirements.txt，跳过{Colors.ENDC}")
        return True
    
    # 确定 pip 路径
    if os.name == 'nt':
        pip_path = software_path / "venv" / "Scripts" / "pip.exe"
    else:
        pip_path = software_path / "venv" / "bin" / "pip"
    
    print(f"  {Colors.OKBLUE}正在安装依赖（使用清华镜像源）...{Colors.ENDC}")
    
    cmd = [
        str(pip_path),
        "install",
        "-r", str(requirements),
        "-i", "https://pypi.tuna.tsinghua.edu.cn/simple"
    ]
    
    try:
        subprocess.run(cmd, check=True)
        print(f"  {Colors.OKGREEN}✅ 依赖安装完成{Colors.ENDC}")
        return True
    except Exception as e:
        print(f"  {Colors.WARNING}⚠️  安装警告：{e}{Colors.ENDC}")
        return True

def mark_initialized(software_path):
    """标记已初始化"""
    marker_file = software_path / ".initialized"
    marker_file.touch()
    print(f"\n{Colors.OKGREEN}✅ {software_path.name} 初始化完成{Colors.ENDC}")

def main():
    """主函数"""
    print_header()
    
    # 1. 检查 Python
    if not check_python():
        input(f"\n按回车退出...")
        return False
    
    # 2. 选择软件
    software = select_software()
    if not software:
        print(f"\n{Colors.OKCYAN}已退出{Colors.ENDC}")
        return False
    
    print(f"\n{Colors.BOLD}正在配置：{software['name']}{Colors.ENDC}")
    print(f"路径：{software['path']}\n")
    
    # 3. 创建虚拟环境
    if not setup_venv(software["path"]):
        input(f"\n按回车退出...")
        return False
    
    # 4. 安装依赖
    install_deps(software["path"])
    
    # 5. 标记已初始化
    mark_initialized(software["path"])
    
    print(f"\n{Colors.OKGREEN}{'=' * 60}{Colors.ENDC}")
    print(f"{Colors.BOLD}✨ 配置完成！下次启动请使用：启动.py{Colors.ENDC}")
    print(f"     或双击：{software['name']} 目录下的 一键启动.bat{Colors.ENDC}")
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
