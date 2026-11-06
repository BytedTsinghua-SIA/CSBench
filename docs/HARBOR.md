# Running CSBench with Harbor

[简体中文](HARBOR.zh-CN.md) | [English](HARBOR.md)

This repository includes both the original CSBench implementation and support for the official
[Harbor](https://github.com/laude-institute/harbor) harness while preserving
the original benchmark images and CodeAct agent behavior.

It contains three pieces:

1. a Harbor external-agent adapter for CSBench's original CodeAct workflow;
2. a converter from the CSBench task release to Harbor task schema 1.4;
3. a guarded release script that retags and pushes the original images without
   rebuilding them.

## Image compatibility

Harbor can run a prebuilt image directly through `[environment].docker_image`.
At runtime it creates/mounts `/logs`, uploads verifier files to `/tests`, and
sets the configured working directory. CSBench images already use `/testbed`,
contain a Git checkout there, and provide `sh` and `bash`. No Harbor-specific
image layer is required.

The release mapping is therefore one-to-one:

```text
<existing-source-repository>/cs000003:latest
    -> docker.io/honglifish/csbench:cs000003
```

`scripts/publish_images.py` only calls `docker image inspect`, `docker image
tag`, and `docker image push`; it contains no build command. It verifies that
the local image ID is unchanged after tagging.

## Install

Requirements:

- Python 3.12+
- Docker with Compose v2
- Harbor 0.20.x
- the CSBench tasks and runner included in this repository

```bash
git clone https://github.com/huiyeruzhou/HaneYuu.git CSBench
cd CSBench
scripts/bootstrap.sh
cp .env.example .env
```

Edit `.env` to set the model endpoint. `CSBENCH_ROOT` defaults to this checkout;
no second copy of CSBench is needed. `HARBOR_SOURCE` may
point to a local Harbor checkout when testing against an unreleased Harbor
revision; otherwise the bootstrap script installs the supported PyPI release.
The bootstrap deliberately keeps Harbor's current `httpx` dependency instead
of CSBench's historical `httpx==0.23.1` pin; the CodeAct API used here is
compatible with the newer client, while downgrading it would break Harbor's
dependency contract.

The wrapper understands the following release defaults:

| Variable | Meaning |
|---|---|
| `API_MODEL`, `API_KEY`, `API_BASE`, `PROVIDER` | Model name and endpoint for the original CSBench adapter |
| `CSBENCH_DATASET_DIR` | Harbor dataset path; default `dataset/csbench` |
| `CSBENCH_JOBS_DIR` | Result root; default `jobs` |
| `CSBENCH_CONCURRENCY` | Default concurrent trials; default `4` |
| `CSBENCH_AGENT` | Agent name/import path; default is the CSBench CodeAct adapter |
| `CSBENCH_TASK` | Optional task ID such as `cs000280` |
| `CSBENCH_JOB_NAME` | Optional stable output job name |

`OPENAI_MODEL`, `OPENAI_API_KEY`, and `OPENAI_API_BASE` are accepted aliases
for integrations that use standard OpenAI-compatible environment names.
Harbor's built-in Codex agent uses `OPENAI_API_KEY` and `OPENAI_BASE_URL`.
Never commit the populated `.env` file.

## Generate the Harbor dataset

The converter is offline: it does not invoke Docker or access the network.

```bash
.venv/bin/python scripts/generate_dataset.py --overwrite
```

Each generated task contains:

```text
cs000280/
├── environment/
│   └── .harbor-environment-placeholder
├── instruction.md
├── task.toml
└── tests/
    ├── test.sh
    └── test_override/...
```

Harbor 0.20 requires the `environment/` directory even when `docker_image`
selects a prebuilt image. Git cannot retain an empty directory, so the release
contains a zero-byte hidden placeholder. Harbor may copy it into `/testbed`;
the CSBench agent setup and verifier remove it immediately. It does not create
an image layer or trigger an image build.

The verifier restores `test.sh` and `tests/` from the task's base commit,
applies the released test override, runs the original `test.sh`, and writes the
binary reward to `/logs/verifier/reward.txt`. This matches the original
fresh-container evaluator's protected-test behavior.

## Run

Set the same model endpoint variables used by CSBench, then point Harbor at the
external agent class:

```bash
export OPENAI_API_KEY=...
export OPENAI_API_BASE=...
export PROVIDER=openai
export MODEL_MAX_TOKENS=32768
export MAX_TURNS=50
export CSBENCH_TEMPERATURE=1.0

.venv/bin/harbor run \
  --path dataset/csbench \
  --agent csbench_harbor.agent:CSBenchCodeActAgent \
  --model gpt-5.2 \
  --n-concurrent 4
```

For a one-task local-dataset run, add `--include-task-name cs000280`. Harbor
adds the dataset source prefix in stored results, where the same task appears
as `csbench/cs000280`.

The generated tasks are standard Harbor tasks, so they can also be evaluated
with Harbor's built-in agents independently of the CSBench adapter, for example:

```bash
.venv/bin/harbor run -p dataset/csbench \
  --include-task-name cs000280 \
  --agent mini-swe-agent \
  --model openai/gpt-5.2
```

Use `--agent csbench_harbor.agent:CSBenchCodeActAgent` only when reproducing
the original CSBench prompt, tools, and turn loop. Built-in Harbor agents may
have their own installation extras and credential requirements.

### Agent/scaffold choices exposed by Harbor 0.20

The Harbor 0.20 CLI currently exposes the following relevant built-in choices.
This list describes harness interoperability, not agents individually validated
by this repository:

- general coding loops: `aider`, `cline-cli`, `deerflow`, `goose`, `langgraph`,
  `mini-swe-agent`, `opencode`, `openhands`, `openhands-sdk`, `swe-agent`,
  `terminus`, `terminus-1`, `terminus-2`, and `trae-agent`;
- model/vendor coding CLIs: `antigravity-cli`, `claude-code`, `codex`,
  `copilot-cli`, `cursor-cli`, `gemini-cli`, `kimi-cli`, `qwen-coder`, and
  `rovodev-cli`;
- other packaged agents: `computer-1`, `devin`, `dspy-rlm`, `eve`,
  `grok-build`, `hermes`, `mimo`, `nemo-agent`, `nop`, `openclaw`, `oracle`,
  `pi`, and `vibe`.

Harbor also accepts a custom Python import path (`module.path:ClassName`) and
ACP registry shorthands (`acp:<agent>`). Names in this list describe interfaces
exposed by Harbor 0.20, not agents individually installed or validated here.

### Codex agent

CSBench neither provides nor requires a custom Codex adapter. Harbor's built-in
`codex` agent installs the official Codex CLI, runs the task, and records its
native trajectory in ATIF. The standard wrapper invocation is:

```bash
CSBENCH_AGENT=codex \
CSBENCH_TASK=cs000003 \
scripts/run_harbor.sh -k 1 -n 1 \
  --agent-kwarg reasoning_effort=medium \
  --agent-kwarg web_search=disabled
```

When Harbor is invoked directly, its official Codex adapter reads
`OPENAI_API_KEY` and optionally `OPENAI_BASE_URL` from the host environment;
the model comes from `--model`. `OPENAI_BASE_URL` should be the API root and
should not include the `/responses` path that Codex appends. As alternatives,
Harbor accepts `CODEX_AUTH_JSON_PATH`, or `CODEX_FORCE_AUTH_JSON=true` to reuse
the host's `~/.codex/auth.json`.

Harbor's `--env-file` loads `.env` into the host process. Network proxies that
must reach agent setup and execution should be passed with the official
`--agent-env` / `--ae` option. With the wrapper, set `HTTP_PROXY` and
`HTTPS_PROXY` (or their lowercase forms) in `.env`; the wrapper forwards them.
The equivalent direct Harbor command is below. The single quotes let Harbor
resolve the values from the host environment instead of persisting proxy URLs
in the job configuration:

```bash
.venv/bin/harbor run \
  --path dataset/csbench \
  --include-task-name cs000003 \
  --env-file .env \
  --agent codex \
  --model gpt-5.3-codex \
  --agent-env 'HTTP_PROXY=${HTTP_PROXY}' \
  --agent-env 'HTTPS_PROXY=${HTTPS_PROXY}' \
  --agent-kwarg reasoning_effort=medium \
  --agent-kwarg web_search=disabled
```

Omit the two proxy arguments when no proxy is configured. Add `--install-only`
for a zero-model-call installation check. On an unchanged `cs000003` image,
Harbor 0.20's built-in `codex` completed installation in about one minute with
zero exceptions using only these proxy arguments; no image rebuild or
repository-defined Python agent was needed.

For compatibility with the original CSBench `.env`, `scripts/run_harbor.sh`
maps `API_KEY` / `API_BASE` to the standard variables Codex expects and removes
a trailing `/responses` from `API_BASE`. This is only an entry-point
convenience; direct Harbor use should prefer the official variables above.

### Repeated attempts and concurrency

`scripts/run_harbor.sh` loads `.env`, selects stable CSBench defaults, and then
forwards all additional arguments to the official CLI. Harbor's `-k` controls
attempts per task and `-n` controls the global number of concurrent trials:

```bash
CSBENCH_TASK=cs000280 \
CSBENCH_JOB_NAME=gpt52-mini \
scripts/run_harbor.sh -k 2 -n 8
```

The equivalent direct options are `--n-attempts 2` and `--n-concurrent 8`.
Set `CSBENCH_JOBS_DIR` to change the output root and `CSBENCH_AGENT` to select
another agent. Use a unique job name for every model/configuration that will be
compared.

## Results: format, viewing, and analysis

Harbor owns the on-disk result format. A completed job has this shape:

```text
jobs/<job-name>/
├── config.json
├── lock.json
├── result.json                 # job counts, evals, tokens, and cost
├── job.log
└── <trial-name>/
    ├── config.json
    ├── lock.json
    ├── result.json             # task, agent/model, timings, reward, exception
    ├── trial.log
    ├── artifacts/manifest.json
    └── verifier/
        ├── reward.txt          # raw CSBench reward: 1 or 0
        └── test-stdout.txt     # raw test output
```

The job-level `result.json` includes `n_total_trials` and `stats`, including
completed/errored trial counts, `evals`, token totals, and `cost_usd`. The
trial-level `result.json` includes `task_name`, `agent_info`, `agent_result`,
`verifier_result`, `exception_info`, timestamps, and per-stage results. For
CSBench, `verifier_result.rewards.reward == 1` means the canonical task tests
passed; `0` means they did not. Exceptions are recorded separately and should
not be inferred from reward alone.

Use the official Harbor viewer for interactive inspection:

```bash
.venv/bin/harbor view jobs --jobs
# Harbor prints the selected local URL; the default port range starts at 8080.
```

Use the repository's read-only exporter for numeric summaries and tables:

```bash
python3 scripts/summarize_harbor_results.py jobs/<job-name>
make summarize JOB=jobs/<job-name>  # equivalent shortcut
```

For a single job it creates `analysis/trials.csv` and
`analysis/summary.json`. For a jobs root it creates `_analysis/` and aggregates
all direct child jobs. The CSV has one row per trial; the JSON reports trials,
scored trials, passes, pass rate, mean reward, exceptions, tokens, and cost,
both overall and by agent/model. The exporter never changes or uploads a job.

Tool ownership is intentionally explicit:

- Official Harbor: `harbor run` / `harbor job start`, `harbor view`, job and
  trial `result.json`, logs, and verifier artifacts.
- CSBench helpers: `scripts/run_harbor.sh` for configuration, `smoke_test.sh`
  for isolated validation, and `summarize_harbor_results.py` for CSV/JSON.
- Optional official feature: `harbor analyze <job-or-trial>` asks another
  model to analyze trajectories. It can consume API budget and is not required
  for scoring or aggregation. `harbor upload` writes results to an external
  service and is never called by the repository helpers.

Do not combine `.smoke/jobs/` with reportable jobs. A `nop` smoke trial should
normally receive reward 0 because it makes no code change; zero exceptions is
the relevant signal that task loading, the container, and the verifier worked.

The repository also provides stable entry points:

```bash
make generate
make smoke TASK=cs000280        # Harbor/container/verifier path, no model call
make smoke-agent TASK=cs000280  # one real CSBench CodeAct trial
make harbor-run                  # settings from .env
```

Smoke tests use `docker.io/honglifish/csbench:<task-id>` by default. To test
an equivalent local mirror, explicitly select its unchanged-image mapping:

```bash
SMOKE_IMAGE_TEMPLATE='registry.example/csbench/{task_id}:latest' \
make smoke TASK=cs000280
```

Smoke-test jobs are deliberately isolated under the gitignored `.smoke/`
directory and are marked `NON-PAPER / NON-REPORTABLE`. They must not be merged
with benchmark results or used in paper tables.

## Prepare Docker Hub release

Authenticate separately with Docker; this repository never reads or stores a
registry password. The command below is a dry run and performs no Docker
operation:

```bash
python scripts/publish_images.py \
  --source-repository registry.example/csbench
```

Actual publication is intentionally guarded and should only be run during the
release process. Execute mode refuses every target except
`docker.io/honglifish/csbench`:

```bash
python scripts/publish_images.py \
  --source-repository registry.example/csbench \
  --execute \
  --confirm-target docker.io/honglifish/csbench
```
