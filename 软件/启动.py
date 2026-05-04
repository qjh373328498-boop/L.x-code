# -*- coding: utf-8 -*-
"""
启动文件 - 统一入口
快速启动选中的软件，跳过环境检测
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
    print(f"\n{Colors.OKCYAN}{'=' * 50}{Colors.ENDC}")
    print(f"{Colors.BOLD}       软件启动器{Colors.ENDC}")
    print(f"{Colors.OKCYAN}{'=' * 50}{Colors.ENDC}\n")

def get_software_list():
    """获取可用软件列表"""
    software_dir = Path(__file__).parent
    software_list = []
    
    for item in software_dir.iterdir():
        if item.is_dir() and (item / "app.py").exists():
            initialized = (item / ".initialized").exists()
            software_list.append({
                "name": item.name,
                "path": item,
                "initialized": initialized
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
        icon = "✅" if software["initialized"] else "⚠️"
        print(f"  {i}. {software['name']} {icon}")
    
    print(f"  0. 退出")
    print()
    
    choice = input(f"{Colors.BOLD}请选择要启动的软件 (0-{len(software_list)}): {Colors.ENDC}").strip()
    
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

def get_python_path(software_path):
    """获取虚拟环境中的 Python 路径"""
    if os.name == 'nt':  # Windows
        return software_path / "venv" / "Scripts" / "python.exe"
    else:  # Linux/Mac
        return software_path / "venv" / "bin" / "python"

def launch_app(software):
    """启动应用"""
    venv_python = get_python_path(software["path"])
    app_path = software["path"] / "app.py"
    
    # 检查虚拟环境
    if not venv_python.exists():
        print(f"\n{Colors.FAIL}❌ 虚拟环境不存在{Colors.ENDC}")
        print(f"\n{Colors.WARNING}⚠️  请先运行配置：python 配置文件.py{Colors.ENDC}")
        print(f"\n或者双击：{software['name']} 目录下的 一键启动.bat")
        print(f"\n{Colors.OKCYAN}按回车键退出...{Colors.ENDC}")
        input()
        return False
    
    # 检查 app.py
    if not app_path.exists():
        print(f"{Colors.FAIL}❌ 未找到 app.py{Colors.ENDC}")
        print(f"\n{Colors.OKCYAN}按回车键退出...{Colors.ENDC}")
        input()
        return False
    
    # 启动应用
    print(f"\n{Colors.OKGREEN}  正在启动：{software['name']}{Colors.ENDC}")
    print(f"  地址：http://localhost:8501")
    print(f"  {Colors.OKCYAN}按 Ctrl+C 停止服务{Colors.ENDC}\n")
    
    try:
        if os.name == 'nt':
            cmd = f'"{venv_python}" "{app_path}"'
        else:
            cmd = f'"{venv_python}" "{app_path}"'
        
        # 直接运行，不捕获输出
        subprocess.run(cmd, shell=True)
        
        print(f"\n{Colors.OKCYAN}应用已退出{Colors.ENDC}")
        print(f"按回车键关闭...")
        input()
        return True
        
    except KeyboardInterrupt:
        print(f"\n{Colors.OKCYAN}应用已停止{Colors.ENDC}")
        print(f"按回车键关闭...")
        input()
        return True
    except Exception as e:
        print(f"\n{Colors.FAIL}❌ 启动失败：{e}{Colors.ENDC}")
        print(f"\n{Colors.WARNING}可能的原因:{Colors.ENDC}")
        print(f"  1. 虚拟环境未创建：python 配置文件.py")
        print(f"  2. 缺少依赖：进入软件目录运行 pip install -r requirements.txt")
        print(f"  3. 端口被占用：修改 app.py 中的端口号")
        print(f"\n按回车键关闭...")
        input()
        return False

def main():
    print_header()
    
    software = select_software()
    if not software:
        print(f"\n{Colors.OKCYAN}已退出{Colors.ENDC}")
        input("按回车键关闭...")
        return
    
    if not software["initialized"]:
        print(f"\n{Colors.WARNING}⚠️  该软件尚未配置{Colors.ENDC}")
        print(f"\n1. 运行配置：python 配置文件.py")
        print(f"2. 或双击：{software['name']} 目录下的 一键启动.bat")
        print(f"\n是否立即配置？")
        choice = input("输入 y 配置，其他取消：").strip().lower()
        if choice == 'y':
            # 调用配置文件
            config_script = Path(__file__).parent / "配置文件.py"
            subprocess.run([sys.executable, str(config_script)])
            print(f"\n配置完成后，请重新运行：python 启动.py")
        else:
            print(f"\n{Colors.OKCYAN}已取消{Colors.ENDC}")
        
        input("按回车键退出...")
        return
    
    launch_app(software)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print(f"\n{Colors.OKCYAN}程序已中断{Colors.ENDC}")
    except Exception as e:
        print(f"{Colors.FAIL}异常：{e}{Colors.ENDC}")
        sys.exit(1)
