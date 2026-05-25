#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"

cd "$SCRIPT_DIR"

# Dependencies are already installed in Dockerfile
echo "Running pytest in $(pwd)"
pytest -q tests