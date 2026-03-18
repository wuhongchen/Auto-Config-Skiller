---
name: auto-config-skiller
slug: auto-config-skiller
version: 1.2.0
description: OpenClaw 环境诊断 + 核心技能自动安装助手，默认无交互执行。
metadata:
  clawdbot:
    emoji: "🛠️"
    os: ["darwin", "linux"]
    requires:
      bins: ["python3", "git", "npx"]
  openclaw:
    type: skill
    entry: setup.sh
---

# Auto Config Skiller

用于 OpenClaw 新环境的一键初始化：体检、安装链路自检、自动降级安装、通道插件安装、技能同步、`.env` 模板生成。

## 何时使用

- 用户说“初始化 OpenClaw”“一键装基础技能”“帮我配置环境”。
- 工作区刚创建，缺少常用技能和配置模板。

## OpenClaw 调用方式

优先使用默认无交互模式：

```bash
./setup.sh --skip-persona
```

如果要注入人设，可显式指定编号（非交互）：

```bash
python3 scripts/diagnose_and_install.py --persona 1
```

仅在用户明确要求时，才使用交互选择：

```bash
python3 scripts/diagnose_and_install.py --interactive-persona
```

## 常用参数

- `--skills-dir <path>`: 指定技能安装目录。
- `--skip-feishu`: 跳过飞书插件部署。
- `--skip-validation`: 跳过 Git 仓库连通性验证。
- `--skip-persona`: 跳过人设注入。
- `--dry-run`: 仅打印执行计划，不真实安装。

## 目录约定

- 优先使用 `OPENCLAW_SKILLS_DIR` 或 `OPENCLAW_WORKSPACE/skills`。
- 若目录结构符合 `<workspace>/skills/<this-skill>`，则自动安装到 `<workspace>/skills`。
- `persona.md` 与 `.env` 生成在工作区目录（默认是 `<workspace>`）。
