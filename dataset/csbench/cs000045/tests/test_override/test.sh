#!/usr/bin/env bash
# 统一测试入口脚本
# 功能: 构建 + 执行 pytest 单元测试
set -euo pipefail

PROJECT_ROOT=$(cd "$(dirname "$0")/../.." && pwd)
# echo "[INFO] 项目根目录: $PROJECT_ROOT"

SCRIPT_DIR=$(cd "$(dirname "$0")" && pwd)
echo "[INFO] 脚本目录: $SCRIPT_DIR"

echo "[INFO] 运行 pytest..."
python3 -m pytest -q "$SCRIPT_DIR/tests" || {
  echo "[ERROR] 单元测试失败" >&2
  exit 1
}

echo "[INFO] 所有测试通过。"
