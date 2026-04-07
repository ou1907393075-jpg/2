#!/usr/bin/env bash
set -euo pipefail

if ! command -v python3 >/dev/null 2>&1; then
  echo "[错误] 未检测到 python3，请先安装 Python 3 后重试。"
  exit 1
fi

cd "$(dirname "$0")"
python3 game.py
