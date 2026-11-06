# AI Assistant Guide

Read `AGENTS.md` before making changes. It is the authoritative set of
repository-wide instructions; this file is a concise entry point for assistants
that discover `CLAUDE.md` automatically. Using this repository does not require
Claude or any particular model provider.

## Purpose and architecture

The `main` branch is the Harbor-compatible CSBench release. It retains the
original runner while exposing the same tasks as Harbor task schema 1.4:

- `dataset/csbench/`: ready-to-run Harbor tasks;
- `src/csbench_harbor/`: adapter for the original CSBench CodeAct loop;
- `tasks/`: original source and task metadata;
- `main.py` / `run.py`: original experiment entry points;
- `scripts/run_harbor.sh`: public Harbor entry point.

Harbor uses the existing CSBench images directly. Do not add a Harbor image
layer or rebuild images merely for compatibility. The verifier restores the
protected tests and runs the original task `test.sh`.

## Common commands

```bash
scripts/bootstrap.sh
.venv/bin/pytest -q

# One task, two attempts, four concurrent trials
CSBENCH_TASK=cs000280 \
CSBENCH_JOB_NAME=dev \
scripts/run_harbor.sh -k 2 -n 4

# Isolated harness/container/verifier check with no model call
make smoke TASK=cs000280

# Official interactive result viewer
.venv/bin/harbor view jobs --jobs

# Read-only tabular and aggregate export
python3 scripts/summarize_harbor_results.py jobs/<job-name>
```

Extra options passed to `scripts/run_harbor.sh` are official Harbor CLI
options. `-k` means attempts per task; `-n` means concurrent trials.
The smoke command uses public Docker Hub images by default; a release owner may
set `SMOKE_IMAGE_TEMPLATE` to an accessible unchanged-image template before
the public tags are available.

## Result interpretation

Harbor writes one job-level `result.json` plus a subdirectory per trial. Each
trial has its own `result.json`, `trial.log`, and `verifier/` artifacts. In
CSBench, reward 1 means the canonical tests passed and reward 0 means they did
not; inspect `exception_info` separately. Use Harbor's official viewer for
trajectories and the repository summarizer for `trials.csv` and `summary.json`.

`harbor analyze` is an optional additional model call and is not required for
scoring. Do not run it by default. Do not run `harbor upload`, publish Docker
images, commit, or push unless explicitly authorized.

## Non-negotiable safeguards

- Keep nop smoke outputs in `.smoke/`; they are non-paper/non-reportable.
- Do not change task labels, expected results, protected tests, or paper data.
- Do not expose secrets or copy `.env` values into tracked files.
- Preserve unrelated edits and keep Chinese/English public docs aligned.

See `docs/HARBOR.md` for the complete task and output formats and `README.md`
or `README.en.md` for user-facing instructions.
