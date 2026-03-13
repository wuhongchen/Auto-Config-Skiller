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

def check_clawhub():
    print(f"  - ClawHub CLI: ", end="", flush=True)
    try:
        # 尝试通过 npx 运行 clawhub (不带 -y 避免自动安装，只是探测)
        result = subprocess.run(['npx', 'clawhub', '--cli-version'], capture_output=True, text=True, timeout=5)
        if result.returncode == 0:
            version = result.stdout.strip().split()[-1]
            print(f"{Colors.GREEN}已就绪 ({version}){Colors.ENDC}")
            return True
        else:
            print(f"{Colors.YELLOW}未全局安装 (建议通过 npx 使用){Colors.ENDC}")
            return False
    except:
        print(f"{Colors.RED}未检测到 Node.js/npx{Colors.ENDC}")
        return False

def check_feishu_tools():
    print(f"  - 飞书官方工具栈: ", end="", flush=True)
    try:
        # 探测飞书官方工具包
        result = subprocess.run(['npx', '@larksuite/openclaw-lark-tools', '--help'], 
                             capture_output=True, text=True, timeout=5)
        if result.returncode == 0:
            print(f"{Colors.GREEN}发现并可用{Colors.ENDC}")
            return True
        else:
            print(f"{Colors.YELLOW}待部署{Colors.ENDC}")
            return False
    except:
        print(f"{Colors.RED}无法调用 (需 Node.js){Colors.ENDC}")
        return False

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
    
    # 飞书工具检查
    check_feishu_tools()
    
    # ClawHub 检查
    check_clawhub()
    
    # 网络检查
    check_network()
    
    # 权限检查
    check_permissions()
    
    # 配置检查
    check_env_file()

# 2. 技能编排 (Skill Orchestration)
SKILL_STORE = {
    "安全工具 (Security Tools) - [首选必装]": {
        "Skill-Vetter": "https://github.com/kiwi-miwi/skill-vetter.git",
        "Clawscan": "https://github.com/openclaw/clawscan.git"
    },
    "通讯 (Communication)": {
        "IM-Master-Skills": "https://github.com/LeoYeAI/openclaw-master-skills.git"
    },
    "基础工具 (Basic Tools)": {
        "Exec-Tool": "https://github.com/openclaw/exec-tool.git",
        "Web-Search-Tavily": "https://github.com/tavily-ai/tavily-python.git"
    },
    "优化工具 (Optimization Tools)": {
        "ClawRouter": "https://github.com/openclaw/claw-router.git"
    }
}

def install_feishu_plugin():
    print_step("初始化飞书官方通讯插件...")
    print(f"  [飞书] 正在调用官方安装程序 ... ", end="", flush=True)
    try:
        # 该命令会启动交互式安装或诊断修复
        # 注意：此处不使用 --no-input 是因为飞书工具通常需要引导创建机器人
        print(f"\n{Colors.BLUE}>>> 提示: 接下来将启动官方飞书工具，请根据屏幕提示操作 (如需跳过请 Ctrl+C){Colors.ENDC}")
        result = subprocess.run(['npx', '-y', '@larksuite/openclaw-lark-tools', 'install'], 
                             text=True)
        if result.returncode == 0:
            print(f"{Colors.GREEN}飞书插件环境部署完成{Colors.ENDC}")
        else:
            print(f"{Colors.RED}飞书插件安装退出 (code: {result.returncode}){Colors.ENDC}")
    except Exception as e:
        print(f"{Colors.RED}飞书安装异常: {str(e)}{Colors.ENDC}")

# 推荐通过 ClawHub 安装的 Slug (针对官方/核心 Skill)
CLAWHUB_SLUGS = [
    "skill-vetter",
    "exec-tool",
    "weather-skill",
    "market-news-skiller"
]

def install_via_clawhub():
    print_step("尝试通过 ClawHub 安装核心技能...")
    base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))
    
    for slug in CLAWHUB_SLUGS:
        target_path = os.path.join(base_dir, slug)
        if os.path.exists(target_path):
            print(f"  [已存在] {slug} - 跳过")
            continue
            
        print(f"  [ClawHub] 正在安装 {slug} ... ", end="", flush=True)
        try:
            # 使用 npx -y 确保自动下载执行
            # 添加 --no-input 避免交互，--dir 指定安装位置
            result = subprocess.run(['npx', '-y', 'clawhub@latest', 'install', slug, '--no-input', '--dir', base_dir], 
                                 capture_output=True, text=True)
            if result.returncode == 0:
                print(f"{Colors.GREEN}完成{Colors.ENDC}")
            else:
                print(f"{Colors.YELLOW}失败 (可能需登录或网络限制){Colors.ENDC}")
                # print(f"    调试信息: {result.stderr.strip()}")
        except Exception as e:
            print(f"{Colors.RED}异常: {str(e)}{Colors.ENDC}")

def install_skills():
    print_step("开始基础安装包编排 (Git Clone 备选)...")
    
    # 获取 skills 根目录 (假设脚本在 auto-config-skiller/scripts 下)
    base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))
    
    for category, skills in SKILL_STORE.items():
        print(f"\n{Colors.BLUE}{Colors.BOLD}--- {category} ---{Colors.ENDC}")
        for name, url in skills.items():
            target_path = os.path.join(base_dir, name)
            if os.path.exists(target_path):
                print(f"  [已存在] {name} - 跳过")
            else:
                print(f"  [Git 克隆] {name} ... ", end="", flush=True)
                try:
                    # 真正执行克隆
                    result = subprocess.run(['git', 'clone', '--depth', '1', url, target_path], 
                                         capture_output=True, text=True)
                    if result.returncode == 0:
                        print(f"{Colors.GREEN}完成{Colors.ENDC}")
                    else:
                        print(f"{Colors.RED}失败: {result.stderr.strip()}{Colors.ENDC}")
                except Exception as e:
                    print(f"{Colors.RED}异常: {str(e)}{Colors.ENDC}")

def main():
    print(f"{Colors.HEADER}{Colors.BOLD}=======================================")
    print("   OpenClaw 自动配置助手 (诊断 & 分类安装)")
    print(f"======================================={Colors.ENDC}")
    
    diagnose_env()
    
    # 飞书官方插件部署
    install_feishu_plugin()
    
    # 优先使用 ClawHub 安装
    install_via_clawhub()
    
    # 作为补全使用 Git 安装
    install_skills()
    
    print_step("配置引导")
    print("所有工具已编排。请手动检查 .env.example 并配置环境变量。")
    print("提示: 核心 Skill 推荐通过 `npx clawhub login` 登录后获取完整权限。")
    print(f"\n{Colors.GREEN}{Colors.BOLD}🎉 初始化完成！{Colors.ENDC}")

if __name__ == "__main__":
    main()
