#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
export PYTHONPATH="${SCRIPT_DIR}:${PYTHONPATH:-}"

cd "$SCRIPT_DIR"

# Compile test_multicore executable
echo "Compiling test_multicore..."
make test_multicore

# Run pytest
echo "Running pytest in $(pwd)"
pytest -q tests


