#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
export PYTHONPATH="${SCRIPT_DIR}/../../src:${PYTHONPATH:-}"

cd "$SCRIPT_DIR"

echo "Running pytest in $(pwd)"
pytest -q tests
