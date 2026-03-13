# 🚀 OpenClaw 自动配置助手使用指南

本技能旨在为您的 OpenClaw 提供全方位的环境管理、技能编排与快速部署能力。

## 🌟 核心使用场景

### 1. 新环境一键体检 (Environment Diagnosis)
**场景**：刚在一台新电脑上部署了 OpenClaw，或者运行中发现 Agent 响应异常。
**命令**：
```bash
python3 scripts/diagnose_and_install.py
```
**效果**：
- 自动识别 OpenClaw 核心版本。
- 检查 Python、Git 及 Node.js (ClawHub) 环境。
- 实时测试 GitHub 连通性，诊断网络堵塞。
- 探测 `.env` 配置文件是否缺失。

### 2. 必装技能包快速同步 (One-Click Install)
**场景**：快速补全 OpenClaw 生态中最常用、最核心的工具。
**动作**：
- **混合安装路径**：优先通过 **Tencent SkillHub** (腾讯源) 安装 `skill-vetter` 等核心组件，解决官方源需要登录或付费的问题。
- **官方兜底**：作为补全，支持通过官方 ClawHub 或直接 Git 克隆完成安装。
- **智能版本管理**：为不同技能匹配适配的分支（如 `main`/`master`），确保运行稳定性。

### 3. 配置飞书通讯枢纽 (Official Feishu Plugin)
**场景**：需要将 OpenClaw 接入飞书，并实现文档、日历、Meego 的深度自动化。
**动作**：
- 脚本将引导您完成官方飞书工具包的配置。
- 自动创建或关联飞书机器人，并完成一键授权。

### 4. 内置人设注入 (Persona Setup)
**场景**：需要赋予 Robot 专业的灵魂设定。
**动作**：
- 在配置结尾，为您准备了来自 `agency-agents` 的高分人设库。
- 选择后会自动下载完整的 Persona Prompt 到 `persona.md` 中，随时可复制到 System Prompt 注入灵魂。

### 5. 技能库持续维护 (Update & Maintenance)
**场景**：需要同步最新的技能包代码。
**命令**：
- 建议通过 `npx clawhub update` 维护已通过 ClawHub 安装的插件。
- 重新运行本脚本会自动下载缺失的必备库。

## 🛠 维护者 Tips
- **权限问题**：若提示权限拒绝，请确保在工作目录下运行。
- **配置提醒**：安装完成后，请务必根据 `.env.example` 填写您的 API Keys。
- **官方插件**：飞书插件推荐配合 `/feishu auth` 命令解锁完整文档读写能力。
