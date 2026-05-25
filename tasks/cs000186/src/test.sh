#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"

cd "$SCRIPT_DIR"

rm -rf build && mkdir -p build && cd build
cmake -DCMAKE_BUILD_TYPE=Debug ..
make -j2 arc_replacer_test disk_scheduler_test page_guard_test buffer_pool_manager_test
cd ..

# Run the tests

echo "Running pytest in $(pwd)"
pytest -q tests
