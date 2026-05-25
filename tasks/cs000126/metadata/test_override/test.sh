#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

export PYTHONPATH="$SCRIPT_DIR${PYTHONPATH:+:$PYTHONPATH}"

echo "Running pytest in $(pwd)"

if [[ $# -gt 0 ]]; then
  pytest "$@"
else
  pytest -q tests
fi