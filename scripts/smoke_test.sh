#!/usr/bin/env bash
set -euo pipefail

repo_root=$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)
if [[ -f "$repo_root/.env" && "${CSBENCH_ENV_LOADED:-}" != "1" ]]; then
  if [[ ! -x "$repo_root/.venv/bin/python" ]]; then
    echo "Missing .venv; run scripts/bootstrap.sh first" >&2
    exit 2
  fi
  exec "$repo_root/.venv/bin/python" "$repo_root/scripts/env_exec.py" \
    --env-file "$repo_root/.env" "$repo_root/scripts/smoke_test.sh" "$@"
fi

harbor_bin="$repo_root/.venv/bin/harbor"
python_bin="$repo_root/.venv/bin/python"
task_id=${SMOKE_TASK:-cs000280}
smoke_agent=${SMOKE_AGENT:-nop}
smoke_image_template=${SMOKE_IMAGE_TEMPLATE:-}
if [[ -z "$smoke_image_template" ]]; then
  smoke_image_template='docker.io/honglifish/csbench:{task_id}'
fi
export CSBENCH_ROOT=${CSBENCH_ROOT:-$repo_root}
smoke_root="$repo_root/.smoke"
dataset_parent=$(mktemp -d -t csbench-harbor-smoke.XXXXXX)
trap 'rm -rf "$dataset_parent"' EXIT
dataset_dir="$dataset_parent/dataset"
jobs_dir="$smoke_root/jobs"
job_name="nonreportable-${smoke_agent}-${task_id}-$(date -u +%Y%m%dT%H%M%SZ)"

if [[ ! -x "$harbor_bin" ]]; then
  echo "Missing $harbor_bin; run scripts/bootstrap.sh first" >&2
  exit 2
fi
echo "NON-PAPER / NON-REPORTABLE Harbor smoke test"
echo "All artifacts stay under: $smoke_root"
echo "Image template: $smoke_image_template"
"$python_bin" "$repo_root/scripts/generate_dataset.py" \
  --csbench-root "$CSBENCH_ROOT" \
  --output-dir "$dataset_dir" \
  --image-template "$smoke_image_template" \
  --task "$task_id" \
  --overwrite

mkdir -p "$jobs_dir"
if [[ "$smoke_agent" == "nop" ]]; then
  (cd "$dataset_parent" && "$harbor_bin" run \
    --path "$dataset_dir" \
    --agent nop \
    --n-concurrent 1 \
    --jobs-dir "$jobs_dir" \
    --job-name "$job_name")
  exit 0
fi

if [[ "$smoke_agent" != "codeact" ]]; then
  echo "SMOKE_AGENT must be nop or codeact" >&2
  exit 2
fi
if [[ -z "${OPENAI_MODEL:-${API_MODEL:-}}" || -z "${OPENAI_API_KEY:-${API_KEY:-}}" ]]; then
  echo "OPENAI_MODEL/API_MODEL and OPENAI_API_KEY/API_KEY are required for the CodeAct smoke test" >&2
  exit 2
fi
(cd "$dataset_parent" && "$harbor_bin" run \
  --path "$dataset_dir" \
  --agent csbench_harbor.agent:CSBenchCodeActAgent \
  --model "${OPENAI_MODEL:-$API_MODEL}" \
  --n-concurrent 1 \
  --jobs-dir "$jobs_dir" \
  --job-name "$job_name")
