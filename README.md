# 🚀 OpenClaw Auto-Config-Skiller (自动配置助手)

[![OpenClaw](https://img.shields.io/badge/OpenClaw-Skill-blue.svg)](https://github.com/openclaw/openclaw)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](https://opensource.org/licenses/MIT)

> **Auto-Config-Skiller** 旨在解决 OpenClaw 新手“环境配置慢、技能安装杂、人设缺失”的痛点，为您提供一键式、傻瓜化的配置体验。它是一个自动化极强的“元技能”（Meta-Skill），专门用来组装和调优您的 OpenClaw Agent。

## ✨ 核心特性

- 🩺 **全自动化环境体检**：自动检测 Python、Node.js、Git、权限以及网络畅通度。
- ⚡ **多源加速下载机制**：无缝集成 **ClawHub**、**Tencent SkillHub（国内加速）** 以及 **GitHub Fast Proxy（防墙直连）**，无惧任何网络或登录限制。
- 🛠️ **预装全套高分技能**：为您预置经过实战检验的核心全家桶（如安全扫描、路由、自我优化 Agent、多引擎搜索等）。
- 🤫 **符合官方规范的静默安装**：完全无阻塞执行，自动生成 `.env` 配置文件模板，后续按需修改，丝滑融入自动化流水线。
- 🎭 **一键下发专业人设**：基于权威社区提示词库，自动为您置入顶级 Prompt 模板（如 AI 工程师）。

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

### 🎁 您将完整获得的“弹药库”
本助手并非简单的脚本，它内部集成了强大的工作流机制和丰厚的开箱即用插件。运行 `setup.sh` 后，它将自动为您加载以下五大板块的能力：

#### 1. 🩺 深度环境体检与自修复 (Deep Diagnosis)
- **依赖自检**：毫秒级探测 Python 3.9+、Node.js 与 Git 版本，以及读写权限。
- **配置探测**：自动嗅探版本并生成对应的 `.env` 本地模板。
- **飞书枢纽自动联通**：自动静默拉取官方通讯插件 `@larksuite/openclaw-lark-tools@latest`，并帮您自动执行流式回答优化（自动开启 `channels.feishu.streaming` 等底层通讯优化卡片体验）。

#### 2. ⚡ 极限智能代理与容错中心 (Proxy & Network Fallback)
为了扫平国内开发者配环境的一切阻碍，引入了军工级防断连网络机制：
- **实时探测链路**：工具启动时毫秒级测速 `github.com`。
- **三重无回显并发下载**：GitHub 直连超时时，自动切入国内定制加速链：**Tencent SkillHub** 模块优先 -> **ClawHub** 国内源降级 -> **GH-Proxy / GH-Fast** Git 双重重试兜底。
- **SSL 强握手规避**：对 GitHub Raw 采取 3 个代理节点阵列负载，彻底解决国内访问大模型指令库握手报错和 404 死链问题。

#### 3. 🤖 Persona 灵魂注入系统 (Auto-Prompting)
不需要您去学晦涩深奥的提示词工程：
- 开箱集成由资深极客维护的 [agency-agents](https://github.com/msitarzewski/agency-agents) 高级人设项目。
- 自动化流中提供了高达 60 秒的延时带参选择菜单，您可以自主化身为：AI 工程师、架构师或代码审查专家。若不操作则自动跳过，契合 OpenClaw 完全后台静默式运转的第一原则。

#### 4. 🧰 特级高分能力组 (The 13 Core Skills)
系统将并行且以最新分支为您全自动装载经过 OpenClaw 官方社区认证的 13 大金牌防爆模块，实现：全栈打通。

**[架构与基础设施层]**
- `exec-tool`：高能终端执行器。
- `channels-setup`：多渠道快速搭建通道向导 (如飞书/钉钉)。
- `claw-router`：智能模型路由网关，帮您自动分发给性价比高的大模型、有效控制 Token 成本。

**[自我进化与黑客级研发层]**
- `self-improving-agent`：在与您对话的过程中，让大模型自主修改错误代码并自动迭代的能力。
- `skill-creator`：给 Agent 加入自动化生成新 Skill 的造物主能力。
- `github`：原生打通代码仓互动及审查能力。
- `skill-vetter`：作为守门员，部署任何非官方来源技能前将进行深度黑盒代码安全排除了流氓风险。

**[信息聚合与超级全能工具层]**
- `agent-browser`：专属 AI 高沉浸纯净浏览器操作组件。
- `multi-search-engine`：聚合如 Google / Tavily 甚至 17 个搜索引擎库帮大模型长脑子。
- `weather-skill` & `cron-mastery`：基于生活向的环境感知与高精度定时计划调度服务。
- `find-skills` & `IM-Master-Skills`：涵盖了全站中文开源的高精尖实用套件合集与知识库入口。

#### 5. 🤫 符合原生的无头环境管理 (Headless Friendly)
所有的错误抛出、下载提示，最终都会统一返回到规范的日志系统中。即便是在完全黑屏没有外设（如 Github Actions / Docker）中，它都能在后台通过管道捕获平稳完成体检+组装，没有任何阻挡阻塞流程（哪怕是回车）。

---

## 📖 详细文档

欲了解完整的工作流解析、进阶运维指南以及常见问题解答（FAQ），请参阅我们准备的详细手册：
👉 **[点击查阅《使用指南 (USAGE_GUIDE.md)》](./docs/USAGE_GUIDE.md)**

---

## 🤝 贡献与反馈

这是为广大中文生态用户量身定制的提效工具。如果在部署中遇到任何网络或兼容问题，欢迎在 GitHub 提交 [Issues](https://github.com/wuhongchen/Auto-Config-Skiller/issues)！
我们崇尚 **KISS** (Keep It Simple, Stupid) 原则与**第一性原理**。感谢您的使用与反馈！
