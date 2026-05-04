# -*- coding: utf-8 -*-
"""
软件启动器 - 交互式菜单
支持：学创杯辅助软件、财务工具箱、一键财报分析
"""
import os
import sys
import subprocess
from pathlib import Path

# 颜色输出
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
    """打印欢迎头"""
    print(f"\n{Colors.HEADER}{'=' * 70}{Colors.ENDC}")
    print(f"{Colors.BOLD}              软件启动器 - 交互式菜单 v2.0{Colors.ENDC}")
    print(f"{Colors.HEADER}{'=' * 70}{Colors.ENDC}\n")
    print(f"{Colors.OKCYAN}提示：如果启动失败，可以直接双击各软件目录下的：一键启动.bat{Colors.ENDC}\n")

def get_software_list():
    """获取可用软件列表"""
    software_dir = Path(__file__).parent
    software_list = []
    
    # 扫描包含 app.py 的目录
    for item in software_dir.iterdir():
        if item.is_dir() and (item / "app.py").exists():
            software_list.append({
                "name": item.name,
                "path": str(item),
                "has_batch": (item / "一键启动.bat").exists()
            })
    
    return sorted(software_list, key=lambda x: x["name"])

def select_software():
    """选择软件"""
    software_list = get_software_list()
    
    if not software_list:
        print(f"{Colors.FAIL}  未找到可用的软件！{Colors.ENDC}")
        return None
    
    print(f"{Colors.OKBLUE}发现 {len(software_list)} 个软件：{Colors.ENDC}")
    print()
    
    for i, software in enumerate(software_list, 1):
        batch_icon = "✅" if software["has_batch"] else "  "
        print(f"  {i}. {software['name']} {batch_icon}")
    
    print(f"  0. 退出")
    print()
    
    choice = input(f"{Colors.BOLD}请输入选项 (0-{len(software_list)}): {Colors.ENDC}").strip()
    
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

def check_and_create_venv(software_path):
    """检查并创建虚拟环境"""
    venv_path = os.path.join(software_path, "venv")
    pyvenv_cfg = os.path.join(venv_path, "pyvenv.cfg")
    
    # Windows 和 Linux 的 python.exe 路径不同
    if os.name == 'nt':  # Windows
        venv_python = os.path.join(venv_path, "Scripts", "python.exe")
    else:  # Linux/Mac
        venv_python = os.path.join(venv_path, "bin", "python")
    
    need_recreate = False
    
    if not os.path.exists(venv_path):
        print(f"  {Colors.WARNING}检测到未创建虚拟环境{Colors.ENDC}")
        need_recreate = True
    elif not (os.path.exists(pyvenv_cfg) and os.path.exists(venv_python)):
        print(f"  {Colors.WARNING}检测到虚拟环境损坏，将重新创建{Colors.ENDC}")
        need_recreate = True
        # 删除损坏的 venv
        try:
            import shutil
            shutil.rmtree(venv_path)
            print(f"  已删除损坏的虚拟环境")
        except Exception as e:
            print(f"  {Colors.FAIL}删除失败的 venv 失败：{e}{Colors.ENDC}")
            print(f"  {Colors.FAIL}请手动删除 venv 目录后重试{Colors.ENDC}")
            return False
    
    if need_recreate:
        print(f"  正在创建虚拟环境...")
        try:
            # 使用当前 Python 版本创建 venv
            subprocess.run([sys.executable, "-m", "venv", venv_path], check=True)
            
            # 验证创建成功
            if os.path.exists(venv_python):
                print(f"  {Colors.OKGREEN}✅ 虚拟环境创建成功{Colors.ENDC}")
                return True
            else:
                print(f"  {Colors.FAIL}❌ 虚拟环境创建失败{Colors.ENDC}")
                return False
                
        except subprocess.CalledProcessError as e:
            print(f"  {Colors.FAIL}❌ 创建虚拟环境失败：{e}{Colors.ENDC}")
            return False
        except Exception as e:
            print(f"  {Colors.FAIL}❌ 未知错误：{e}{Colors.ENDC}")
            return False
    
    return True

def install_requirements(software_path, venv_python):
    """安装依赖"""
    requirements_path = os.path.join(software_path, "requirements.txt")
    
    if not os.path.exists(requirements_path):
        print(f"  {Colors.OKCYAN}未发现 requirements.txt，跳过依赖安装{Colors.ENDC}")
        return True
    
    print(f"  正在检查并安装依赖...")
    
    # 使用清华镜像源加速
    if os.name == 'nt':  # Windows
        cmd = f'"{venv_python}" -m pip install -r "{requirements_path}" -i https://pypi.tuna.tsinghua.edu.cn/simple -q'
    else:
        cmd = f'"{venv_python}" -m pip install -r "{requirements_path}" -i https://pypi.tuna.tsinghua.edu.cn/simple'
    
    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
        if result.returncode == 0:
            print(f"  {Colors.OKGREEN}✅ 依赖安装完成{Colors.ENDC}")
            return True
        else:
            print(f"  {Colors.WARNING}⚠️  依赖安装可能有警告：{result.stderr.strip()[:100]}{Colors.ENDC}")
            return True  # 继续执行
    except Exception as e:
        print(f"  {Colors.FAIL}❌ 依赖安装失败：{e}{Colors.ENDC}")
        return False

def start_app(software_path):
    """启动应用"""
    app_path = os.path.join(software_path, "app.py")
    venv_python = os.path.join(software_path, "venv", "Scripts" if os.name == 'nt' else "bin", "python")
    
    if not os.path.exists(app_path):
        print(f"  {Colors.FAIL}❌ 未找到 app.py{Colors.ENDC}")
        return False
    
    print(f"\n{Colors.OKGREEN}{'=' * 70}{Colors.ENDC}")
    print(f"  正在启动应用...")
    print(f"  路径：{software_path}")
    print(f"\n  {Colors.WARNING}按 Ctrl+C 可停止服务{Colors.ENDC}")
    print(f"{Colors.OKGREEN}{'=' * 70}{Colors.ENDC}\n")
    
    try:
        # 使用 venv 中的 Python 执行
        if os.name == 'nt':  # Windows
            cmd = f'"{venv_python}" "{app_path}"'
        else:  # Linux/Mac
            cmd = f'"{venv_python}" "{app_path}"'
        
        subprocess.run(cmd, shell=True)
        return True
    except KeyboardInterrupt:
        print(f"\n\n{Colors.OKCYAN}应用已停止{Colors.ENDC}")
        return True
    except Exception as e:
        print(f"  {Colors.FAIL}❌ 启动失败：{e}{Colors.ENDC}")
        return False

def main():
    """主函数"""
    print_header()
    
    while True:
        software = select_software()
        
        if software is None:
            print(f"\n{Colors.OKCYAN}感谢使用，再见！{Colors.ENDC}\n")
            break
        
        software_path = software["path"]
        software_name = software["name"]
        
        print(f"\n{Colors.BOLD}准备启动：{software_name}{Colors.ENDC}")
        print()
        
        # 1. 检查虚拟环境
        if not check_and_create_venv(software_path):
            print(f"\n{Colors.FAIL}虚拟环境检查失败，无法继续{Colors.ENDC}")
            continue
        
        # 2. 安装依赖
        venv_python = os.path.join(software_path, "venv", "Scripts" if os.name == 'nt' else "bin", "python")
        if not install_requirements(software_path, venv_python):
            print(f"\n{Colors.WARNING}依赖安装跳过，尝试直接启动...{Colors.ENDC}")
        
        # 3. 启动应用
        if start_app(software_path):
            print(f"\n{Colors.OKCYAN}应用已退出{Colors.ENDC}")
        else:
            print(f"\n{Colors.FAIL}应用启动失败{Colors.ENDC}")
        
        print()
        
        # 询问是否继续
        again = input(f"是否继续启动其他软件？(y/n): ").strip().lower()
        if again != 'y':
            break
    
    print(f"\n{Colors.HEADER}{'=' * 70}{Colors.ENDC}\n")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print(f"\n\n{Colors.OKCYAN}程序已中断{Colors.ENDC}")
    except Exception as e:
        print(f"\n{Colors.FAIL}程序异常退出：{e}{Colors.ENDC}")
        import traceback
        traceback.print_exc()
