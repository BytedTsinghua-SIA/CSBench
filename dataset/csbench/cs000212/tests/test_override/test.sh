set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
# Set PYTHONPATH to parent directory to allow importing from src package
PARENT_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"
export PYTHONPATH="${PARENT_DIR}:${PYTHONPATH:-}"

cd "$SCRIPT_DIR"

# Run pytest with warnings disabled
echo "Running pytest in $(pwd)"
pytest -q tests