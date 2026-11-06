# CSBench

[简体中文](./README.md) | [English](./README.en.md)

CSBench is a Docker-based benchmark framework for academic computer science tasks. It evaluates coding agents on end-to-end, system-level fixing, implementation, and debugging workflows in real repositories.

The `main` branch is the complete Harbor-compatible release. It retains the original CSBench tasks, runner, evaluator, and documentation while also publishing the same tasks in Harbor task schema 1.4. Users can reproduce the paper's original CodeAct workflow or run Harbor built-in and custom agents without changing the task images.

The historical experiment implementation remains available on the `origin_experiment` branch. New users should start from `main`.

## Two Ways to Run CSBench

| Mode | Best for | Entry point |
|---|---|---|
| Harbor (recommended) | A standard harness, alternative agents/scaffolds, and future extensions | `scripts/run_harbor.sh` |
| Original CSBench runner | Exact reproduction of the original CodeAct prompt, tools, and loop | `main.py` / `run.py` |

Both modes use the task definitions under `tasks/` and the same Docker images. Harbor references the prebuilt images directly; no Harbor-specific image layer is required. See the [Harbor guide](docs/HARBOR.md) for the design, supported agents, and validation procedure.

## Harbor Quick Start

Requirements: Python 3.12+ and Docker with Compose v2.

```bash
git clone https://github.com/huiyeruzhou/HaneYuu.git CSBench
cd CSBench
scripts/bootstrap.sh
cp .env.example .env
```

After filling in the model endpoint in `.env`, run one task or the full dataset:

```bash
CSBENCH_TASK=cs000280 scripts/run_harbor.sh  # one task
scripts/run_harbor.sh                       # all tasks
```

You can also use a Harbor built-in agent directly. This example assumes that
the credentials required by that agent are already exported:

```bash
.venv/bin/harbor run \
  --path dataset/csbench \
  --include-task-name cs000280 \
  --agent mini-swe-agent \
  --model openai/gpt-5.2
```

Codex uses Harbor's built-in `--agent codex`; no CSBench-specific Codex agent
is required. If a container cannot reach the Codex installation sources,
configure `HTTP_PROXY` / `HTTPS_PROXY` in `.env`. The wrapper forwards them to
the setup and run phases through Harbor's official `--agent-env` option. See
the [Harbor guide](docs/HARBOR.md#codex-agent) for the complete command and
endpoint details.

`dataset/csbench/` contains ready-to-run Harbor tasks. `scripts/generate_dataset.py` can regenerate them from the original tasks included in this repository. Task images use `docker.io/honglifish/csbench:<task-id>`; the publication helper remains dry-run by default.

### Repeated attempts, concurrency, and job names

`scripts/run_harbor.sh` loads `.env` and forwards additional arguments to Harbor unchanged. `-k` is the number of attempts per task and `-n` is the global number of concurrent trials; both are official Harbor options:

```bash
# Run cs000280 twice, with at most 8 concurrent trials
CSBENCH_TASK=cs000280 \
CSBENCH_JOB_NAME=gpt52-mini \
scripts/run_harbor.sh -k 2 -n 8
```

Outputs go to `jobs/<job-name>/` by default. Use `CSBENCH_JOBS_DIR` to change the output root and `CSBENCH_AGENT` to select another agent. Give every reportable configuration a unique job name so smoke tests, models, and configurations remain isolated.

### View and summarize Harbor results

Use Harbor's official web viewer to inspect jobs, trials, agent trajectories, exceptions, and verifier output:

```bash
.venv/bin/harbor view jobs --jobs
```

The job-level `result.json` stores aggregate state; each trial directory has a `result.json` with the task, agent/model, tokens/cost, exceptions, and verifier reward. `verifier/reward.txt` is the raw binary score and `verifier/test-stdout.txt` contains test output. CSBench also provides a read-only helper that flattens the official JSON into CSV and aggregates pass rates by agent/model:

```bash
python3 scripts/summarize_harbor_results.py jobs/<job-name>
# Equivalent Make target
make summarize JOB=jobs/<job-name>
```

For one job, it writes `analysis/trials.csv` and `analysis/summary.json`; for a `jobs/` root, it writes `jobs/_analysis/`. Execution and web viewing are official Harbor CLI features; CSV/JSON summarization is a repository helper. `harbor analyze` is an optional, additional model-based trajectory analysis and is not required to compute benchmark scores.

See the [Harbor guide](docs/HARBOR.md) for the complete output tree, field semantics, and the boundary between official and repository tooling.

## Original CSBench Runner Quick Start

### Install Dependencies

If you already ran `scripts/bootstrap.sh`, its `.venv` contains the dependencies for both the Harbor adapter and the original runner. To reproduce the historical dependency set exactly (including the old `httpx` pin), use a separate environment so it cannot conflict with Harbor:

- Install with `uv`

```bash
uv venv .venv-original --python 3.13
source .venv-original/bin/activate            # Activate the original experiment environment
uv pip install -r requirements.txt            # Install the common project dependencies
```

- Install with `pip`

```bash
python -m venv .venv-original
source .venv-original/bin/activate
pip install -r requirements.txt               # Install the original experiment dependencies
```

`requirements-freeze.txt` is also provided as a reference freeze for reproducing the original experiment environment.

### Configure API Access

These variables are eventually passed into `litellm` initialization.
OpenAI-compatible providers such as OpenRouter do not require changing `PROVIDER`. But responses API of Azure models require changing `PROVIDER` to `azure`.

```sh
cat > .env <<EOF
PROVIDER="openai"
API_MODE="chat" # use "responses" for the latest GPT models
API_BASE="https://xxx/v1"
API_KEY="sk-xxxxxx"
API_MODEL="gpt-5.2"

OUTPUT_ROOT="."
DOCKER_REGISTRY="docker.io"
DOCKER_REPOSITORY="honglifish/csbench"
EOF
```

### Run the Benchmark

```bash
python3 main.py -n 3 -k 2             # Main entry: pull images from registry (no local build)
python3 read_report.py                # Summarize the existing results in reports/
```

By default, `main.py` performs these steps in order:

1. Prepare or reuse the Docker image for each task
2. Invoke `scripts.run_agent` to run the agent inside the container
3. Invoke `scripts.evaluate_patch` to replay the patch and run tests
4. Invoke `scripts.visualize_conversation` to generate a conversation visualization
5. Continuously write structured results into `reports/` and stage outputs into `logs/`

`read_report.py` does the following:

- Scan `reports/*.json`
- Locate the corresponding log directory by `task_name` and `attempt_id`
- Summarize failures in build / coldstart / run_agent / evaluate
- Check whether a patch is empty
- Count pass distributions across multiple attempts per task
- Print timeout, abnormal, and suspicious samples for inspection

After a run, the most useful places to check are:

- `logs/<task_name>/attempt<N>/`: execution logs, conversations, and patches
- `reports/<task_name>_attempt<N>.json`: structured result summaries
- `tasks/<task_name>/`: task source code and task metadata

### Test Multiple Models

The `ENV_FILE` environment variable can be used to point to a custom env file. To test multiple models, you can maintain files such as `.env.gpt` and `.env.glm`, then switch `ENV_FILE` before running.

The following two runs can execute in parallel as long as they use different `OUTPUT_ROOT` values:

```bash
export ENV_FILE=.env.gpt
python3 run.py -k 1

export ENV_FILE=.env.glm
python3 run.py -k 1
```

## Main Entry Points

### `main.py`

```bash
python3 main.py -n 10                           # Scan TASK_ROOT and run the first 10 tasks
python3 main.py -n 50 -x 8 -k 2                 # 8 workers, 2 attempts per task
python3 main.py --task cs000007                 # Run a single task
python3 main.py --task cs000007 -k 3            # Run 3 attempts for one task
python3 main.py --task "[cs000007,cs000008]"    # Run multiple explicit tasks
```

Parameter summary:

- `--task`: run a specific task; if omitted, the whole `TASK_ROOT` is scanned
- `-n` / `--num-tasks`: limit the number of tasks to run
- `-k` / `--pass-k`: number of attempts per task
- `-x`: number of concurrent workers; setting it too high can significantly increase CPU and memory pressure

`main.py` executes the following stages:

1. Prepare or reuse the Docker image for the task
2. Invoke `scripts.run_agent` to run the agent inside the container
3. Invoke `scripts.evaluate_patch` to replay the patch and run tests
4. Invoke `scripts.visualize_conversation` to generate an HTML visualization
5. Continuously write reports into `reports/` and stage outputs into `logs/`

Public images use the shared-repository layout resolved from `DOCKER_REGISTRY` / `DOCKER_REPOSITORY` in `.env`. Leave `DOCKER_REPOSITORY` empty to restore the historical namespace/task layout.

Engineering details:

- Uses threads and shared state to avoid repeating the “image preparation” stage across attempts
- Writes stdout/stderr of each step to files to avoid long-running subprocesses getting stuck on pipes
- Tries to stop unfinished tasks gracefully on Ctrl+C
- Uses a live panel to show the status of concurrent tasks

### `run.py`

`run.py` is the local-build entry: it stages a build context and runs docker build via `scripts/build_image.py`, then runs a coldstart check (`test.sh`) before continuing with agent/evaluation. Use this when you need to build or rebuild images locally.

```bash
python3 run.py --task cs000007 --force-build
```

### `read_report.py`

```bash
python3 read_report.py
```

It reads all results under `reports/` and `logs/` and summarizes them.

It includes:

- Scanning `reports/*.json`
- Resolving the matching log directory by `task_name` and `attempt_id`
- Summarizing failures in build / coldstart / run_agent / evaluate
- Checking whether patches are empty
- Aggregating pass distributions across multiple attempts
- Printing timeout, abnormal, and suspicious cases for debugging

Common commands:

```bash
python3 read_report.py                         # Read the default reports/ directory
python3 read_report.py --report reports        # Explicitly choose a report directory
python3 read_report.py --attempts 2            # Aggregate results assuming 2 attempts per task
```

### `.env` Configuration

The project automatically reads `.env` at startup. A typical configuration looks like this:

```env
# TASK_ROOT=tasks
# OUTPUT_ROOT=.
# BUILD_ROOT=build
# DOCKER_REGISTRY=docker.io
# DOCKER_REPOSITORY=honglifish/csbench

PROVIDER=openai
API_KEY=your_key
API_MODEL=your_model
API_BASE=
```

Common config fields:

- `TASK_ROOT`: root directory for tasks
- `OUTPUT_ROOT`: output root; logs and reports will be stored under `<OUTPUT_ROOT>/logs/` and `<OUTPUT_ROOT>/reports/`
- `BUILD_ROOT`: cache/staging directory used during local Docker image builds
- `DOCKER_REGISTRY`: Docker registry hostname
- `DOCKER_REPOSITORY`: shared repository used by the public release; each task uses its task ID as the tag. The default example resolves to `docker.io/honglifish/csbench:cs000007`
- `DOCKER_NAMESPACE` / `DOCKER_TAG`: used only when `DOCKER_REPOSITORY` is empty, preserving the historical `<registry>/<namespace>/<task>:<tag>` layout
- `PROVIDER` / `OPENAI_*`: LLM provider and model configuration; keep the `OPENAI_` prefix even when using non-OpenAI providers, because these variables are consumed by `litellm`

## Directory Conventions

### `tasks/` (`TASK_ROOT`)

`tasks/` contains the benchmark data itself. A typical task looks like this:

```text
tasks/<task_name>/
  src/
  metadata/
  entry_list.txt   # optional legacy artifact; current code no longer reads it
```

Where:

- `src/`: task source code copied into `/testbed` inside the image
- `metadata/task.md`: task description read by the agent
- `metadata/Dockerfile`: task-specific image definition
- `metadata/test_override/`: test files restored during evaluation to prevent test tampering
- `entry_list.txt`: legacy image/base-commit mapping file; the current runtime path no longer depends on it

### `logs/` (`OUTPUT_ROOT/logs/`)

`logs/` stores the full execution history of each attempt. A typical structure is:

```text
logs/<task_name>/attempt<N>/
  1.docker_build.out
  1.docker_build.err
  2.coldstart.out              # produced only by `run.py` (local-build path)
  2.coldstart.err
  3.run_agent.out
  3.run_agent.err
  4.evaluate.out
  4.evaluate.err
  5.transform.out
  5.transform.err
  conversation_history.json
  patch
  testbed.zip                 # Only generated with --archive-testbed
```

The most important files are:

- `conversation_history.json`: full conversation trace
- `patch`: final git patch generated by the agent
- `*.out` / `*.err`: stdout and stderr of each stage
- `testbed.zip`: optional snapshot of the evaluation workspace

### `reports/` (`OUTPUT_ROOT/reports/`)

`reports/` stores structured results, one JSON file per attempt:

```text
reports/<task_name>_attempt<N>.json
```

These files usually record:

- Whether each stage succeeded
- Per-stage durations
- Stdout/stderr summaries
- Final evaluation result

### `build/` (`BUILD_ROOT`)

`build/` is the Docker build staging directory. Each task generates:

```text
build/<task_name>/
build/<task_name>.lock
```

Their meanings are:

- `build/<task_name>/`: staged Docker build context
- `build/<task_name>.lock`: lock file to prevent concurrent builds of the same task

## `scripts/` Modules

This directory contains helper scripts that can also be executed independently.

### `scripts/build_image.py`

Basic usage:

```bash
python3 -m scripts.build_image <task_name>
```

Common commands:

```bash
python3 -m scripts.build_image cs000007                   # Build the image locally
python3 -m scripts.build_image cs000007 --force           # Force rebuild the image
python3 -m scripts.build_image cs000007 --use-pip-mirror  # Enable a pip mirror during build
python3 -m scripts.build_image cs000007 --push            # Push the image after a successful build
```

### `scripts/run_agent.py`

Basic usage:

```bash
python3 -m scripts.run_agent code_act_agent <task_name> <log_tag>
```

Common commands:

```bash
python3 -m scripts.run_agent code_act_agent cs000007 attempt0  # Run one standalone agent attempt
```

### `scripts/evaluate_patch.py`

Basic usage:

```bash
python3 -m scripts.evaluate_patch <task_name> <attempt_id>
```

Common commands:

```bash
python3 -m scripts.evaluate_patch cs000007 0                    # Replay a patch and run tests
python3 -m scripts.evaluate_patch cs000007 0 --archive-testbed  # Also export testbed.zip for debugging
```

### `scripts/visualize_conversation.py`

Basic usage:

```bash
python3 -m scripts.visualize_conversation <conversation_history.json>
```

Common commands:

```bash
python3 -m scripts.visualize_conversation logs/cs000007/attempt0/conversation_history.json  # Convert to HTML
```

## Source Architecture

### How to Read the Code (Recommended Order)

1. Start with `run.py`: it is a “state management + CLI driver”. Each stage (build/coldstart/run_agent/evaluate/transform) is wrapped as a Runner step with status tracking, reusability, and concurrent execution. It also persists stdout/stderr into `logs/` and writes structured results into `reports/`. `main.py` reuses this Runner/UI/concurrency layer and only swaps the image-preparation stage for pull.
2. Then read `scripts/`: these are the actual subprocess entrypoints that do the real work (e.g., `scripts.run_agent`, `scripts.evaluate_patch`).
3. Finally `src/`: abstractions such as `BenchTask`/runtime/agents that map tasks to images/repos, wrap container operations, and provide pluggable agent workflows.

### `main.py` vs `run.py`

- `main.py`: pull-image entry (default). Reuses `run.py` Runner/UI/logging, but replaces the image stage with `docker pull`; it also skips coldstart (marks it as success).
- `run.py`: local-build entry. Builds images and runs coldstart, suitable for image authoring/updating.

### Why `run.py` Exists (Design Rationale)

You can run the pipeline with a few commands (prepare image → run agent → replay patch → run tests). But you would lose what matters for benchmark runs: concurrency scheduling, cross-attempt shared setup, robust subprocess handling and Ctrl+C shutdown, per-step stdout/stderr persistence, live status UI, and structured `reports/` for automated summarization.

### `src/config.py`

Centralizes global paths and environment variables, such as:

- `TASK_ROOT`
- `OUTPUT_ROOT`
- `BUILD_ROOT`
- `DOCKER_REGISTRY`
- `DOCKER_REPOSITORY`
- `DOCKER_NAMESPACE`
- `DOCKER_TAG`

### `src/task/`

Task abstraction layer. `BenchTask` is responsible for:

- Reading `metadata/task.md`
- Resolving the public shared-repository image from `DOCKER_REGISTRY` / `DOCKER_REPOSITORY`, while retaining compatibility with the historical `DOCKER_NAMESPACE` / `DOCKER_TAG` layout
- Running `git rev-parse HEAD` inside the image and treating `/testbed`'s `HEAD` as the task's `base_commit`
- Providing log-directory and task-related helper paths

### `src/runtime/`

Container runtime abstraction. `LocalDockerContainerRuntime` handles:

- Starting and stopping Docker containers
- Executing commands inside containers
- Copying files between host and container
- Supporting more advanced interactive screen / attach workflows

### `src/agents/`

Agent implementation, roughly split into three layers:

- `workflows/`: workflow orchestration
- `tools/`: tools available to the agent
- `utils/llm.py`: LLM configuration and integration

## FAQ

### What if the build is stuck on a lock?

The lock file is usually at `build/<task_name>.lock`. If you are sure no matching build process is still running, you can remove that file manually.

### How do I switch task directories, output directories, or Docker registry settings?

Edit `.env`, for example:

```env
TASK_ROOT=/path/to/tasks
OUTPUT_ROOT=/path/to/output
BUILD_ROOT=/path/to/build-root
DOCKER_REGISTRY=your-registry.example.com
DOCKER_REPOSITORY=your-namespace/csbench
```
