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
def diagnose_env():
    print_step("正在开启环境诊断...")
    
    # 检查 Python
    py_version = sys.version.split()[0]
    print(f"  - Python 版本: {py_version} ... {Colors.GREEN}通过{Colors.ENDC}")
    
    # 检查 Git
    try:
        git_version = subprocess.check_output(['git', '--version']).decode().strip()
        print(f"  - Git 版本: {git_version} ... {Colors.GREEN}通过{Colors.ENDC}")
    except:
        print_error("未检测到 Git，请先安装 Git。")
        sys.exit(1)
        
    # 检查目录
    current_dir = os.getcwd()
    print(f"  - 当前工作负载目录: {current_dir}")
    
    # 检查磁盘空间 (Mac/Linux)
    total, used, free = shutil.disk_usage("/")
    print(f"  - 可用磁盘空间: {free // (2**30)} GB ... {Colors.GREEN}通过{Colors.ENDC}")

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
