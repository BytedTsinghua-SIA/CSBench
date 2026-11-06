set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
export PYTHONPATH="${SCRIPT_DIR}:${PYTHONPATH:-}"

cd "$SCRIPT_DIR"

# Run pytest with warnings disabled
echo "Running pytest in $(pwd)"
pytest -q tests