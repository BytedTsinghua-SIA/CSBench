#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"

cd "$SCRIPT_DIR"

cd datasets && tar -xzvf cifar-10-python.tar.gz
cd ..

echo "Running pytest in $(pwd)"
pytest -q tests
