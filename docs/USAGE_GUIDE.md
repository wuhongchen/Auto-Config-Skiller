# 🚀 OpenClaw 自动配置助手 (Auto-Config-Skiller) 使用指南

本助手旨在解决 OpenClaw 新手“环境配置慢、技能安装杂、人设缺失”的痛点，提供一键式、傻瓜化的配置体验。

## 📦 一键安装 (Quick Install)

如果您已经安装了 OpenClaw，可以通过以下原生命令直接安装并启动本工具：

```bash
npx clawhub install https://github.com/wuhongchen/Auto-Config-Skiller.git
```

```bash
./setup.sh
```

> ⚠️ **遵循 OpenClaw 设计理念**：本工具全程采用**静默式无阻塞执行（Silent Execution）**，不会在终端进行任何需要人为介入的弹窗拦截或交互询问。它将在后台丝滑平稳地为您准备好一切！

---

## 🛠 一键配置标准工作流 (Standard Workflow)

只需运行一个命令，即可完成从环境体检到灵魂注入的全过程：
```bash
./setup.sh
```

### 第一步：全方位环境诊断 (Diagnosis)
脚本启动后，会立即对您的系统进行“核磁共振”式的体检：
- **核心组件**：检测 Python 3.9+、Git、Node.js 是否就绪。
- **环境探测**：自动识别当前的 OpenClaw 版本。
- **资源就绪**：检查磁盘写入权限及 `.env` 配置文件状态。
- **网络测试**：实时测试 GitHub 及官方注册表的连通性，自动切换国内备用镜像。

### 第二步：飞书通讯枢纽部署 (Feishu Plugin)
通过官方工具链 `@larksuite/openclaw-lark-tools` 快速建立通讯桥梁：
- **自动安装**：一键部署官方飞书插件。
- **引导配置**：脚本会引导您完成飞书机器人的创建与参数填入。

### 第三步：核心技能库全量分发 (Skill Orchestration)
本工具采用了 **“Tencent SkillHub 优先 + ClawHub 补全 + Git 深度同步”** 的三重保障机制：
- **免登录安装**：优先使用腾讯源安装 `skill-vetter`、`channels-setup` 等高分技能，绕过官方源的付费或登录校验。
- **高分应用全家桶**：自动为您装好 `self-improving-agent`、`github`、`agent-browser` 等 Agent 必备工具。
- **版本锁定**：自动匹配各个技能的最稳定分支（main/master），确保环境一致性。

### 第四步：环境配置模板下发 (Auto .env)
再也不用手动去复制粘贴 `.env.example`，工具会静默检查配置状态：
- **安全拷贝**：如未配置，将为您自动复制生成 `.env` 初始配置模板。
- **配置指引**：在控制台打印醒目的提醒，引导您在脚本运行结束后自行填入飞书密钥、API Key 等关键参数（符合完全隔离的自动化设计）。

### 第五步：AI 灵魂静默注入 (Persona Injection)
基于开源高分项目 `msitarzewski/agency-agents` 库：
- **默认武装**：在后台自动下载并配置“AI 工程师 (AI Engineer)”经典人设到 `persona.md`。
- **灵活替换**：此人设将作为 System Prompt 注入您的终端环境。后续如需切换职业，您可直接手动编辑或覆盖 `persona.md` 文件。

---

## 🌟 进阶运维场景

### 1. 定期技能体检
如果您在运行过程中发现某个技能库代码过旧，再次运行 `./setup.sh`，脚本会自动执行 `git pull` 或 `clawhub update` 增量更新。

### 2. 切换人设
想让您的 Agent 从“AI 工程师”变成“软件架构师”或“代码评审专家”？直接修改工作区下的 `persona.md` 文件内容，替换为新的 Prompt 内容即可。

## 💡 常见问题 (FAQ)
- **Q: 提示 skillhub 未找到或无法安装？**
  - A: 如果网络严重受限导致腾讯加速源也无法部署，脚本会自动打印“已转入 Git 补全流程”。由于采用无阻塞退避原则，全过程不影响您的基础安装。
- **Q: .env 文件该怎么填？**
  - A: 打开项目目录下的 `.env`，填入 `OPENAI_API_KEY`（大模型调用凭证）以及您申请好的 `FEISHU_APP_ID` / `FEISHU_APP_SECRET`（如果配置了飞书机器人通讯）。
- **Q: 安装失败了？**
  - A: 请检查本地网络连通性。若官方源不稳定，工具具备智能探测连通性的功能，通常在几秒钟后会自动切换镜像源，耐心等待即可。
