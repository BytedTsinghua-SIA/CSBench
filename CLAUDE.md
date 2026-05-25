# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Overview

CSBench is a Docker-based benchmark system for evaluating AI coding agents on academic computer science tasks. The system follows a three-phase workflow: **build → run → evaluate**.

## Common Commands

### Environment Setup
```bash
# Install dependencies
pip install -r requirements.txt

# Configure environment (copy .env.example to .env and edit)
cp .env.example .env
# Edit .env to set PROVIDER, API_KEY, API_MODEL, API_BASE
```

### Building Docker Images
```bash
# Build a single task's Docker image (stores locally by default)
python3 -m scripts.build_image <task_name>

# Force rebuild even if image exists
python3 -m scripts.build_image <task_name> --force

# Push after a successful build
python3 -m scripts.build_image <task_name> --push

# Example
python3 -m scripts.build_image cs000007
```

### Running Agent on Tasks
```bash
# Run agent on a specific task with a log tag
python3 -m scripts.run_agent code_act_agent <task_name> <log_tag>

# Example
python3 -m scripts.run_agent code_act_agent cs000007 attempt0
```

### Evaluating Results
```bash
# Evaluate a specific attempt (applies patch and runs tests)
python3 -m scripts.evaluate_patch <task_name> <attempt_id>

# Evaluate and export /testbed to testbed.zip for debugging
python3 -m scripts.evaluate_patch <task_name> <attempt_id> --archive-testbed

# Example (evaluates attempt0 for cs000007)
python3 -m scripts.evaluate_patch cs000007 0
```

### Orchestrated Runs
```bash
# Default entry: pull images from registry, then run/evaluate
python3 main.py -n 10 -k 3

# Run a single task end-to-end (build → run → evaluate)
python3 run.py --task <task_name> --attempt-id <attempt_id>

# Run multiple tasks with pass@k evaluation
python3 run.py -n 10 -k 3  # First 10 tasks, 3 attempts each

# Run all tasks
python3 run.py
```

### Visualization
```bash
# Convert conversation history to human-readable format
python3 -m scripts.visualize_conversation logs/<task_name>/attempt<N>/conversation_history.json
```

### Cleanup
```bash
# Remove all build directories (staging dirs for Docker builds)
make clean
```

## Architecture

### Core Components

**Tasks** (`tasks/`, `tasks0105/`, etc.): Each task directory (e.g., `cs000001`) contains:
- `src/`: Source code copied into Docker container at `/testbed/`
- `metadata/Dockerfile`: Container environment definition
- `metadata/task.md`: Task instructions given to the agent
- `metadata/test_override/`: Test files restored after agent runs (prevents tampering)
- `entry_list.txt`: Legacy image/base-commit mapping file; current runtime code no longer depends on it

**Agents** (`src/agents/`): LLM-based workflows that solve tasks:
- `workflows/CodeActWorkflow`: Main implementation using tool-calling pattern
- `tools/`: ExecuteBashTool, StrReplaceTool, FinishTool

**Runtime** (`src/runtime/`): Container interaction layer:
- `LocalDockerContainerRuntime`: Manages Docker containers via `docker exec` and `docker cp`

### Three-Phase Workflow

1. **Build Phase** (`scripts/build_image.py`):
   - Stages build context: copies `src/` to `BUILD_ROOT/{task_name}/`
   - Runs `docker build --platform linux/amd64`
   - Uses `BUILD_ROOT/{task_name}.lock` to prevent concurrent builds

2. **Run Phase** (`main.py` / `run.py` + `scripts/run_agent.py`):
   - `main.py` pulls a prebuilt image and skips coldstart
   - `run.py` builds the image locally and runs coldstart before continuing
   - Starts Docker container with task image
   - Loads task instructions from `metadata/task.md`
   - Runs agent workflow (max 50 turns)
   - Generates git patch: `git diff --cached <base_commit> --binary --full-index`
   - Saves conversation and patch to `logs/{task_name}/attempt{N}/`

3. **Evaluation Phase** (`scripts/evaluate_patch.py`):
   - Starts fresh container from same image
   - Applies git patch using `git apply --3way`
   - Restores test files from `metadata/test_override/`
   - Runs `bash test.sh` (1800s timeout)
   - Returns pass/fail based on exit code

### Configuration

Environment variables (`.env` file):
- `PROVIDER`: LLM provider (e.g., "openai", "anthropic")
- `API_KEY`: API key for LLM
- `API_MODEL`: Model name
- `API_BASE`: Optional API base URL
- `OUTPUT_ROOT`: Directory for logs/reports (default: ".")
- `TASK_ROOT`: Directory containing tasks (default: "tasks")
- `BUILD_ROOT`: Directory containing staged Docker build contexts (default: "build")
- `DOCKER_REGISTRY`: Docker registry hostname (default: "docker.io")
- `DOCKER_NAMESPACE`: Docker namespace/project (default: "honglifish/csbench")
- `DOCKER_TAG`: Docker image tag (default: "latest")

Paths managed by `src/config.py`:
- `logs/{task_name}/attempt{N}/`: Conversation history, patches, command outputs
- `reports/{task_name}_attempt{N}.json`: Execution metadata

### Agent Tool Architecture

The agent interacts with containers through three tools:

**ExecuteBashTool**: Executes shell commands via `docker exec -i container bash -lc "command"`
- Output truncated to 25,600 characters
- Each command runs in login shell with full environment

**StrReplaceTool**: Views/creates/edits files using string replacement
- Operations in Python memory (not sed)
- Files transferred via `docker cp`
- Supports: create, view, str_replace, insert, undo_edit

**FinishTool**: Signals task completion

### Parallel Execution Pattern

`run.py` orchestrator manages multiple tasks × attempts:
- ThreadPoolExecutor with max 24 workers
- Task-level shared state prevents duplicate setup work
- File-based locks for image building
- Graceful shutdown via global `STOP_EVENT`
- Real-time status display using Rich library

### Key Design Patterns

**Docker Isolation**: All tasks run in isolated `linux/amd64` containers for reproducibility

**Git-Based Patches**: All agent changes captured as binary-aware git patches, excluding build artifacts (*.o, *.pyc, etc.)

**Tool Call Truncation**: Workflow enforces one tool call per turn by truncating multiple calls

**Output Truncation**: Command outputs limited to 25,600 characters to prevent context overflow

**Test Security**: Files in `metadata/test_override/` restored after agent runs to prevent tampering

**Content Preservation**: File operations use `docker cp` instead of shell commands to avoid encoding issues

## Development Workflow

When modifying the codebase:

1. **Agent workflows** are in `src/agents/workflows/` - modify these to change agent behavior
2. **Tools** are in `src/agents/tools/` - add new tools here for agent capabilities
3. **Runtime** is in `src/runtime/` - modify for different container backends
4. **Task loading** is in `src/task/bench_task.py` - handles task metadata
5. **Scripts** are entry points - modify for orchestration changes

The system uses litellm for LLM API calls, supporting multiple providers through unified interface.
