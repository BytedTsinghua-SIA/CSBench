#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"

cd "$SCRIPT_DIR"
export PYTHONPATH="$PWD:${PYTHONPATH:-}"
echo "Running pytest in $(pwd)"
pytest -q tests
