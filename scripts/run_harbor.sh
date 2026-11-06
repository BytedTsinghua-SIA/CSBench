#!/usr/bin/env bash
set -euo pipefail

repo_root=$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)
if [[ -f "$repo_root/.env" && "${CSBENCH_ENV_LOADED:-}" != "1" ]]; then
  if [[ ! -x "$repo_root/.venv/bin/python" ]]; then
    echo "Missing .venv; run scripts/bootstrap.sh first" >&2
    exit 2
  fi
  exec "$repo_root/.venv/bin/python" "$repo_root/scripts/env_exec.py" \
    --env-file "$repo_root/.env" "$repo_root/scripts/run_harbor.sh" "$@"
fi

harbor_bin="$repo_root/.venv/bin/harbor"
dataset_dir=${CSBENCH_DATASET_DIR:-$repo_root/dataset/csbench}
jobs_dir=${CSBENCH_JOBS_DIR:-$repo_root/jobs}
export CSBENCH_ROOT=${CSBENCH_ROOT:-$repo_root}
agent=${CSBENCH_AGENT:-csbench_harbor.agent:CSBenchCodeActAgent}
model=${OPENAI_MODEL:-${API_MODEL:-}}
concurrency=${CSBENCH_CONCURRENCY:-4}
task_id=${CSBENCH_TASK:-}
job_name=${CSBENCH_JOB_NAME:-csbench-harbor-$(date -u +%Y%m%dT%H%M%SZ)}
task_args=()
proxy_args=()

if [[ "$dataset_dir" != /* ]]; then
  dataset_dir="$repo_root/$dataset_dir"
fi
if [[ "$jobs_dir" != /* ]]; then
  jobs_dir="$repo_root/$jobs_dir"
fi

if [[ ! -x "$harbor_bin" ]]; then
  echo "Missing $harbor_bin; run scripts/bootstrap.sh first" >&2
  exit 2
fi
if [[ -z "$model" ]]; then
  echo "Set OPENAI_MODEL or API_MODEL before running Harbor" >&2
  exit 2
fi
if [[ -n "$task_id" ]]; then
  task_args=(--include-task-name "$task_id")
fi
if [[ "$agent" == "codex" ]]; then
  if [[ -z "${OPENAI_API_KEY:-}" && -n "${API_KEY:-}" ]]; then
    export OPENAI_API_KEY=$API_KEY
  fi
  codex_base_url=${OPENAI_BASE_URL:-${OPENAI_API_BASE:-${API_BASE:-}}}
  if [[ "$codex_base_url" == */responses ]]; then
    codex_base_url=${codex_base_url%/responses}
  fi
  if [[ -n "$codex_base_url" ]]; then
    export OPENAI_BASE_URL=$codex_base_url
  fi
fi
for proxy_name in HTTP_PROXY HTTPS_PROXY ALL_PROXY http_proxy https_proxy all_proxy; do
  if [[ -n "${!proxy_name:-}" ]]; then
    # Keep the persisted Harbor config referential: Harbor resolves this value
    # from the host environment instead of copying a proxy URL into config.json.
    proxy_args+=(--agent-env "$proxy_name=\${$proxy_name}")
  fi
done
if [[ ! -f "$dataset_dir/dataset_manifest.csv" ]]; then
  echo "Harbor task/dataset not found: $dataset_dir" >&2
  exit 2
fi

mkdir -p "$jobs_dir"
cd "${TMPDIR:-/tmp}"
exec "$harbor_bin" run \
  --path "$dataset_dir" \
  --agent "$agent" \
  --model "$model" \
  --n-concurrent "$concurrency" \
  --jobs-dir "$jobs_dir" \
  --job-name "$job_name" \
  "${proxy_args[@]}" \
  "${task_args[@]}" \
  "$@"
