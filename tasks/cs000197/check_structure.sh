#!/usr/bin/env bash
# 打印项目目录结构并比较 test.sh / tests 是否一致

set -e

ROOT_DIR="${1:-.}"

echo "📁 Project structure under: $ROOT_DIR"
echo "----------------------------------------"

# 优先用 tree 打印结构
if command -v tree >/dev/null 2>&1; then
    tree -L 3 "$ROOT_DIR"
else
    find "$ROOT_DIR" -maxdepth 3 | sed 's|[^/]*/|  |g'
fi

echo "----------------------------------------"
echo "🔍 Checking key files and test consistency..."

# 定义路径
META_DIR="$ROOT_DIR/metadata"
SRC_DIR="$ROOT_DIR/src"
TEST_OVERRIDE_DIR="$META_DIR/test_override"

# 1️⃣ 检查必要目录
for dir in "$META_DIR" "$SRC_DIR" "$TEST_OVERRIDE_DIR"; do
    if [ ! -d "$dir" ]; then
        echo "❌ Missing directory: $dir"
        MISSING=1
    fi
done

# 2️⃣ 检查关键文件
for f in Dockerfile task.md; do
    if [ -f "$META_DIR/$f" ]; then
        echo "✅ Found: metadata/$f"
    else
        echo "❌ Missing: metadata/$f"
    fi
done

# 3️⃣ 比较 test.sh
if [ -f "$TEST_OVERRIDE_DIR/test.sh" ] && [ -f "$SRC_DIR/test.sh" ]; then
    if diff -q "$TEST_OVERRIDE_DIR/test.sh" "$SRC_DIR/test.sh" >/dev/null; then
        echo "✅ test.sh files are identical"
    else
        echo "⚠️ test.sh files differ between test_override and src"
        echo "   Run: diff $TEST_OVERRIDE_DIR/test.sh $SRC_DIR/test.sh"
    fi
else
    echo "❌ Missing test.sh in one of: $TEST_OVERRIDE_DIR or $SRC_DIR"
fi

# 4️⃣ 比较 tests 目录
if [ -d "$TEST_OVERRIDE_DIR/tests" ] && [ -d "$SRC_DIR/tests" ]; then
    echo "🔍 Comparing tests/ directories..."
    DIFF_OUTPUT=$(diff -qr "$TEST_OVERRIDE_DIR/tests" "$SRC_DIR/tests" || true)
    if [ -z "$DIFF_OUTPUT" ]; then
        echo "✅ tests directories are identical"
    else
        echo "⚠️ tests directories differ:"
        echo "$DIFF_OUTPUT"
    fi
else
    echo "❌ Missing tests/ in one of: $TEST_OVERRIDE_DIR or $SRC_DIR"
fi

echo "----------------------------------------"
echo "✅ Structure check complete."
