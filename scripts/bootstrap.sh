#!/usr/bin/env bash
set -euo pipefail

repo_root=$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)
csbench_root=${CSBENCH_ROOT:-$repo_root}
python_bin=${PYTHON:-python}

if [[ ! -f "$csbench_root/requirements.txt" ]]; then
  echo "CSBENCH_ROOT is not a CSBench checkout: $csbench_root" >&2
  exit 2
fi

"$python_bin" - <<'PY'
import sys
if sys.version_info < (3, 12):
    raise SystemExit(
        f"Python 3.12+ is required by Harbor; got {sys.version.split()[0]}"
    )
PY

"$python_bin" -m venv --clear "$repo_root/.venv"
"$repo_root/.venv/bin/python" -m pip install --upgrade pip

if [[ -n "${HARBOR_SOURCE:-}" ]]; then
  "$repo_root/.venv/bin/python" -m pip install -e "$HARBOR_SOURCE"
else
  "$repo_root/.venv/bin/python" -m pip install 'harbor>=0.20,<0.21'
fi
"$repo_root/.venv/bin/python" -m pip install -e "$repo_root"
"$repo_root/.venv/bin/python" -m pip install 'httpx[socks]>=0.27' pytest

echo "Environment ready: $repo_root/.venv"
echo "CSBench source: $csbench_root"
echo "Copy .env.example to .env and fill in model credentials."
