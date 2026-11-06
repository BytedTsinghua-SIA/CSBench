#!/usr/bin/env bash
set -euo pipefail

# 获取脚本所在目录（在容器中应该是 /testbed）
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"

# 在容器中，如果构建上下文是 src 目录，文件会被直接复制到 /testbed
# 所以 /testbed 包含 bpe.py, tests/ 等，但没有 src/ 目录
# 但是测试文件使用 from src.xxx，所以我们需要创建 src 目录结构

# 检查是否需要创建 src 目录结构
if [ -f "${SCRIPT_DIR}/bpe.py" ] && [ ! -d "${SCRIPT_DIR}/src" ]; then
    # 文件直接在 /testbed 下，需要创建 src 目录结构
    # 在 /testbed 下创建 src 目录，并将 Python 文件链接进去
    mkdir -p "${SCRIPT_DIR}/src"
    # 将所有 .py 文件链接到 src 目录（除了 tests 目录下的）
    for pyfile in "${SCRIPT_DIR}"/*.py; do
        if [ -f "$pyfile" ]; then
            filename=$(basename "$pyfile")
            if [ ! -e "${SCRIPT_DIR}/src/${filename}" ]; then
                ln -sf "../${filename}" "${SCRIPT_DIR}/src/${filename}"
            fi
        fi
    done
    # 创建 __init__.py
    touch "${SCRIPT_DIR}/src/__init__.py"
    # PYTHONPATH 设置为 /testbed，这样 from src.xxx 就能找到 /testbed/src/xxx
    export PYTHONPATH="${SCRIPT_DIR}:${PYTHONPATH:-}"
else
    # 正常情况：src 目录存在（构建上下文是整个项目）
    PROJECT_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"
    export PYTHONPATH="${PROJECT_ROOT}:${PYTHONPATH:-}"
fi

cd "$SCRIPT_DIR"

echo "Running pytest in $(pwd)"

# 运行测试
pytest -q tests
