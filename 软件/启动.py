# -*- coding: utf-8 -*-
"""
启动文件 - 快速启动应用
跳过环境检测和依赖安装
"""
import os
import sys
import subprocess
from pathlib import Path

class Colors:
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'

def get_python_path():
    """获取虚拟环境中的 Python 路径"""
    software_dir = Path(__file__).parent
    
    if os.name == 'nt':  # Windows
        return software_dir / "venv" / "Scripts" / "python.exe"
    else:  # Linux/Mac
        return software_dir / "venv" / "bin" / "python"

def main():
    software_dir = Path(__file__).parent
    venv_python = get_python_path()
    app_path = software_dir / "app.py"
    
    # 检查虚拟环境
    if not venv_python.exists():
        print(f"{Colors.FAIL}❌ 虚拟环境不存在{Colors.ENDC}")
        print(f"\n请先运行：配置文件.py")
        print(f"或双击：一键启动.bat\n")
        input("按回车退出...")
        return False
    
    # 检查 app.py
    if not app_path.exists():
        print(f"{Colors.FAIL}❌ 未找到 app.py{Colors.ENDC}")
        input("按回车退出...")
        return False
    
    # 启动应用
    print(f"\n{Colors.OKCYAN}{'=' * 50}{Colors.ENDC}")
    print(f"{Colors.BOLD}  正在启动应用...{Colors.ENDC}")
    print(f"  地址：http://localhost:8501")
    print(f"  按 Ctrl+C 停止服务")
    print(f"{Colors.OKCYAN}{'=' * 50}{Colors.ENDC}\n")
    
    try:
        if os.name == 'nt':
            cmd = f'"{venv_python}" "{app_path}"'
        else:
            cmd = f'"{venv_python}" "{app_path}"'
        
        subprocess.run(cmd, shell=True)
        return True
        
    except KeyboardInterrupt:
        print(f"\n{Colors.OKCYAN}应用已停止{Colors.ENDC}")
        return True
    except Exception as e:
        print(f"{Colors.FAIL}❌ 启动失败：{e}{Colors.ENDC}")
        return False

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print(f"\n{Colors.OKCYAN}程序已中断{Colors.ENDC}")
    except Exception as e:
        print(f"{Colors.FAIL}异常：{e}{Colors.ENDC}")
        sys.exit(1)
