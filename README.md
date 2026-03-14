# 🚀 OpenClaw Auto-Config-Skiller (自动配置助手)

[![OpenClaw](https://img.shields.io/badge/OpenClaw-Skill-blue.svg)](https://github.com/openclaw/openclaw)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](https://opensource.org/licenses/MIT)

> **Auto-Config-Skiller** 旨在解决 OpenClaw 新手“环境配置慢、技能安装杂、人设缺失”的痛点，为您提供一键式、傻瓜化的配置体验。它是一个自动化极强的“元技能”（Meta-Skill），专门用来组装和调优您的 OpenClaw Agent。

## ✨ 核心特性

- 🩺 **全自动化环境体检**：自动检测 Python、Node.js、Git、权限以及网络畅通度。
- ⚡ **多源加速下载机制**：无缝集成 **ClawHub**、**Tencent SkillHub（国内加速）** 以及 **GitHub Fast Proxy（防墙直连）**，无惧任何网络或登录限制。
- 🛠️ **预装全套高分技能**：为您预置经过实战检验的核心全家桶（如安全扫描、路由、自我优化 Agent、多引擎搜索等）。
- 💬 **沉浸交互配置体验**：智能探测终端类型，支持交互式问答自动生成 `.env` 配置文件（如检测环境不支持交互会安全降级自动生成）。
- 🎭 **一键注入专业人设**：基于权威社区提示词库，为您内置架构师、代码审查专家、产品经理等顶级 Prompt 模板。

---

## 📦 快速安装 (Quick Install)

作为标准的 OpenClaw 包，您可以直接在终端（或与 Agent 的对话中）输入以下指令一键安装本工具：

```bash
npx clawhub install https://github.com/wuhongchen/Auto-Config-Skiller.git
```

如果是在 Agent 对话框中，您也可以直接对它说：
> *“帮我用 clawhub 安装这个技能：`https://github.com/wuhongchen/Auto-Config-Skiller.git`”*

---

## 🚀 使用方法 (Usage)

安装成功后，进入到技能目录并执行引导脚本即可开启自动化配置流：

```bash
cd <您的 OpenClaw 工作区>/auto-config-skiller
./setup.sh
```

*(如果提示没有执行权限，通常只需要运行一次 `chmod +x setup.sh`。事实上，如果您通过 OpenClaw 官方包管理器安装，此步已被自动处理。)*

### 🎁 我们为您准备了哪些“弹药”？
脚本运行后，将自动为您编排并加载以下精选技能（免配置/免维护）：
- **核心体系**：`exec-tool` (执行器)、`claw-router` (智能模型路由/控制成本)、`channels-setup` (飞书/微信通道拓展)。
- **安全与防护**：`skill-vetter` 及 `clawscan`，构筑全方位代码防线。
- **高级强化模式**：`self-improving-agent` (自纠正智能体)、`github` 分析组件、`agent-browser` (沉浸式网页研判)、`skill-creator`。
- **神级效率工具**：`cron-mastery` (定时任务)、`multi-search-engine` (17款搜商整合包含百度/谷歌)。

---

## 📖 详细文档

欲了解完整的工作流解析、进阶运维指南以及常见问题解答（FAQ），请参阅我们准备的详细手册：
👉 **[点击查阅《使用指南 (USAGE_GUIDE.md)》](./docs/USAGE_GUIDE.md)**

---

## 🤝 贡献与反馈

这是为广大中文生态用户量身定制的提效工具。如果在部署中遇到任何网络或兼容问题，欢迎在 GitHub 提交 [Issues](https://github.com/wuhongchen/Auto-Config-Skiller/issues)！
我们崇尚 **KISS** (Keep It Simple, Stupid) 原则与**第一性原理**。感谢您的使用与反馈！
