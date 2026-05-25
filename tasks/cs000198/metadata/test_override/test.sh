#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
export PYTHONPATH="${SCRIPT_DIR}:${PYTHONPATH:-}"

cd "$SCRIPT_DIR"

# 编译并准备 ramulator 测试所需文件（静音正常输出，保留错误）
echo "Compiling test_cache..."
make test_cache >/dev/null

echo "Running pytest in $(pwd)"
pytest -q tests


