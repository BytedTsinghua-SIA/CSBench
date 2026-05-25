#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"

cd "$SCRIPT_DIR"

rm -rf build && mkdir -p build && cd build
cmake -DCMAKE_BUILD_TYPE=Debug ..
make -j2 count_min_sketch_test
cd ..

# Run the tests

echo "Running pytest in $(pwd)"
pytest -q tests
