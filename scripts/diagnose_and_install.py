import os
import subprocess
import sys
import shutil
import argparse
import urllib.request
import ssl
import json

# ============================================================
# 颜色常量
# ============================================================
class Colors:
    HEADER = '\033[95m'
    BLUE   = '\033[94m'
    GREEN  = '\033[92m'
    YELLOW = '\033[93m'
    RED    = '\033[91m'
    ENDC   = '\033[0m'
    BOLD   = '\033[1m'

def print_step(msg):
    print(f"\n{Colors.YELLOW}{Colors.BOLD}[*] {msg}{Colors.ENDC}")

def print_success(msg):
    print(f"{Colors.GREEN}✔ {msg}{Colors.ENDC}")

def print_warn(msg):
    print(f"{Colors.YELLOW}[!] {msg}{Colors.ENDC}")

def print_error(msg):
    print(f"{Colors.RED}✘ {msg}{Colors.ENDC}")

# ============================================================
# 国内 GitHub 加速代理
# ============================================================
GITHUB_PROXY = "https://ghfast.top/"

# ============================================================
# 全局状态
# ============================================================
IS_CLAWHUB_LOGGED_IN = False
IS_NON_INTERACTIVE   = False

# 国内 npm 加速镜像
CHINA_REGISTRY = "https://registry.npmmirror.com"

# ============================================================
# ClawHub / SkillHub 技能 slug 定义
# ============================================================

# ClawHub 使用的 slug 列表（对应 npx clawhub install <slug>）
CLAWHUB_SLUGS = [
    "skill-vetter",
    "exec-tool",
    "weather-skill",
    "claw-router",
    "channels-setup",
    "self-improving-agent",
    "find-skills",
    "agent-browser",
    "github",
    "skill-creator",
    "cron-mastery",
    "multi-search-engine",
]

# SkillHub 使用的 slug 列表（对应 skillhub install <slug>）
# 注意：SkillHub 是腾讯维护的独立仓库，slug 命名与 ClawHub 不同
# 只列出 SkillHub 实际收录的技能，避免全部失败的问题
SKILLHUB_SLUGS = [
    "exec-tool",
    "claw-router",
    "channels-setup",
    "skill-vetter",
    "find-skills",
    "skill-creator",
]

# ============================================================
# 技能仓库（Git 克隆备选源）
# ============================================================
# 每个条目对应一个独立仓库，确保克隆目标是有效的单一技能仓库
SKILL_STORE = {
    "核心工具 (Core Tools) - [推荐必装]": {
        "exec-tool": {
            "url": "https://github.com/openclaw/exec-tool.git",
            "tag": "main"
        },
        "ClawRouter": {
            "url": "https://github.com/BlockRunAI/ClawRouter.git",
            "tag": "main"
        },
        "channels-setup": {
            "url": "https://github.com/openclaw/channels-setup.git",
            "tag": "main"
        },
    },
    "高级 Agent 扩展 (Advanced Agent Skills)": {
        "Find-Skills": {
            "url": "https://github.com/VoltAgent/awesome-openclaw-skills.git",
            "tag": "main"
        },
    },
    "实用工具与搜索 (Utilities & Search)": {
        "Clawscan": {
            "url": "https://github.com/openclaw/clawscan.git",
            "tag": "main"
        },
        "IM-Master-Skills": {
            "url": "https://github.com/LeoYeAI/openclaw-master-skills.git",
            "tag": "main"
        },
    }
}

# ============================================================
# 1. 环境诊断 (Environment Diagnosis)
# ============================================================
def check_network(host="github.com"):
    print(f"  - 网络连通性 ({host}): ", end="", flush=True)
    try:
        subprocess.check_output(
            ['ping', '-c', '1', '-W', '2', host],
            stderr=subprocess.STDOUT
        )
        print(f"{Colors.GREEN}畅通{Colors.ENDC}")
        return True
    except Exception:
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
        result = subprocess.run(
            ['openclaw', '--version'],
            capture_output=True, text=True
        )
        version = result.stdout.strip().split('\n')[-1]
        if version:
            print(f"{Colors.GREEN}{version}{Colors.ENDC}")
        else:
            print(f"{Colors.RED}无法获取{Colors.ENDC}")
    except Exception:
        print(f"{Colors.RED}未安装或不在 PATH 中{Colors.ENDC}")

def check_clawhub():
    global IS_CLAWHUB_LOGGED_IN
    print(f"  - ClawHub CLI: ", end="", flush=True)
    IS_CLAWHUB_LOGGED_IN = False
    try:
        result = subprocess.run(
            ['npx', 'clawhub', '--cli-version'],
            capture_output=True, text=True, timeout=10
        )
        if result.returncode == 0:
            version = result.stdout.strip().split()[-1]
            login_check = subprocess.run(
                ['npx', 'clawhub', 'whoami'],
                capture_output=True, text=True, timeout=10
            )
            if login_check.returncode == 0:
                print(f"{Colors.GREEN}已登录 ({version}){Colors.ENDC}")
                IS_CLAWHUB_LOGGED_IN = True
            else:
                print(f"{Colors.YELLOW}就绪但未登录 ({version}){Colors.ENDC}")
            return True
        else:
            print(f"{Colors.YELLOW}待部署{Colors.ENDC}")
            return False
    except Exception:
        print(f"{Colors.RED}未检测到 Node.js 或 ClawHub{Colors.ENDC}")
        return False

def check_feishu_tools():
    print(f"  - 飞书官方工具栈: ", end="", flush=True)
    try:
        result = subprocess.run(
            ['npx', '@larksuite/openclaw-lark-tools', '--help'],
            capture_output=True, text=True, timeout=10
        )
        if result.returncode == 0:
            print(f"{Colors.GREEN}发现并可用{Colors.ENDC}")
            return True
        else:
            print(f"{Colors.YELLOW}待部署{Colors.ENDC}")
            return False
    except Exception:
        print(f"{Colors.RED}无法调用 (需 Node.js){Colors.ENDC}")
        return False

def check_skillhub():
    print(f"  - Tencent SkillHub: ", end="", flush=True)
    potential_paths = ['skillhub', os.path.expanduser('~/.local/bin/skillhub')]
    for path in potential_paths:
        try:
            result = subprocess.run(
                [path, '--version'],
                capture_output=True, text=True, timeout=5
            )
            if result.returncode == 0:
                print(f"{Colors.GREEN}已就绪{Colors.ENDC}")
                return True
        except Exception:
            continue
    print(f"{Colors.YELLOW}未发现{Colors.ENDC}")
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
    except Exception:
        print_error("未检测到 Git，请先安装 Git。")
        sys.exit(1)

    # OpenClaw 版本检查
    check_openclaw_version()

    # .env 文件检查（之前遗漏）
    check_env_file()

    # 飞书工具检查
    check_feishu_tools()

    # ClawHub 检查
    check_clawhub()

    # SkillHub 检查
    check_skillhub()

    # 网络检查
    check_network()

    # 权限检查
    check_permissions()

# ============================================================
# 2. 仓库地址验证
# ============================================================
def validate_repository_urls():
    print_step("正在验证 SKILL_STORE 中的仓库地址...")
    all_valid = True

    # 忽略 SSL 验证（国内网络环境下常见的中间代理证书问题）
    ctx = ssl.create_default_context()
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE

    for category, skills in SKILL_STORE.items():
        for name, config in skills.items():
            url = config["url"]
            print(f"  - 检查 {name} ({url}) ... ", end="", flush=True)
            try:
                req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
                with urllib.request.urlopen(req, context=ctx, timeout=8) as response:
                    code = response.getcode()
                    if code == 200:
                        print(f"{Colors.GREEN}有效{Colors.ENDC}")
                    else:
                        print(f"{Colors.YELLOW}状态码 {code}{Colors.ENDC}")
            except Exception as e:
                print(f"{Colors.RED}无效: {str(e)}{Colors.ENDC}")
                all_valid = False

    if not all_valid:
        print_warn("部分仓库地址验证失败，安装时可能会出错。")
    else:
        print_success("所有仓库地址验证通过！")
    return all_valid

# ============================================================
# 3. 飞书插件部署
# ============================================================
def configure_feishu_streaming():
    """配置飞书流式卡片相关选项（在飞书插件安装成功后调用）"""
    print_step("优化飞书流式卡片配置...")
    commands = [
        ['openclaw', 'config', 'set', 'channels.feishu.streaming', 'true'],
        ['openclaw', 'config', 'set', 'channels.feishu.footer.elapsed', 'true'],
        ['openclaw', 'config', 'set', 'channels.feishu.footer.status', 'true'],
    ]
    for cmd in commands:
        print(f"  执行: {' '.join(cmd)} ... ", end="", flush=True)
        try:
            result = subprocess.run(cmd, capture_output=True, text=True)
            if result.returncode == 0:
                print(f"{Colors.GREEN}成功{Colors.ENDC}")
            else:
                print(f"{Colors.YELLOW}忽略 (可能环境未完全就绪){Colors.ENDC}")
        except Exception:
            print(f"{Colors.RED}失败{Colors.ENDC}")

def install_feishu_plugin():
    """
    初始化飞书官方通讯插件。

    修复：
    - 非交互模式或非 TTY 时直接跳过，不再调用任何交互式子进程，
      彻底规避 ERR_USE_AFTER_CLOSE 的 readline 关闭问题。
    - 仅在真正的交互式终端中才启动官方工具。
    """
    print_step("初始化飞书官方通讯插件...")

    # 判断是否应跳过交互
    is_interactive_env = sys.stdin.isatty() and sys.stdout.isatty()

    if IS_NON_INTERACTIVE or not is_interactive_env:
        print_warn("检测到非交互式环境（或已启用 --non-interactive），跳过飞书插件交互式安装。")
        print(f"  {Colors.BLUE}如需安装，请手动执行: npx -y @larksuite/openclaw-lark-tools install{Colors.ENDC}")
        return

    print(f"\n{Colors.BLUE}>>> 提示: 接下来将启动官方飞书工具，如需跳过请 Ctrl+C{Colors.ENDC}")
    try:
        result = subprocess.run(
            ['npx', '-y', '@larksuite/openclaw-lark-tools', 'install'],
            text=True
        )
        if result.returncode == 0:
            print_success("飞书插件部署完成")
            # 安装成功后自动执行流式配置
            configure_feishu_streaming()
        else:
            print_error(f"飞书插件安装退出 (返回码: {result.returncode})")
    except KeyboardInterrupt:
        print(f"\n{Colors.YELLOW}已取消飞书插件安装。{Colors.ENDC}")
    except Exception as e:
        print_error(f"飞书安装异常: {str(e)}")

# ============================================================
# 4. SkillHub 安装（腾讯加速源）
# ============================================================
def install_skillhub_cli():
    """尝试自动安装 SkillHub CLI"""
    print_step("正在自动部署 Tencent SkillHub CLI (国内加速源)...")
    try:
        install_cmd = (
            "curl -fsSL "
            "https://skillhub-1388575217.cos.ap-guangzhou.myqcloud.com/install/install.sh"
            " | bash -s -- --no-skills"
        )
        result = subprocess.run(install_cmd, shell=True, text=True)
        if result.returncode == 0:
            print_success("SkillHub CLI 部署成功")
            local_bin = os.path.expanduser('~/.local/bin')
            if local_bin not in os.environ.get("PATH", ""):
                os.environ["PATH"] = f"{local_bin}:{os.environ['PATH']}"
            return True
        else:
            print_error("SkillHub 部署失败")
            return False
    except Exception as e:
        print_error(f"部署异常: {str(e)}")
        return False

def _get_skillhub_cli():
    """探测系统中可用的 skillhub 可执行路径"""
    potential_paths = ['skillhub', os.path.expanduser('~/.local/bin/skillhub')]
    for p in potential_paths:
        try:
            if subprocess.run([p, '--version'], capture_output=True, timeout=5).returncode == 0:
                return p
        except Exception:
            continue
    return None

def install_via_skillhub():
    """
    通过 Tencent SkillHub 同步核心技能。

    修复：
    - 使用独立的 SKILLHUB_SLUGS 列表（只包含 SkillHub 实际收录的技能），
      避免使用 CLAWHUB_SLUGS 导致全部"跳过 (可能仓库未收录)"。
    - 增加 slug 存在性说明，失败时给出友好提示。
    """
    print_step("通过 Tencent SkillHub 同步核心技能...")
    base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))

    skillhub_path = _get_skillhub_cli()

    if not skillhub_path:
        print_warn("未发现 SkillHub CLI，准备自动安装以开启加速模式...")
        if install_skillhub_cli():
            skillhub_path = _get_skillhub_cli() or os.path.expanduser('~/.local/bin/skillhub')
        else:
            print_warn("SkillHub 安装失败，将跳过此模块（不影响后续 Git 安装流程）。")
            return

    installed_count = 0
    skipped_count  = 0

    for slug in SKILLHUB_SLUGS:
        target_path = os.path.join(base_dir, slug)
        if os.path.exists(target_path):
            print(f"  [已存在] {slug} - 跳过同步")
            skipped_count += 1
            continue

        print(f"  [SkillHub] 正在安装 {slug} ... ", end="", flush=True)
        try:
            result = subprocess.run(
                [skillhub_path, 'install', slug, '--dir', base_dir],
                capture_output=True, text=True, timeout=60
            )
            if result.returncode == 0:
                print(f"{Colors.GREEN}完成{Colors.ENDC}")
                installed_count += 1
            else:
                stderr_lower = (result.stderr or "").lower()
                if "not found" in stderr_lower or "404" in stderr_lower:
                    print(f"{Colors.YELLOW}SkillHub 未收录此技能，将由 Git 补全{Colors.ENDC}")
                else:
                    print(f"{Colors.YELLOW}失败（将由 Git 补全）: {result.stderr.strip()[:80]}{Colors.ENDC}")
        except subprocess.TimeoutExpired:
            print(f"{Colors.YELLOW}超时，将由 Git 补全{Colors.ENDC}")
        except Exception as e:
            print(f"{Colors.RED}异常: {str(e)}{Colors.ENDC}")

    print(f"\n  SkillHub 汇总: 安装 {installed_count} 个，跳过 {skipped_count} 个。")

# ============================================================
# 5. ClawHub 安装（官方源补全）
# ============================================================
def install_via_clawhub():
    """
    通过 ClawHub 尝试同步/更新技能（可选）。

    修复：
    - 使用正确的 CLAWHUB_SLUGS 列表（已在文件顶部定义，不再引用未定义变量）。
    - 失败时静默转入 Git 补全流程，不中断整体安装。
    """
    print_step("通过 ClawHub 尝试同步/更新 (可选)...")
    base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))

    # 自动启用国内镜像
    os.environ["CLAWHUB_REGISTRY"] = CHINA_REGISTRY

    for slug in CLAWHUB_SLUGS:
        target_path = os.path.join(base_dir, slug)

        if os.path.exists(target_path):
            # 已由 SkillHub 或之前步骤安装，跳过
            continue

        print(f"  [ClawHub] 尝试后台拉取 {slug} ... ", end="", flush=True)
        try:
            result = subprocess.run(
                ['npx', '-y', 'clawhub@latest', 'install', slug,
                 '--no-input', '--dir', base_dir],
                capture_output=True, text=True, timeout=60
            )
            if result.returncode == 0:
                print(f"{Colors.GREEN}完成{Colors.ENDC}")
            else:
                print(f"{Colors.BLUE}已转入 Git 补全流程{Colors.ENDC}")
        except subprocess.TimeoutExpired:
            print(f"{Colors.YELLOW}超时，已转入 Git 补全{Colors.ENDC}")
        except Exception:
            print(f"{Colors.BLUE}跳过（将由 Git 补全）{Colors.ENDC}")

# ============================================================
# 6. Git 克隆安装（最终备选）
# ============================================================
def install_skills():
    """
    通过 Git clone 安装 SKILL_STORE 中的技能（最终备选来源）。

    修复：
    - SKILL_STORE 中每个条目现在对应独立的单技能仓库，避免将大型单体仓库
      克隆为错误命名的文件夹。
    - 对已由 ClawHub/SkillHub 安装的 slug 做更精确的跳过判断。
    """
    print_step("同步基础安装包 (Git Pull/Clone)...")
    base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))

    # 收集已由 Hub 安装的技能集合
    hub_installed = set()
    for slug in CLAWHUB_SLUGS + SKILLHUB_SLUGS:
        if os.path.exists(os.path.join(base_dir, slug)):
            hub_installed.add(slug.lower())

    for category, skills in SKILL_STORE.items():
        print(f"\n{Colors.BLUE}{Colors.BOLD}--- {category} ---{Colors.ENDC}")
        for name, config in skills.items():
            target_path = os.path.join(base_dir, name)
            url = config["url"]
            tag = config.get("tag", "main")

            # 检查是否已被 Hub 覆盖（名称匹配任意 slug）
            if any(name.lower() == s or name.lower().replace("-", "") == s.replace("-", "")
                   for s in hub_installed):
                print(f"  [Hub已覆盖] {name}")
                continue

            if os.path.exists(target_path):
                print(f"  [已存在] {name} - 正在拉取更新 ... ", end="", flush=True)
                try:
                    git_env = {**os.environ, "GIT_TERMINAL_PROMPT": "0"}
                    result = subprocess.run(
                        ['git', '-C', target_path, 'pull', 'origin', tag],
                        capture_output=True, text=True, env=git_env, timeout=60
                    )
                    if result.returncode == 0:
                        print(f"{Colors.GREEN}已更新{Colors.ENDC}")
                    else:
                        print(f"{Colors.YELLOW}更新失败 (跳过): {result.stderr.strip()[:60]}{Colors.ENDC}")
                except subprocess.TimeoutExpired:
                    print(f"{Colors.YELLOW}超时，跳过{Colors.ENDC}")
                except Exception as e:
                    print(f"{Colors.YELLOW}异常: {str(e)}{Colors.ENDC}")
            else:
                print(f"  [Git 克隆] {name} ... ", end="", flush=True)
                git_env = {**os.environ, "GIT_TERMINAL_PROMPT": "0"}

                try:
                    # 第一轮：原始地址
                    result = subprocess.run(
                        ['git', 'clone', '-b', tag, '--depth', '1', url, target_path],
                        capture_output=True, text=True, env=git_env, timeout=60
                    )

                    if result.returncode == 0:
                        print(f"{Colors.GREEN}完成{Colors.ENDC}")
                    else:
                        # 第二轮：代理加速
                        print(f"{Colors.YELLOW}重试(代理)... {Colors.ENDC}", end="", flush=True)
                        proxy_url = f"{GITHUB_PROXY}{url}"
                        result_proxy = subprocess.run(
                            ['git', 'clone', '-b', tag, '--depth', '1', proxy_url, target_path],
                            capture_output=True, text=True, env=git_env, timeout=90
                        )

                        if result_proxy.returncode == 0:
                            print(f"{Colors.GREEN}代理同步成功{Colors.ENDC}")
                        else:
                            print(f"{Colors.RED}彻底失败{Colors.ENDC}")
                            stderr = result_proxy.stderr or ""
                            if "Authentication failed" in stderr:
                                print(f"    {Colors.RED}原因: 该仓库可能需要私有权限或 Token{Colors.ENDC}")
                            elif "not found" in stderr.lower() or "does not exist" in stderr.lower():
                                print(f"    {Colors.RED}原因: 仓库不存在或 URL 有误{Colors.ENDC}")
                            else:
                                print(f"    {Colors.RED}详情: {stderr.strip()[:120]}{Colors.ENDC}")

                except subprocess.TimeoutExpired:
                    print(f"{Colors.RED}超时{Colors.ENDC}")
                except Exception as e:
                    print(f"{Colors.RED}克隆异常: {str(e)}{Colors.ENDC}")

# ============================================================
# 7. 交互式配置
# ============================================================
def interactive_config():
    print_step("设置项目配置")
    base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    env_path         = os.path.join(base_dir, ".env")
    env_example_path = os.path.join(base_dir, ".env.example")

    # 修复：使用正确的 sys.stdin.isatty()（原代码错误地使用了 isatatty）
    is_interactive_env = sys.stdin.isatty() and sys.stdout.isatty()

    if IS_NON_INTERACTIVE or not is_interactive_env:
        print_warn("当前环境不支持交互式输入或已启用 --non-interactive，已转为自动生成默认配置。")
        if os.path.exists(env_path):
            print(f"  {Colors.GREEN}.env 文件已存在，保留现有配置。{Colors.ENDC}")
        elif os.path.exists(env_example_path):
            try:
                shutil.copyfile(env_example_path, env_path)
                print_success(f"已根据 .env.example 自动生成初始 .env 文件。")
                print(f"  {Colors.BLUE}请手动编辑: {env_path}{Colors.ENDC}")
            except Exception as e:
                print_error(f"复制配置文件失败: {e}")
        else:
            print_warn(".env.example 也不存在，请手动创建 .env 文件。")
        return

    # 交互模式
    print(f"  （交互模式）")
    if os.path.exists(env_path):
        try:
            choice = input(
                f"  {Colors.YELLOW}[!] .env 文件已存在，是否重新配置？(y/N): {Colors.ENDC}"
            ).strip().lower()
        except EOFError:
            print_warn("输入流已关闭，跳过配置。")
            return
        if choice != 'y':
            print(f"  {Colors.GREEN}跳过配置，保留现有文件。{Colors.ENDC}")
            return

    # 从 .env.example 读取 key
    config_data = {}
    if os.path.exists(env_example_path):
        with open(env_example_path, 'r', encoding='utf-8') as f:
            for line in f:
                if '=' in line and not line.startswith('#'):
                    key = line.split('=')[0].strip()
                    config_data[key] = ""
    else:
        config_data = {
            "FEISHU_APP_ID": "", "FEISHU_APP_SECRET": "",
            "OPENAI_API_KEY": "", "OPENAI_BASE_URL": "https://api.openai.com/v1"
        }

    print(f"\n{Colors.BLUE}>>> 请根据提示输入配置信息 (直接回车可跳过/保持默认):{Colors.ENDC}")
    categories = {
        "FEISHU": "飞书 (Feishu) 配置",
        "OPENAI": "AI (LLM) 配置",
        "MP_":    "公众号推送配置",
    }
    final_config  = []
    current_cat   = ""

    for key in config_data.keys():
        matched_cat = "其他"
        for prefix, title in categories.items():
            if key.startswith(prefix):
                matched_cat = title
                break

        if matched_cat != current_cat:
            print(f"\n  {Colors.BOLD}[ {matched_cat} ]{Colors.ENDC}")
            current_cat = matched_cat

        try:
            val = input(f"  > {key}: ").strip()
        except EOFError:
            print_warn("输入流已关闭，中止配置。")
            break
        final_config.append(f"{key}={val}\n")

    try:
        with open(env_path, 'w', encoding='utf-8') as f:
            f.writelines(final_config)
        print_success(".env 配置文件已生成！")
    except Exception as e:
        print_error(f"写入 .env 失败: {e}")

# ============================================================
# 8. AI 人设配置
# ============================================================
def setup_persona():
    print_step("配置内置 AI 人设 (Persona)")
    personas = [
        {"name": "AI 工程师 (AI Engineer)",
         "path": "engineering/engineering-ai-engineer.md"},
        {"name": "资深前端开发 (Frontend Developer)",
         "path": "engineering/engineering-frontend-developer.md"},
        {"name": "软件架构师 (Software Architect)",
         "path": "engineering/engineering-software-architect.md"},
        {"name": "飞书集成开发专家 (Feishu Integration Developer)",
         "path": "engineering/engineering-feishu-integration-developer.md"},
        {"name": "代码审查专家 (Code Reviewer)",
         "path": "engineering/engineering-code-reviewer.md"},
        {"name": "跳过配置 / Skip", "path": None},
    ]

    for i, p in enumerate(personas):
        print(f"  [{i+1}] {p['name']}")

    if IS_NON_INTERACTIVE or not (sys.stdin.isatty() and sys.stdout.isatty()):
        print_warn("非交互模式：自动跳过人设配置。")
        return

    try:
        choice = input(
            f"\n{Colors.YELLOW}请选择一个内置人设 (1-{len(personas)}): {Colors.ENDC}"
        ).strip()
    except EOFError:
        print_warn("输入流已关闭，跳过人设配置。")
        return

    try:
        idx = int(choice) - 1
        if idx < 0 or idx >= len(personas) or personas[idx]["path"] is None:
            print(f"  {Colors.GREEN}已跳过人设配置。{Colors.ENDC}")
            return

        selected = personas[idx]
        print(f"  正在下载人设: {selected['name']} ... ", end="", flush=True)

        raw_url = (
            f"https://raw.githubusercontent.com/msitarzewski/agency-agents/main/"
            f"{selected['path']}"
        )
        base_dir    = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))
        persona_path = os.path.join(base_dir, "persona.md")

        ctx = ssl.create_default_context()
        ctx.check_hostname = False
        ctx.verify_mode    = ssl.CERT_NONE

        req = urllib.request.Request(raw_url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req, context=ctx, timeout=15) as response:
            content = response.read().decode('utf-8')

        with open(persona_path, 'w', encoding='utf-8') as f:
            f.write(content)

        print(f"{Colors.GREEN}成功{Colors.ENDC}")
        print(f"  {Colors.YELLOW}人设已保存至: {persona_path}{Colors.ENDC}")

    except ValueError:
        print(f"  {Colors.GREEN}输入无效，已跳过人设配置。{Colors.ENDC}")
    except Exception as e:
        print(f"{Colors.RED}获取或保存人设失败: {e}{Colors.ENDC}")

# ============================================================
# 主入口
# ============================================================
def main():
    global IS_NON_INTERACTIVE

    parser = argparse.ArgumentParser(description="OpenClaw 自动配置助手")
    parser.add_argument("--non-interactive", action="store_true",
                        help="启用非交互模式，跳过所有用户输入")
    parser.add_argument("--skip-validation", action="store_true",
                        help="跳过仓库地址验证")
    args = parser.parse_args()

    IS_NON_INTERACTIVE = args.non_interactive

    print(f"{Colors.HEADER}{Colors.BOLD}=======================================")
    print("   OpenClaw 自动配置助手 (傻瓜模式)")
    print(f"======================================={Colors.ENDC}")

    if IS_NON_INTERACTIVE:
        print_warn("正在以非交互模式运行，将使用默认配置。")

    print(f"{Colors.BLUE}本工具将自动完成以下操作：")
    print("1. 诊断环境、配置飞书通道")
    print("2. 自动集成腾讯 SkillHub 加速源 (免登录同步核心技能)")
    print("3. 全量编排核心技能库并进行交互式配置")
    print(f"---------------------------------------{Colors.ENDC}")

    # 0. 环境诊断
    diagnose_env()

    # 1. 验证仓库地址 (可选)
    if not args.skip_validation:
        validate_repository_urls()

    # 2. 飞书官方插件部署（非交互或非 TTY 时自动跳过）
    install_feishu_plugin()

    # 3. 技能安装优先级流
    #    优先 SkillHub（国内加速）→ ClawHub（官方补全）→ Git（最终兜底）
    install_via_skillhub()
    install_via_clawhub()
    install_skills()

    # 4. 交互式配置
    interactive_config()

    # 5. 引导内置人设
    setup_persona()

    print_step("配置任务完成！")
    print("提示: 核心内容已就绪。请查看指南 ./docs/USAGE_GUIDE.md")
    print(f"\n{Colors.GREEN}{Colors.BOLD}🎉 自动化流程执行完毕！{Colors.ENDC}")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print(f"\n{Colors.RED}程序被用户中断。{Colors.ENDC}")
        sys.exit(1)
    except Exception as e:
        print(f"\n{Colors.RED}程序发生非预期错误: {e}{Colors.ENDC}")
        sys.exit(1)
