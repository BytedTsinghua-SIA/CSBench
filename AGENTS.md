# Instructions for AI Coding Agents

This is the Harbor-compatible release branch of CSBench. Preserve both public
interfaces: standard Harbor task schema 1.4 under `dataset/csbench/` and the
original CSBench runner under `main.py` / `run.py`.

## Read first

1. Read `README.md` (or `README.en.md`) for the public workflow.
2. Read `docs/HARBOR.md` for image, task, verifier, and result semantics.
3. Inspect the relevant implementation and tests before editing.

## Repository map

- `dataset/csbench/`: checked-in Harbor dataset generated from the release.
- `tasks/`: original CSBench task sources and metadata.
- `src/csbench_harbor/`: external-agent adapter and runtime bridge.
- `src/agents/`, `src/runtime/`: original CodeAct workflow and container runtime.
- `scripts/run_harbor.sh`: `.env`-aware Harbor entry point; extra CLI arguments
  are forwarded to Harbor.
- `scripts/generate_dataset.py`: deterministic offline dataset generator.
- `scripts/smoke_test.sh`: isolated non-reportable Harbor validation.
- `scripts/summarize_harbor_results.py`: read-only job/trial CSV and JSON export.
- `scripts/publish_images.py`: guarded image-retag/publication helper; dry-run by
  default.
- `jobs/`: reportable Harbor outputs by convention.
- `.smoke/`: ignored, non-reportable validation outputs only.

## Setup and routine validation

```bash
scripts/bootstrap.sh
.venv/bin/pytest -q
python3 -m py_compile scripts/*.py
bash -n scripts/*.sh
git diff --check
```

Regenerate the public dataset only when its source or generator changes:

```bash
.venv/bin/python scripts/generate_dataset.py --overwrite
git diff --exit-code -- dataset/csbench
```

For an end-to-end container/verifier check that makes no model call:

```bash
make smoke TASK=cs000280
```

This writes only to `.smoke/`. A nop reward of 0 is expected; zero exceptions
is the signal that task loading, the existing image, and the verifier worked.
The default image is the public Docker Hub tag. Before publication, set
`SMOKE_IMAGE_TEMPLATE` explicitly to an accessible unchanged-image template.

## Running and reading Harbor results

```bash
CSBENCH_TASK=cs000280 CSBENCH_JOB_NAME=dev scripts/run_harbor.sh -k 2 -n 4
.venv/bin/harbor view jobs --jobs
python3 scripts/summarize_harbor_results.py jobs/dev
```

`-k` (attempts per task) and `-n` (concurrent trials) are official Harbor
options. The official files are `jobs/<job>/result.json` and each trial's
`result.json`; raw verifier artifacts live under `<trial>/verifier/`. The local
summarizer writes `analysis/trials.csv` and `analysis/summary.json` but never
modifies or uploads a job.

`harbor analyze` is optional model-based trajectory analysis, not basic score
aggregation. Do not invoke it by default. `harbor upload` is an external write;
do not invoke it without explicit authorization.

## Safety and preservation rules

- Do not commit, push Git branches, publish images, or execute Docker pushes
  unless the user explicitly asks for that action.
- Never run `scripts/publish_images.py --execute` implicitly. Its normal mode
  is a dry run.
- Do not rebuild or alter task images for Harbor compatibility. Harbor uses the
  original prebuilt images through `[environment].docker_image`.
- Do not change task labels, expected results, protected tests, or paper result
  data as part of infrastructure work.
- Keep smoke outputs under `.smoke/` and never include them in reportable
  benchmark aggregation.
- Do not call paid model APIs, including optional trajectory analysis, merely
  to validate local code. Use the nop smoke unless a real agent run is asked for.
- Never place API keys, registry credentials, or `.env` contents in tracked
  files or logs.
- Preserve unrelated user changes in a dirty worktree.

## Editing expectations

- Keep English and Chinese public documentation consistent.
- If the generator changes, verify that checked-in generated tasks are either
  unchanged or intentionally updated.
- If result parsing changes, test both successful trials and exceptions.
- Clearly distinguish official Harbor behavior from repository helper scripts.
- Prefer small, reviewable patches and run the focused tests plus
  `git diff --check` before handing off.
