#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"

cd "$SCRIPT_DIR"

echo "Running pytest in $(pwd)"
# Build the C++ project first
echo "Building project..."
make

pytest -q tests