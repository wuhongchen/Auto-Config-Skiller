# Auto Config Skiller (自动配置助手)

该技能旨在为 OpenClaw 用户提供一键式的环境初始化、基础技能安装及核心配置服务。

## 场景描述
当你刚刚安装好基础的 OpenClaw 后，可以使用此技能快速补全“小龙虾”生态所需的核心 Skill 和 Python 依赖库，避免手动克隆仓库和配置 `.env` 的繁琐过程。

## 核心分类编排
为了让 OpenClaw 更具战斗力，我们将技能分为以下四个核心维度：

1. **通讯 (Communication)**
   - `Feishu-OpenClaw`: 飞书官方插件，支持文档、群聊、日历及 Meego 深度集成。
2. **基础工具 (Basic Tools)**
   - `CN-Life Toolkit`: 国内生活服务（天气、快递、油价等）。
   - `Exec Tool / Web Search`: 核心执行与搜索能力。
3. **优化工具 (Optimization Tools)**
   - `Skill-Self-Improving`: 让 AI 在交互中自我优化。
   - `ClawRouter`: 智能路由，优化成本。
4. **安全工具 (Security Tools) - [必装]**
   - `Skill-Vetter`: 技能审计大师，安装其他技能前的第一道防线。
   - `Clawscan`: 安全扫描。

## 工作流 (Workflows)
1. **环境诊断 (Diagnosis)**
   - **官方通道**: 集成飞书诊断与修复工具 `openclaw-lark-tools`。
   - **配置自检**: 自动识别 `.env` 配置文件状态及目录写入权限。
   - **资源评估**: 检测磁盘空间等基础硬件状态。
2. **分类调研 (Research)**
   - 自动拉取 ClawHub 推荐列表，识别核心工具。
3. **自动化安装 (Auto-Install)**
   - 交互式选择分类或全量安装。
   - **多源加速**: 支持 ClawHub 与 Tencent SkillHub (国内镜像)，自动避开登录限制。
   - **智能配置**: 自动完成 `.env` 交互式引导配置。


## 维护者
Antigravity
