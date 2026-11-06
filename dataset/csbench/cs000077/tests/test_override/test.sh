#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

export CSBENCH_SRC_DIR="${CSBENCH_SRC_DIR:-$SCRIPT_DIR}"

cd "${SCRIPT_DIR}"
pytest -q tests
