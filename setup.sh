#!/usr/bin/env bash

set -euo pipefail

# ==========================================
# OpenClaw 自动配置助手 - 一键启动脚本
# ==========================================

GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m'

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ENTRY="${SCRIPT_DIR}/scripts/diagnose_and_install.py"

echo -e "${BLUE}=======================================${NC}"
echo -e "${BLUE}   OpenClaw 自动配置助手 (OpenClaw 友好模式)${NC}"
echo -e "${BLUE}=======================================${NC}"

if ! command -v python3 >/dev/null 2>&1; then
    echo -e "${YELLOW}未发现 Python3，请先安装 Python。${NC}"
    exit 1
fi

echo -e "${GREEN}[*] 正在启动环境体检与自动安装...${NC}"
python3 "${ENTRY}" "$@"

echo -e "\n${GREEN}处理完成。${NC}"
echo -e "${YELLOW}如需飞书联通，请按脚本提示补全 .env 后再执行渠道配置。${NC}"
echo -e "${BLUE}查看详细指南: ${SCRIPT_DIR}/docs/USAGE_GUIDE.md${NC}"
