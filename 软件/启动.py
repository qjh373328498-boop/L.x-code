# -*- coding: utf-8 -*-
"""
启动文件 - 统一入口
快速启动选中的软件，支持自动内网穿透
"""
import os
import sys
import subprocess
import time
import socket
import webbrowser
import re
from pathlib import Path

# 全局变量：cloudflared 路径（从配置文件同步）
CLOUDFLARED_PATH = None

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
    
    try:
        choice = input(f"{Colors.BOLD}请选择要启动的软件 (0-{len(software_list)}): {Colors.ENDC}").strip()
    except EOFError:
        print(f"\n{Colors.OKBLUE}已退出{Colors.ENDC}")
        return None
    
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
    if os.name == 'nt':
        return str(software_path / "venv" / "Scripts" / "python.exe")
    else:
        return str(software_path / "venv" / "bin" / "python")

def get_cloudflared_path():
    """获取 cloudflared 路径（持久化存储）"""
    global CLOUDFLARED_PATH
    if CLOUDFLARED_PATH:
        return str(CLOUDFLARED_PATH)
    
    software_dir = Path(__file__).parent
    cloudflared_dir = software_dir / ".cloudflared"
    
    # 根据操作系统选择正确的文件名
    if os.name == 'nt':  # Windows
        cloudflared_path = cloudflared_dir / "cloudflared.exe"
    else:  # Linux
        cloudflared_path = cloudflared_dir / "cloudflared"
    
    if cloudflared_path.exists():
        CLOUDFLARED_PATH = cloudflared_path
        return str(cloudflared_path)
    
    # 回退到旧路径（兼容性）
    if os.name == 'nt':
        old_path = Path("/tmp/cloudflared.exe")
    else:
        old_path = Path("/tmp/cloudflared-linux-amd64")
    
    if old_path.exists():
        CLOUDFLARED_PATH = old_path
        return str(old_path)
    
    CLOUDFLARED_PATH = cloudflared_path
    return str(cloudflared_path)

def check_cloudflared_installed():
    """检查 cloudflared 是否已安装"""
    cloudflared_path = Path(get_cloudflared_path())
    return cloudflared_path.exists()

def start_tunnel(port=8501):
    """启动 Cloudflare Tunnel 并返回公网地址"""
    cloudflared_path = Path(get_cloudflared_path())
    
    if not cloudflared_path.exists():
        print(f"{Colors.FAIL}❌ cloudflared 未找到{Colors.ENDC}")
        return None
    
    print(f"\n{Colors.OKBLUE}正在启动 Cloudflare Tunnel...{Colors.ENDC}")
    print(f"{Colors.WARNING}⏳ 首次启动可能需要 20-30 秒，请耐心等待...{Colors.ENDC}\n")
    
    # 停止旧的 tunnel 进程
    if os.name == 'nt':
        subprocess.run(["taskkill", "/F", "/IM", "cloudflared.exe"], 
                       stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    else:
        subprocess.run(["pkill", "-f", "cloudflared"], 
                       stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    time.sleep(2)
    
    # 启动 tunnel
    try:
        cmd = [str(cloudflared_path), "tunnel", "--url", f"http://localhost:{port}", "--protocol", "http2"]
        tunnel_proc = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            bufsize=1
        )
        
        # 等待获取公网地址
        print("正在获取公网地址...")
        start_time = time.time()
        timeout = 60  # 60 秒超时
        
        while True:
            if time.time() - start_time > timeout:
                print(f"{Colors.FAIL}❌ 获取地址超时{Colors.ENDC}")
                tunnel_proc.terminate()
                return None
            
            line = tunnel_proc.stdout.readline()
            if not line:
                if tunnel_proc.poll() is not None:
                    print(f"{Colors.FAIL}❌ Tunnel 进程异常退出{Colors.ENDC}")
                    return None
                time.sleep(0.5)
                continue
            
            # 查找包含 trycloudflare.com 的行
            if "trycloudflare.com" in line and "https://" in line:
                # 提取 URL
                match = re.search(r'https://[^\s|]+\s*trycloudflare\.com', line)
                if match:
                    url = match.group(0).strip()
                    # 清理可能的多余字符
                    url = url.rstrip('│|').strip()
                    print(f"\n{Colors.OKGREEN}✓ Tunnel 启动成功！{Colors.ENDC}")
                    print(f"\n{Colors.BOLD}🌐 公网访问地址：{Colors.OKCYAN}{url}{Colors.ENDC}\n")
                    return url
            
            # 显示进度
            elapsed = int(time.time() - start_time)
            if elapsed % 5 == 0:
                print(f"⏳ 等待中... ({elapsed}秒)", end='\r')
    
    except Exception as e:
        print(f"{Colors.FAIL}❌ 启动失败：{e}{Colors.ENDC}")
        return None

def get_local_ip():
    """获取本机局域网 IP"""
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        local_ip = s.getsockname()[0]
        s.close()
        return local_ip
    except:
        return "192.168.x.x"

def launch_app(software):
    """启动应用"""
    venv_python = get_python_path(software["path"])
    app_path = software["path"] / "app.py"
    
    # 检查虚拟环境
    if not venv_python.exists():
        print(f"\n{Colors.FAIL}❌ 虚拟环境不存在{Colors.ENDC}")
        print(f"\n{Colors.WARNING}⚠️  虚拟环境路径：{venv_python}{Colors.ENDC}")
        print(f"\n请按以下步骤操作：")
        print(f"  1. 打开该软件目录（如：一键财报分析）")
        print(f"  2. 双击运行 一键启动.bat")
        print(f"  3. 或命令行运行：python 配置文件.py")
        print(f"\n{Colors.OKCYAN}按回车键退出...{Colors.ENDC}")
        try:
            input()
        except EOFError:
            pass
        return False
    
    # 检查 app.py
    if not app_path.exists():
        print(f"{Colors.FAIL}❌ 未找到 app.py{Colors.ENDC}")
        print(f"\n{Colors.OKCYAN}按回车键退出...{Colors.ENDC}")
        try:
            input()
        except EOFError:
            pass
        return False
    
    # 启动应用
    print(f"\n{Colors.OKGREEN}✓  正在启动：{software['name']}{Colors.ENDC}")
    print(f"\n{Colors.OKBLUE}━━━ 访问方式（任选其一）━━━{Colors.ENDC}")
    print(f"  {Colors.OKGREEN}[1] 本机访问{Colors.ENDC}      http://localhost:8501")
    print(f"                     （仅限当前电脑使用）")
    print(f"  {Colors.OKGREEN}[2] 局域网访问{Colors.ENDC}    http://{get_local_ip()}:8501")
    print(f"                     （同一 WiFi 下的手机/平板可访问）")
    print(f"  {Colors.OKGREEN}[3] 公网访问{Colors.ENDC}      自动生成公网地址")
    print(f"                     （任何地方都能访问，推荐使用）")
    print(f"\n{Colors.OKCYAN}按 Ctrl+C 停止服务{Colors.ENDC}")
    print(f"{Colors.OKBLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━{Colors.ENDC}\n")
    
    try:
        # 启动 Streamlit 服务
        cmd = f'"{venv_python}" -m streamlit run "{app_path}" --server.headless true --server.address 0.0.0.0 --server.port 8501'
        streamlit_proc = subprocess.Popen(
            cmd, 
            shell=True, 
            stdout=subprocess.DEVNULL, 
            stderr=subprocess.DEVNULL
        )
        
        print("⏳ 等待 Streamlit 服务启动...")
        time.sleep(5)
        print(f"{Colors.OKGREEN}✓ 服务已就绪{Colors.ENDC}\n")
        
        # 选择访问方式
        print("请选择访问方式：")
        print("  [1] 本机访问   （仅限当前电脑）")
        print("  [2] 局域网访问 （同 WiFi 设备）")
        print("  [3] 公网访问   （任何地方，自动配置）")
        
        try:
            choice = input(f"\n{Colors.BOLD}请输入选项 (1-3, 默认 1): {Colors.ENDC}").strip()
        except EOFError:
            choice = "1"
        
        if not choice:
            choice = "1"
        
        # 处理选择
        if choice == "3":
            # 公网访问 - 启动 Cloudflare Tunnel
            if check_cloudflared_installed():
                public_url = start_tunnel(8501)
                if public_url:
                    time.sleep(2)  # 等待 Cloudflare 生效
                    webbrowser.open(public_url)
                    print(f"{Colors.OKGREEN}✓ 已自动打开浏览器{Colors.ENDC}")
                else:
                    print(f"\n{Colors.WARNING}⚠️  公网访问启动失败，降级为本机访问{Colors.ENDC}")
                    webbrowser.open("http://localhost:8501")
                    print(f"{Colors.OKCYAN}提示：请先运行 python 配置文件.py 安装 Cloudflare Tunnel 工具{Colors.ENDC}")
            else:
                print(f"\n{Colors.WARNING}⚠️  未找到 Cloudflare Tunnel 工具{Colors.ENDC}")
                print(f"{Colors.OKCYAN}正在启动本机访问...\n{Colors.ENDC}")
                webbrowser.open("http://localhost:8501")
                print(f"{Colors.FAIL}提示：请运行 python 配置文件.py 下载公网访问工具，然后选择 [3] 公网访问{Colors.ENDC}")
        
        elif choice == "2":
            # 局域网访问
            url = f"http://{get_local_ip()}:8501"
            print(f"\n正在打开：{url}")
            webbrowser.open(url)
            print(f"{Colors.OKGREEN}✓ 已打开浏览器{Colors.ENDC}")
        
        else:
            # 本机访问（默认）
            url = "http://localhost:8501"
            print(f"\n正在打开：{url}")
            webbrowser.open(url)
            print(f"{Colors.OKGREEN}✓ 已打开浏览器{Colors.ENDC}")
        
        print(f"\n{Colors.OKBLUE}━━━ 服务运行中 ━━━{Colors.ENDC}")
        print(f"{Colors.WARNING}按 Ctrl+C 停止服务{Colors.ENDC}")
        print(f"{Colors.OKBLUE}━━━━━━━━━━━━━━━━━━━━━━{Colors.ENDC}\n")
        
        # 等待用户中断
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            print(f"\n{Colors.OKCYAN}应用已停止{Colors.ENDC}")
            
            # 清理 tunnel 进程
            if os.name == 'nt':
                subprocess.run(["taskkill", "/F", "/IM", "cloudflared.exe"], 
                              stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            else:
                subprocess.run(["pkill", "-f", "cloudflared"], 
                              stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            
            return True
            
    except Exception as e:
        print(f"\n{Colors.FAIL}❌ 启动失败：{e}{Colors.ENDC}")
        print(f"\n{Colors.WARNING}可能的原因:{Colors.ENDC}")
        print(f"  1. 虚拟环境未创建：python 配置文件.py")
        print(f"  2. 端口被占用：修改 app.py 中的端口号")
        print(f"  3. 缺少依赖：pip install -r requirements.txt")
        print(f"\n按回车键关闭...")
        try:
            input()
        except EOFError:
            pass
        return False

def main():
    print_header()
    
    software = select_software()
    if not software:
        print(f"\n{Colors.OKCYAN}已退出{Colors.ENDC}")
        try:
            input("按回车键关闭...")
        except EOFError:
            pass
        return
    
    if not software["initialized"]:
        print(f"\n{Colors.WARNING}⚠️  该软件尚未配置{Colors.ENDC}")
        print(f"\n1. 运行配置：python 配置文件.py")
        print(f"2. 或双击：{software['name']} 目录下的 一键启动.bat")
        print(f"\n是否立即配置？")
        choice = input("输入 y 配置，其他取消：").strip().lower()
        if choice == 'y':
            config_script = Path(__file__).parent / "配置文件.py"
            subprocess.run([sys.executable, str(config_script)])
            print(f"\n配置完成后，请重新运行：python 启动.py")
        else:
            print(f"\n{Colors.OKCYAN}已取消{Colors.ENDC}")
        
        try:
            input("按回车键退出...")
        except EOFError:
            pass
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
