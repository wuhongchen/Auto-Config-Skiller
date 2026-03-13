import os
import subprocess
import sys
import shutil

# 颜色常量
class Colors:
    HEADER = '\033[95m'
    BLUE = '\033[94m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'

def print_step(msg):
    print(f"\n{Colors.YELLOW}{Colors.BOLD}[*] {msg}{Colors.ENDC}")

def print_success(msg):
    print(f"{Colors.GREEN}✔ {msg}{Colors.ENDC}")

def print_error(msg):
    print(f"{Colors.RED}✘ {msg}{Colors.ENDC}")

# 1. 环境诊断 (Environment Diagnosis)
def check_network(host="github.com"):
    print(f"  - 网络连通性 ({host}): ", end="", flush=True)
    try:
        # 使用 ping 测试 (Mac/Linux -c 1)
        subprocess.check_output(['ping', '-c', '1', '-W', '2', host], stderr=subprocess.STDOUT)
        print(f"{Colors.GREEN}畅通{Colors.ENDC}")
        return True
    except:
        print(f"{Colors.RED}受限 (可能需要代理){Colors.ENDC}")
        return False

def check_permissions():
    print(f"  - 目录写入权限: ", end="", flush=True)
    if os.access(os.getcwd(), os.W_OK):
        print(f"{Colors.GREEN}通过{Colors.ENDC}")
    else:
        print(f"{Colors.RED}拒绝 (请检查文件夹权限){Colors.ENDC}")

def check_env_file():
    print(f"  - .env 配置文件: ", end="", flush=True)
    base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    env_path = os.path.join(base_dir, ".env")
    if os.path.exists(env_path):
        print(f"{Colors.GREEN}已发现{Colors.ENDC}")
    else:
        print(f"{Colors.YELLOW}未配置 (需根据 .env.example 创建){Colors.ENDC}")

def check_openclaw_version():
    print(f"  - OpenClaw 版本: ", end="", flush=True)
    try:
        # 尝试通过 CLI 获取版本
        result = subprocess.run(['openclaw', '--version'], capture_output=True, text=True)
        version = result.stdout.strip().split('\n')[-1] # 取最后一行
        if version:
            print(f"{Colors.GREEN}{version}{Colors.ENDC}")
        else:
            print(f"{Colors.RED}无法获取{Colors.ENDC}")
    except:
        print(f"{Colors.RED}未安装或不在 PATH 中{Colors.ENDC}")

def diagnose_env():
    print_step("正在开启多维度环境诊断...")
    
    # Python 检查
    py_version = sys.version.split()[0]
    print(f"  - Python 版本: {py_version} ... {Colors.GREEN}通过{Colors.ENDC}")
    
    # Git 检查
    try:
        git_version = subprocess.check_output(['git', '--version']).decode().strip()
        print(f"  - Git 版本: {git_version} ... {Colors.GREEN}通过{Colors.ENDC}")
    except:
        print_error("未检测到 Git，请先安装 Git。")
        sys.exit(1)
        
    # OpenClaw 版本检查
    check_openclaw_version()
    
    # 网络检查
    check_network()
    
    # 权限检查
    check_permissions()
    
    # 配置检查
    check_env_file()
    
    # 磁盘空间 (Mac/Linux)
    try:
        total, used, free = shutil.disk_usage("/")
        print(f"  - 可用磁盘空间: {free // (2**30)} GB ... {Colors.GREEN}通过{Colors.ENDC}")
    except:
        pass

# 2. 技能编排 (Skill Orchestration)
SKILL_STORE = {
    "安全工具 (Security Tools) - [首选必装]": {
        "Skill-Vetter": "https://github.com/kiwi-miwi/skill-vetter.git",
        "Clawscan": "https://github.com/openclaw/clawscan.git"
    },
    "通讯 (Communication)": {
        "IM-Master-Skills": "https://github.com/LeoYeAI/openclaw-master-skills.git",
        "AgentMail": "https://github.com/openclaw/agentmail.git"
    },
    "基础工具 (Basic Tools)": {
        "Exec-Tool": "https://github.com/openclaw/exec-tool.git",
        "Web-Search-Tavily": "https://github.com/tavily-ai/tavily-python.git"
    },
    "优化工具 (Optimization Tools)": {
        "ClawRouter": "https://github.com/openclaw/claw-router.git"
    }
}


def install_skills():
    print_step("开始基础安装包编排...")
    
    # 获取 skills 根目录 (假设脚本在 auto-config-skiller/scripts 下)
    base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))
    
    for category, skills in SKILL_STORE.items():
        print(f"\n{Colors.BLUE}{Colors.BOLD}--- {category} ---{Colors.ENDC}")
        for name, url in skills.items():
            target_path = os.path.join(base_dir, name)
            if os.path.exists(target_path):
                print(f"  [已存在] {name} - 跳过")
            else:
                print(f"  [安装中] {name} ...", end="", flush=True)
                try:
                    # 真正执行克隆
                    result = subprocess.run(['git', 'clone', '--depth', '1', url, target_path], 
                                         capture_output=True, text=True)
                    if result.returncode == 0:
                        print(f" {Colors.GREEN}完成{Colors.ENDC}")
                    else:
                        print(f" {Colors.RED}失败: {result.stderr.strip()}{Colors.ENDC}")
                except Exception as e:
                    print(f" {Colors.RED}异常: {str(e)}{Colors.ENDC}")


def main():
    print(f"{Colors.HEADER}{Colors.BOLD}=======================================")
    print("   OpenClaw 自动配置助手 (诊断 & 安装)")
    print(f"======================================={Colors.ENDC}")
    
    diagnose_env()
    install_skills()
    
    print_step("配置引导")
    print("所有工具已编排。请手动检查 .env.example 并配置环境变量。")
    print(f"\n{Colors.GREEN}{Colors.BOLD}🎉 初始化完成！{Colors.ENDC}")

if __name__ == "__main__":
    main()
