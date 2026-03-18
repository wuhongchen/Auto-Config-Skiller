#!/usr/bin/env python3
import argparse
import os
import select
import shutil
import ssl
import subprocess
import sys
import tarfile
import tempfile
import urllib.request
from urllib.parse import urlparse
from typing import Optional, Tuple

# ============================================================
# 路径常量
# ============================================================
SCRIPT_DIR = os.path.abspath(os.path.dirname(__file__))
PROJECT_ROOT = os.path.abspath(os.path.join(SCRIPT_DIR, ".."))

# ============================================================
# 颜色常量
# ============================================================
class Colors:
    HEADER = "\033[95m"
    BLUE = "\033[94m"
    GREEN = "\033[92m"
    YELLOW = "\033[93m"
    RED = "\033[91m"
    ENDC = "\033[0m"
    BOLD = "\033[1m"


def print_step(msg: str) -> None:
    print(f"\n{Colors.YELLOW}{Colors.BOLD}[*] {msg}{Colors.ENDC}")


def print_success(msg: str) -> None:
    print(f"{Colors.GREEN}✔ {msg}{Colors.ENDC}")


def print_warn(msg: str) -> None:
    print(f"{Colors.YELLOW}[!] {msg}{Colors.ENDC}")


def print_error(msg: str) -> None:
    print(f"{Colors.RED}✘ {msg}{Colors.ENDC}")


# ============================================================
# 常量与全局状态
# ============================================================
GITHUB_PROXY = "https://ghfast.top/"
CHINA_REGISTRY = "https://registry.npmmirror.com"
IS_GITHUB_ACCESSIBLE = True
IS_CLAWHUB_REGISTRY_ACCESSIBLE = True
IS_SKILLHUB_INSTALLER_ACCESSIBLE = True

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
SKILLHUB_SLUGS = [
    "exec-tool",
    "claw-router",
    "channels-setup",
    "skill-vetter",
    "find-skills",
    "skill-creator",
]

# 技能仓库（Git 兜底源）
SKILL_STORE = {
    "核心工具 (Core Tools) - [推荐必装]": {
        "claw-router": {
            "url": "https://github.com/BlockRunAI/ClawRouter.git",
            "tag": "main",
        }
    },
    "高级 Agent 扩展 (Advanced Agent Skills)": {
        "find-skills": {
            "url": "https://github.com/VoltAgent/awesome-openclaw-skills.git",
            "tag": "main",
        }
    },
    "实用工具与搜索 (Utilities & Search)": {
        "im-master-skills": {
            "url": "https://github.com/LeoYeAI/openclaw-master-skills.git",
            "tag": "main",
        }
    },
}

PERSONAS = [
    {"name": "AI 工程师 (AI Engineer)", "path": "engineering/engineering-ai-engineer.md"},
    {
        "name": "资深前端开发 (Frontend Developer)",
        "path": "engineering/engineering-frontend-developer.md",
    },
    {
        "name": "软件架构师 (Software Architect)",
        "path": "engineering/engineering-software-architect.md",
    },
    {
        "name": "飞书集成开发专家 (Feishu Integration Developer)",
        "path": "engineering/engineering-feishu-integration-developer.md",
    },
    {"name": "代码审查专家 (Code Reviewer)", "path": "engineering/engineering-code-reviewer.md"},
]


def _build_ssl_context() -> ssl.SSLContext:
    ctx = ssl.create_default_context()
    # 国内网络环境下常见中间代理证书问题，保持与原脚本一致的兼容策略
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE
    return ctx


class DryRunResult:
    returncode = 0
    stdout = ""
    stderr = ""


def run_command(
    cmd,
    *,
    capture_output: bool = True,
    timeout: Optional[int] = None,
    text: bool = True,
    shell: bool = False,
    env: Optional[dict] = None,
    dry_run: bool = False,
):
    if dry_run:
        preview = cmd if isinstance(cmd, str) else " ".join(cmd)
        print(f"    [dry-run] {preview}")
        return DryRunResult()

    return subprocess.run(
        cmd,
        capture_output=capture_output,
        timeout=timeout,
        text=text,
        shell=shell,
        env=env,
    )


def detect_openclaw_command() -> Optional[str]:
    for cmd in ("openclaw", "claw"):
        if shutil.which(cmd):
            return cmd
    return None


def resolve_skills_dir(override_dir: Optional[str]) -> Tuple[str, str]:
    candidates = []
    if override_dir:
        candidates.append((os.path.abspath(override_dir), "--skills-dir"))

    env_skills = os.environ.get("OPENCLAW_SKILLS_DIR")
    if env_skills:
        candidates.append((os.path.abspath(env_skills), "OPENCLAW_SKILLS_DIR"))

    env_workspace = os.environ.get("OPENCLAW_WORKSPACE")
    if env_workspace:
        candidates.append((os.path.join(os.path.abspath(env_workspace), "skills"), "OPENCLAW_WORKSPACE"))

    layout_parent = os.path.abspath(os.path.join(PROJECT_ROOT, ".."))
    if os.path.basename(layout_parent) == "skills":
        candidates.append((layout_parent, "repo-layout"))

    cwd_skills = os.path.join(os.getcwd(), "skills")
    if os.path.isdir(cwd_skills):
        candidates.append((cwd_skills, "cwd/skills"))

    if not candidates:
        # 非 OpenClaw 标准目录结构时，保守回落到当前项目目录，避免写到项目外。
        candidates.append((PROJECT_ROOT, "project-root"))

    selected_path, source = candidates[0]
    os.makedirs(selected_path, exist_ok=True)
    return selected_path, source


def resolve_workspace_dir(skills_dir: str) -> str:
    env_workspace = os.environ.get("OPENCLAW_WORKSPACE")
    if env_workspace:
        return os.path.abspath(env_workspace)

    skills_dir_abs = os.path.abspath(skills_dir)
    if os.path.basename(skills_dir_abs) == "skills":
        return os.path.dirname(skills_dir_abs)

    cwd = os.path.abspath(os.getcwd())
    if os.path.isdir(os.path.join(cwd, "skills")):
        return cwd

    return PROJECT_ROOT


def ensure_env_template(workspace_dir: str, dry_run: bool = False) -> None:
    target_env = os.path.join(workspace_dir, ".env")
    if os.path.exists(target_env):
        return

    candidates = [
        os.path.join(workspace_dir, ".env.example"),
        os.path.join(PROJECT_ROOT, ".env.example"),
    ]
    source = next((path for path in candidates if os.path.exists(path)), None)
    if not source:
        return

    if dry_run:
        print(f"    [dry-run] copy {source} -> {target_env}")
        return

    shutil.copyfile(source, target_env)
    print_success(f"已自动生成 .env 模板: {target_env}")


def check_network(host: str = "github.com") -> bool:
    global IS_GITHUB_ACCESSIBLE
    print(f"  - 网络连通性 ({host}): ", end="", flush=True)
    try:
        subprocess.check_output(["ping", "-c", "1", "-W", "2", host], stderr=subprocess.STDOUT)
        print(f"{Colors.GREEN}畅通{Colors.ENDC}")
        IS_GITHUB_ACCESSIBLE = True
        return True
    except Exception:
        print(f"{Colors.RED}受限 (可能需要代理){Colors.ENDC}")
        IS_GITHUB_ACCESSIBLE = False
        return False


def check_endpoint(name: str, url: str, timeout: int = 5) -> bool:
    print(f"  - 链路检测 ({name}): ", end="", flush=True)
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req, context=_build_ssl_context(), timeout=timeout) as response:
            code = response.getcode()
        if code and 200 <= code < 400:
            print(f"{Colors.GREEN}可用{Colors.ENDC}")
            return True
        print(f"{Colors.YELLOW}状态码 {code}{Colors.ENDC}")
        return False
    except Exception:
        print(f"{Colors.RED}不可用{Colors.ENDC}")
        return False


def run_install_preflight() -> None:
    global IS_CLAWHUB_REGISTRY_ACCESSIBLE, IS_SKILLHUB_INSTALLER_ACCESSIBLE
    IS_CLAWHUB_REGISTRY_ACCESSIBLE = check_endpoint("ClawHub Registry", "https://registry.npmmirror.com")
    IS_SKILLHUB_INSTALLER_ACCESSIBLE = check_endpoint(
        "SkillHub Installer",
        "https://skillhub-1388575217.cos.ap-guangzhou.myqcloud.com/install/install.sh",
    )


def check_permissions(target_dir: str) -> None:
    print(f"  - 目录写入权限 ({target_dir}): ", end="", flush=True)
    if os.access(target_dir, os.W_OK):
        print(f"{Colors.GREEN}通过{Colors.ENDC}")
    else:
        print(f"{Colors.RED}拒绝 (请检查文件夹权限){Colors.ENDC}")


def check_openclaw_version(openclaw_cmd: Optional[str]) -> None:
    print("  - OpenClaw CLI: ", end="", flush=True)
    if not openclaw_cmd:
        print(f"{Colors.RED}未检测到 openclaw/claw 命令{Colors.ENDC}")
        return

    try:
        result = subprocess.run([openclaw_cmd, "--version"], capture_output=True, text=True, timeout=10)
        version = (result.stdout or result.stderr).strip().split("\n")[-1]
        if result.returncode == 0 and version:
            print(f"{Colors.GREEN}{openclaw_cmd} {version}{Colors.ENDC}")
        else:
            print(f"{Colors.YELLOW}可执行但未返回版本信息{Colors.ENDC}")
    except Exception:
        print(f"{Colors.RED}调用失败{Colors.ENDC}")


def check_clawhub() -> bool:
    print("  - ClawHub CLI: ", end="", flush=True)
    try:
        result = subprocess.run(["npx", "clawhub", "--cli-version"], capture_output=True, text=True, timeout=12)
        if result.returncode != 0:
            print(f"{Colors.YELLOW}待部署{Colors.ENDC}")
            return False

        version = result.stdout.strip().split()[-1] if result.stdout.strip() else "unknown"
        login_check = subprocess.run(["npx", "clawhub", "whoami"], capture_output=True, text=True, timeout=12)
        if login_check.returncode == 0:
            print(f"{Colors.GREEN}已登录 ({version}){Colors.ENDC}")
        else:
            print(f"{Colors.YELLOW}就绪但未登录 ({version}){Colors.ENDC}")
        return True
    except Exception:
        print(f"{Colors.RED}未检测到 Node.js 或 ClawHub{Colors.ENDC}")
        return False


def check_feishu_tools() -> bool:
    print("  - 飞书官方工具栈: ", end="", flush=True)
    try:
        result = subprocess.run(
            ["npx", "-y", "@larksuite/openclaw-lark-tools@latest", "--help"],
            capture_output=True,
            text=True,
            timeout=15,
        )
        if result.returncode == 0:
            print(f"{Colors.GREEN}发现并可用{Colors.ENDC}")
            return True
        print(f"{Colors.YELLOW}待部署{Colors.ENDC}")
        return False
    except Exception:
        print(f"{Colors.RED}无法调用 (需 Node.js){Colors.ENDC}")
        return False


def check_skillhub() -> bool:
    print("  - Tencent SkillHub: ", end="", flush=True)
    for path in ("skillhub", os.path.expanduser("~/.local/bin/skillhub")):
        try:
            result = subprocess.run([path, "--version"], capture_output=True, text=True, timeout=5)
            if result.returncode == 0:
                print(f"{Colors.GREEN}已就绪{Colors.ENDC}")
                return True
        except Exception:
            continue
    print(f"{Colors.YELLOW}未发现{Colors.ENDC}")
    return False


def diagnose_env(skills_dir: str, workspace_dir: str, openclaw_cmd: Optional[str]) -> None:
    print_step("正在开启多维度环境诊断...")
    print(f"  - Python 版本: {sys.version.split()[0]} ... {Colors.GREEN}通过{Colors.ENDC}")

    try:
        git_version = subprocess.check_output(["git", "--version"]).decode().strip()
        print(f"  - Git 版本: {git_version} ... {Colors.GREEN}通过{Colors.ENDC}")
    except Exception:
        print_error("未检测到 Git，请先安装 Git。")
        sys.exit(1)

    check_openclaw_version(openclaw_cmd)
    check_feishu_tools()
    check_clawhub()
    check_skillhub()
    check_network()
    run_install_preflight()
    check_permissions(skills_dir)
    check_permissions(workspace_dir)


def validate_repository_urls() -> bool:
    print_step("正在验证 SKILL_STORE 中的仓库地址...")
    all_valid = True

    ctx = ssl.create_default_context()
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE

    for _, skills in SKILL_STORE.items():
        for name, config in skills.items():
            url = config["url"]
            print(f"  - 检查 {name} ({url}) ... ", end="", flush=True)
            try:
                req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
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


def configure_feishu_streaming(openclaw_cmd: Optional[str], dry_run: bool = False) -> None:
    if not openclaw_cmd:
        print_warn("未检测到 openclaw/claw，跳过飞书 streaming 参数注入。")
        return

    print_step("优化飞书流式卡片配置...")
    commands = [
        [openclaw_cmd, "config", "set", "channels.feishu.streaming", "true"],
        [openclaw_cmd, "config", "set", "channels.feishu.footer.elapsed", "true"],
        [openclaw_cmd, "config", "set", "channels.feishu.footer.status", "true"],
    ]
    for cmd in commands:
        print(f"  执行: {' '.join(cmd)} ... ", end="", flush=True)
        try:
            result = run_command(cmd, timeout=20, dry_run=dry_run)
            if result.returncode == 0:
                print(f"{Colors.GREEN}成功{Colors.ENDC}")
            else:
                print(f"{Colors.YELLOW}忽略 (可能环境未完全就绪){Colors.ENDC}")
        except Exception:
            print(f"{Colors.RED}失败{Colors.ENDC}")


def install_feishu_plugin(openclaw_cmd: Optional[str], dry_run: bool = False) -> None:
    print_step("初始化飞书官方通讯插件...")
    install_cmd = "yes | npx -y @larksuite/openclaw-lark-tools@latest install"

    try:
        result = run_command(install_cmd, shell=True, timeout=240, dry_run=dry_run)
        if result.returncode == 0:
            print_success("飞书插件部署完成")
            configure_feishu_streaming(openclaw_cmd, dry_run=dry_run)
        else:
            print_error(f"飞书插件安装退出 (返回码: {result.returncode})")
    except Exception as e:
        print_error(f"飞书安装异常: {str(e)}")


def install_skillhub_cli(dry_run: bool = False) -> bool:
    print_step("正在自动部署 Tencent SkillHub CLI (国内加速源)...")
    install_cmd = (
        "curl -fsSL "
        "https://skillhub-1388575217.cos.ap-guangzhou.myqcloud.com/install/install.sh"
        " | bash -s -- --no-skills"
    )
    try:
        result = run_command(install_cmd, shell=True, timeout=180, dry_run=dry_run)
        if result.returncode == 0:
            print_success("SkillHub CLI 部署成功")
            local_bin = os.path.expanduser("~/.local/bin")
            if local_bin not in os.environ.get("PATH", ""):
                os.environ["PATH"] = f"{local_bin}:{os.environ.get('PATH', '')}"
            return True
        print_error("SkillHub 部署失败")
        return False
    except Exception as e:
        print_error(f"部署异常: {str(e)}")
        return False


def get_skillhub_cli() -> Optional[str]:
    for path in ("skillhub", os.path.expanduser("~/.local/bin/skillhub")):
        try:
            result = subprocess.run([path, "--version"], capture_output=True, timeout=5)
            if result.returncode == 0:
                return path
        except Exception:
            continue
    return None


def install_via_skillhub(skills_dir: str, dry_run: bool = False) -> None:
    print_step("通过 Tencent SkillHub 同步核心技能...")
    skillhub_path = get_skillhub_cli()

    if not skillhub_path:
        print_warn("未发现 SkillHub CLI，准备自动安装以开启加速模式...")
        if install_skillhub_cli(dry_run=dry_run):
            skillhub_path = get_skillhub_cli() or os.path.expanduser("~/.local/bin/skillhub")
        else:
            print_warn("SkillHub 安装失败，将跳过此模块（不影响后续 Git 安装流程）。")
            return

    installed_count = 0
    skipped_count = 0

    for slug in SKILLHUB_SLUGS:
        target_path = os.path.join(skills_dir, slug)
        if os.path.exists(target_path):
            print(f"  [已存在] {slug} - 跳过同步")
            skipped_count += 1
            continue

        print(f"  [SkillHub] 正在安装 {slug} ... ", end="", flush=True)
        try:
            result = run_command(
                [skillhub_path, "install", slug, "--dir", skills_dir],
                timeout=90,
                dry_run=dry_run,
            )
            if result.returncode == 0:
                print(f"{Colors.GREEN}完成{Colors.ENDC}")
                installed_count += 1
            else:
                stderr_lower = (result.stderr or "").lower()
                if "not found" in stderr_lower or "404" in stderr_lower:
                    print(f"{Colors.YELLOW}SkillHub 未收录此技能，将由 Git 补全{Colors.ENDC}")
                else:
                    err_msg = str(result.stderr or "").strip()
                    print(f"{Colors.YELLOW}失败（将由 Git 补全）: {err_msg[:80]}{Colors.ENDC}")
        except subprocess.TimeoutExpired:
            print(f"{Colors.YELLOW}超时，将由 Git 补全{Colors.ENDC}")
        except Exception as e:
            print(f"{Colors.RED}异常: {str(e)}{Colors.ENDC}")

    print(f"\n  SkillHub 汇总: 安装 {installed_count} 个，跳过 {skipped_count} 个。")


def install_via_clawhub(skills_dir: str, dry_run: bool = False) -> None:
    print_step("通过 ClawHub 尝试同步/更新 (可选)...")
    os.environ["CLAWHUB_REGISTRY"] = CHINA_REGISTRY

    for slug in CLAWHUB_SLUGS:
        target_path = os.path.join(skills_dir, slug)
        if os.path.exists(target_path):
            continue

        print(f"  [ClawHub] 尝试后台拉取 {slug} ... ", end="", flush=True)
        try:
            result = run_command(
                ["npx", "-y", "clawhub@latest", "install", slug, "--no-input", "--dir", skills_dir],
                timeout=90,
                dry_run=dry_run,
            )
            if result.returncode == 0:
                print(f"{Colors.GREEN}完成{Colors.ENDC}")
            else:
                print(f"{Colors.BLUE}已转入 Git 补全流程{Colors.ENDC}")
        except subprocess.TimeoutExpired:
            print(f"{Colors.YELLOW}超时，已转入 Git 补全{Colors.ENDC}")
        except Exception:
            print(f"{Colors.BLUE}跳过（将由 Git 补全）{Colors.ENDC}")


def parse_github_repo(url: str) -> Optional[Tuple[str, str]]:
    parsed = urlparse(url)
    if parsed.netloc.lower() != "github.com":
        return None

    path = parsed.path.strip("/")
    if path.endswith(".git"):
        path = path[:-4]
    parts = path.split("/")
    if len(parts) < 2:
        return None
    return parts[0], parts[1]


def safe_extract_tar(tar: tarfile.TarFile, path: str) -> None:
    base = os.path.abspath(path)
    for member in tar.getmembers():
        member_path = os.path.abspath(os.path.join(path, member.name))
        if not member_path.startswith(base + os.sep) and member_path != base:
            raise ValueError("tar 包含不安全路径，已拒绝解压")
    tar.extractall(path=path)


def download_repo_archive(url: str, branch: str, target_path: str, dry_run: bool = False) -> bool:
    repo_parts = parse_github_repo(url)
    if not repo_parts:
        return False

    owner, repo = repo_parts
    archive_urls = [
        f"https://codeload.github.com/{owner}/{repo}/tar.gz/refs/heads/{branch}",
        f"https://ghfast.top/https://codeload.github.com/{owner}/{repo}/tar.gz/refs/heads/{branch}",
        f"https://mirror.ghproxy.com/https://codeload.github.com/{owner}/{repo}/tar.gz/refs/heads/{branch}",
    ]

    print(f"    尝试源码包降级安装 ({owner}/{repo}:{branch}) ... ", end="", flush=True)
    if dry_run:
        print(f"{Colors.GREEN}dry-run 跳过下载{Colors.ENDC}")
        return True

    for archive_url in archive_urls:
        try:
            req = urllib.request.Request(archive_url, headers={"User-Agent": "Mozilla/5.0"})
            with urllib.request.urlopen(req, context=_build_ssl_context(), timeout=20) as response:
                payload = response.read()

            with tempfile.TemporaryDirectory(prefix="auto-config-skiller-") as temp_dir:
                tar_path = os.path.join(temp_dir, "repo.tar.gz")
                with open(tar_path, "wb") as f:
                    f.write(payload)

                extract_dir = os.path.join(temp_dir, "extract")
                os.makedirs(extract_dir, exist_ok=True)
                with tarfile.open(tar_path, "r:gz") as tar:
                    safe_extract_tar(tar, extract_dir)

                extracted_roots = [
                    os.path.join(extract_dir, name)
                    for name in os.listdir(extract_dir)
                    if os.path.isdir(os.path.join(extract_dir, name))
                ]
                if not extracted_roots:
                    continue

                shutil.move(extracted_roots[0], target_path)
            print(f"{Colors.GREEN}成功{Colors.ENDC}")
            return True
        except Exception:
            continue

    print(f"{Colors.RED}失败{Colors.ENDC}")
    return False


def clone_repo_with_fallback(
    url: str,
    branch: str,
    target_path: str,
    git_env: dict,
    dry_run: bool = False,
) -> Tuple[bool, str]:
    clone_urls = [
        url,
        f"{GITHUB_PROXY}{url}",
        f"https://mirror.ghproxy.com/{url}",
    ]
    last_error = ""

    for clone_url in clone_urls:
        try:
            result = run_command(
                ["git", "clone", "-b", branch, "--depth", "1", clone_url, target_path],
                timeout=90,
                env=git_env,
                dry_run=dry_run,
            )
            if result.returncode == 0:
                return True, ""
            last_error = str(result.stderr or result.stdout or "").strip()
        except subprocess.TimeoutExpired:
            last_error = "git clone 超时"
        except Exception as e:
            last_error = str(e)

    # git 通道全部失败时，自动降级到源码包安装（规避认证/握手问题）
    if download_repo_archive(url, branch, target_path, dry_run=dry_run):
        return True, ""

    if not last_error:
        last_error = "未知错误"
    return False, last_error


def install_skills(skills_dir: str, dry_run: bool = False) -> None:
    print_step("同步基础安装包 (Git Pull/Clone)...")
    hub_installed = set()
    for slug in CLAWHUB_SLUGS + SKILLHUB_SLUGS:
        if os.path.exists(os.path.join(skills_dir, slug)):
            hub_installed.add(slug.lower())

    for category, skills in SKILL_STORE.items():
        print(f"\n{Colors.BLUE}{Colors.BOLD}--- {category} ---{Colors.ENDC}")
        for name, config in skills.items():
            target_path = os.path.join(skills_dir, name)
            url = config["url"]
            tag = config.get("tag", "main")

            if name.lower() in hub_installed:
                print(f"  [Hub已覆盖] {name}")
                continue

            git_env = {**os.environ, "GIT_TERMINAL_PROMPT": "0"}
            if os.path.exists(target_path):
                print(f"  [已存在] {name} - 正在拉取更新 ... ", end="", flush=True)
                try:
                    result = run_command(
                        ["git", "-C", target_path, "pull", "origin", tag],
                        timeout=60,
                        env=git_env,
                        dry_run=dry_run,
                    )
                    if result.returncode == 0:
                        print(f"{Colors.GREEN}已更新{Colors.ENDC}")
                    else:
                        err_msg = str(result.stderr or "").strip()
                        print(f"{Colors.YELLOW}更新失败 (跳过): {err_msg[:60]}{Colors.ENDC}")
                except subprocess.TimeoutExpired:
                    print(f"{Colors.YELLOW}超时，跳过{Colors.ENDC}")
                except Exception as e:
                    print(f"{Colors.YELLOW}异常: {str(e)}{Colors.ENDC}")
            else:
                print(f"  [Git 克隆] {name} ... ", end="", flush=True)
                try:
                    ok, err = clone_repo_with_fallback(
                        url=url,
                        branch=tag,
                        target_path=target_path,
                        git_env=git_env,
                        dry_run=dry_run,
                    )
                    if ok:
                        print(f"{Colors.GREEN}完成{Colors.ENDC}")
                    else:
                        print(f"{Colors.RED}彻底失败{Colors.ENDC}")
                        err_lower = err.lower()
                        if "authentication failed" in err_lower or "permission denied" in err_lower:
                            print(f"    {Colors.RED}原因: Git 认证失败，已自动尝试代理与源码包降级仍失败{Colors.ENDC}")
                        elif "not found" in err_lower or "does not exist" in err_lower:
                            print(f"    {Colors.RED}原因: 仓库不存在或 URL 有误{Colors.ENDC}")
                        else:
                            print(f"    {Colors.RED}详情: {err[:120]}{Colors.ENDC}")
                except subprocess.TimeoutExpired:
                    print(f"{Colors.RED}超时{Colors.ENDC}")
                except Exception as e:
                    print(f"{Colors.RED}克隆异常: {str(e)}{Colors.ENDC}")


def choose_persona(interactive: bool) -> int:
    if not interactive or not sys.stdin.isatty():
        return 0

    print_step("配置内置 AI 人设 (Persona)")
    for i, persona in enumerate(PERSONAS, start=1):
        print(f"  [{i}] {persona['name']}")
    print("  [0] 跳过设置")

    print(
        f"\n{Colors.YELLOW}请选择人设编号 (0-{len(PERSONAS)}, 30秒超时自动跳过): {Colors.ENDC}",
        end="",
        flush=True,
    )
    ready, _, _ = select.select([sys.stdin], [], [], 30)
    if not ready:
        print("\n")
        return 0

    choice = sys.stdin.readline().strip()
    if not choice.isdigit():
        return 0
    return int(choice)


def setup_persona(persona_index: int, workspace_dir: str, dry_run: bool = False) -> None:
    if persona_index <= 0:
        print_step("跳过人设注入 (默认 OpenClaw 无交互模式)")
        return

    idx = persona_index - 1
    if idx < 0 or idx >= len(PERSONAS):
        print_warn("人设编号无效，已跳过注入。")
        return

    selected = PERSONAS[idx]
    print_step(f"配置内置 AI 人设: {selected['name']}")

    urls_to_try = [
        f"https://ghfast.top/https://raw.githubusercontent.com/msitarzewski/agency-agents/main/{selected['path']}",
        f"https://ghproxy.net/https://raw.githubusercontent.com/msitarzewski/agency-agents/main/{selected['path']}",
        f"https://raw.githubusercontent.com/msitarzewski/agency-agents/main/{selected['path']}",
    ]
    persona_path = os.path.join(workspace_dir, "persona.md")

    if dry_run:
        print(f"    [dry-run] write persona -> {persona_path}")
        return

    ctx = ssl.create_default_context()
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE

    for raw_url in urls_to_try:
        try:
            req = urllib.request.Request(raw_url, headers={"User-Agent": "Mozilla/5.0"})
            with urllib.request.urlopen(req, context=ctx, timeout=10) as response:
                content = response.read().decode("utf-8")

            with open(persona_path, "w", encoding="utf-8") as f:
                f.write(content)

            print_success(f"人设已写入: {persona_path}")
            return
        except Exception:
            continue

    print_error("获取人设失败（所有镜像节点均不可达）。")


def main() -> None:
    parser = argparse.ArgumentParser(description="OpenClaw 自动配置助手（默认无交互）")
    parser.add_argument("--skills-dir", help="技能安装目录，默认自动探测")
    parser.add_argument("--skip-validation", action="store_true", help="跳过仓库 URL 验证")
    parser.add_argument("--skip-feishu", action="store_true", help="跳过飞书插件安装")
    parser.add_argument("--skip-persona", action="store_true", help="跳过人设注入")
    parser.add_argument("--persona", type=int, default=0, help="直接指定人设编号（1-N），0 表示跳过")
    parser.add_argument("--interactive-persona", action="store_true", help="允许在 TTY 中交互选择人设")
    parser.add_argument("--dry-run", action="store_true", help="仅打印动作，不实际执行")
    args = parser.parse_args()

    skills_dir, source = resolve_skills_dir(args.skills_dir)
    workspace_dir = resolve_workspace_dir(skills_dir)
    openclaw_cmd = detect_openclaw_command()

    print(f"{Colors.HEADER}{Colors.BOLD}=======================================")
    print("   OpenClaw 自动配置助手 (OpenClaw 调用友好模式)")
    print(f"======================================={Colors.ENDC}")
    print(f"{Colors.BLUE}技能安装目录: {skills_dir} (来源: {source}){Colors.ENDC}")
    print(f"{Colors.BLUE}工作区目录: {workspace_dir}{Colors.ENDC}")
    print(
        f"{Colors.BLUE}模式: {'DRY-RUN' if args.dry_run else 'EXECUTE'} / "
        f"{'交互人设' if args.interactive_persona else '无交互人设'}{Colors.ENDC}"
    )
    print(f"{Colors.BLUE}---------------------------------------{Colors.ENDC}")

    diagnose_env(skills_dir, workspace_dir, openclaw_cmd)

    if not args.skip_validation:
        if IS_GITHUB_ACCESSIBLE:
            validate_repository_urls()
        else:
            print_warn("网络受限，自动跳过仓库 URL 连通性探测。")

    if args.skip_feishu:
        print_step("按参数跳过飞书插件安装")
    else:
        install_feishu_plugin(openclaw_cmd, dry_run=args.dry_run)

    if not IS_GITHUB_ACCESSIBLE and not IS_CLAWHUB_REGISTRY_ACCESSIBLE and not IS_SKILLHUB_INSTALLER_ACCESSIBLE:
        print_warn("网络环境不可用，已自动降级为离线模式：跳过在线安装步骤。")
    elif IS_GITHUB_ACCESSIBLE:
        print(f"\n{Colors.BLUE}>>> GitHub 可访问，优先使用 ClawHub + Git 同步技能...{Colors.ENDC}")
        if IS_CLAWHUB_REGISTRY_ACCESSIBLE:
            install_via_clawhub(skills_dir, dry_run=args.dry_run)
        else:
            print_warn("ClawHub Registry 不可用，自动跳过 ClawHub 步骤。")
        install_skills(skills_dir, dry_run=args.dry_run)
    else:
        print(f"\n{Colors.YELLOW}>>> GitHub 受限，自动降级为 SkillHub -> ClawHub -> Git/源码包 兜底...{Colors.ENDC}")
        if IS_SKILLHUB_INSTALLER_ACCESSIBLE:
            install_via_skillhub(skills_dir, dry_run=args.dry_run)
        else:
            print_warn("SkillHub 安装链路不可用，自动跳过 SkillHub。")
        if IS_CLAWHUB_REGISTRY_ACCESSIBLE:
            install_via_clawhub(skills_dir, dry_run=args.dry_run)
        else:
            print_warn("ClawHub Registry 不可用，自动跳过 ClawHub。")
        install_skills(skills_dir, dry_run=args.dry_run)

    ensure_env_template(workspace_dir, dry_run=args.dry_run)

    if args.skip_persona:
        setup_persona(0, workspace_dir, dry_run=args.dry_run)
    else:
        persona_index = args.persona or choose_persona(args.interactive_persona)
        setup_persona(persona_index, workspace_dir, dry_run=args.dry_run)

    print_step("配置任务完成！")
    print("提示: 核心内容已就绪。请查看指南 ./docs/USAGE_GUIDE.md")
    print(f"\n{Colors.GREEN}{Colors.BOLD}自动化流程执行完毕！{Colors.ENDC}")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print(f"\n{Colors.RED}程序被用户中断。{Colors.ENDC}")
        sys.exit(1)
    except Exception as e:
        print(f"\n{Colors.RED}程序发生非预期错误: {e}{Colors.ENDC}")
        sys.exit(1)
