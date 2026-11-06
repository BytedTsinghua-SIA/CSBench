#!/usr/bin/env python3
"""Generate Harbor task directories from a CSBench checkout.

This command performs no Docker or network operations. Generated tasks refer
to the public, unchanged CSBench images by tag.
"""

from __future__ import annotations

import argparse
import ast
import csv
import hashlib
import json
import re
import shutil
import stat
import tempfile
import tomllib
from pathlib import Path


TASK_ID_RE = re.compile(r"^cs\d{6}$")
COMMIT_RE = re.compile(r"^[0-9a-f]{40}$")
MODEL_COLUMNS = (
    "temp_gpt5_2",
    "temp_claude_sonnet_45",
    "temp_gemini_3_pro",
    "temp_glm_47",
    "temp_kimi_k2",
    "temp_minimax_m2",
    "temp_ds_32",
    "temp_seed_18",
    "temp_qwencoder",
)


def toml_string(value: str) -> str:
    return json.dumps(value, ensure_ascii=False)


def toml_array(values: list[str]) -> str:
    return "[" + ", ".join(toml_string(value) for value in values) + "]"


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def read_base_commit(task_dir: Path, task_id: str) -> str:
    entries: list[tuple[str, str]] = []
    path = task_dir / "entry_list.txt"
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or "," not in line:
            continue
        image, commit = (part.strip() for part in line.split(",", 1))
        if f"/{task_id}:" in image:
            entries.append((image, commit))
    if len(entries) != 1:
        raise ValueError(f"Expected one image entry for {task_id} in {path}, found {len(entries)}")
    commit = entries[0][1]
    if not COMMIT_RE.fullmatch(commit):
        raise ValueError(f"Invalid base commit for {task_id}: {commit}")
    return commit


def task_difficulty(row: dict[str, object]) -> str:
    if row.get("difficulty"):
        return str(row["difficulty"])
    success = sum(int(row[column]) for column in MODEL_COLUMNS) / (4 * len(MODEL_COLUMNS))
    if success < 0.15:
        return "hard"
    if success < 0.40:
        return "medium"
    return "easy"


def verifier_script(base_commit: str) -> str:
    return f"""#!/usr/bin/env bash
set -u

reward_file=/logs/verifier/reward.txt
mkdir -p /logs/verifier
finish() {{
  printf '%s\\n' "$1" > "$reward_file"
  exit 0
}}

cd /testbed || finish 0
git config --global --add safe.directory /testbed || finish 0
rm -f .harbor-environment-placeholder

# The original evaluator applies the agent patch to a fresh image while
# excluding test.sh and tests/. Restore that protected surface before grading.
git cat-file -e {base_commit}:test.sh >/dev/null 2>&1 || finish 0
rm -rf test.sh tests
git checkout {base_commit} -- test.sh >/dev/null 2>&1 || finish 0
if git cat-file -e {base_commit}:tests >/dev/null 2>&1; then
  git checkout {base_commit} -- tests >/dev/null 2>&1 || finish 0
fi

if [ -d /tests/test_override ]; then
  cp -a /tests/test_override/. /testbed/ || finish 0
fi

bash test.sh
status=$?
if [ "$status" -eq 0 ]; then
  finish 1
else
  finish 0
fi
"""


def task_toml(
    task_id: str,
    row: dict[str, object],
    languages: list[str],
    base_commit: str,
    image: str,
) -> str:
    return f"""schema_version = "1.4"

[task]
name = {toml_string(f"csbench/{task_id}")}
version = "1.0.0"
description = {toml_string(f"CSBench task {task_id}: {row['Topic']}")}
authors = []
keywords = ["csbench", "spec-to-code", "repository-level"]

[metadata]
task_id = {toml_string(task_id)}
domain = {toml_string(str(row['Type']))}
topic = {toml_string(str(row['Topic']))}
languages = {toml_array(languages)}
difficulty = {toml_string(task_difficulty(row))}
base_commit = {toml_string(base_commit)}
image_compatibility = "original-csbench-image"

[verifier]
timeout_sec = 2400.0
user = "root"

[agent]
timeout_sec = 7200.0
user = "root"

[environment]
docker_image = {toml_string(image)}
os = "linux"
workdir = "/testbed"
network_mode = "public"
gpus = 0
mcp_servers = []

[verifier.env]

[solution.env]
"""


def copy_override(source: Path, destination: Path) -> None:
    if not source.is_dir():
        return
    for path in source.rglob("*"):
        relative = path.relative_to(source)
        if path.name in {".DS_Store", ".files"}:
            continue
        target = destination / relative
        if path.is_dir():
            target.mkdir(parents=True, exist_ok=True)
        elif path.is_file():
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(path, target)


def parse_args() -> argparse.Namespace:
    here = Path(__file__).resolve().parent.parent
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--csbench-root", type=Path, default=here)
    parser.add_argument(
        "--catalog-dir",
        type=Path,
        default=here / "dataset" / "csbench",
        help="Checked-in Harbor dataset used as metadata when exp/out.csv is absent",
    )
    parser.add_argument("--output-dir", type=Path, default=here / "dataset" / "csbench")
    parser.add_argument("--docker-repository", default="docker.io/honglifish/csbench")
    parser.add_argument(
        "--image-template",
        help=(
            "Optional complete image template containing {task_id}; for example "
            "registry.example/csbench:{task_id} for local smoke tests"
        ),
    )
    parser.add_argument("--task", action="append", dest="tasks", help="Task ID; repeatable")
    parser.add_argument("--overwrite", action="store_true")
    return parser.parse_args()


def load_rows(root: Path, catalog_dir: Path) -> tuple[list[dict[str, object]], Path]:
    """Load private experiment taxonomy when present, else the public catalog."""

    taxonomy = root / "exp" / "out.csv"
    if taxonomy.is_file():
        with taxonomy.open(encoding="utf-8-sig", newline="") as handle:
            return list(csv.DictReader(handle)), taxonomy

    manifest = catalog_dir / "dataset_manifest.csv"
    if not manifest.is_file():
        raise FileNotFoundError(
            f"Neither {taxonomy} nor the public Harbor catalog {manifest} exists"
        )
    rows: list[dict[str, object]] = []
    for task_file in sorted(catalog_dir.glob("cs[0-9][0-9][0-9][0-9][0-9][0-9]/task.toml")):
        with task_file.open("rb") as handle:
            data = tomllib.load(handle)
        metadata = data["metadata"]
        rows.append(
            {
                "id": metadata["task_id"],
                "Type": metadata["domain"],
                "Topic": metadata["topic"],
                "Programming Languages": metadata["languages"],
                "difficulty": metadata["difficulty"],
                "base_commit": metadata["base_commit"],
            }
        )
    if not rows:
        raise ValueError(f"No task metadata found under {catalog_dir}")
    return rows, manifest


def main() -> None:
    args = parse_args()
    root = args.csbench_root.expanduser().resolve()
    task_root = root / "tasks"
    catalog_dir = args.catalog_dir.expanduser().resolve()
    rows, metadata_source = load_rows(root, catalog_dir)

    selected = set(args.tasks or [])
    invalid = sorted(task_id for task_id in selected if not TASK_ID_RE.fullmatch(task_id))
    if invalid:
        raise ValueError(f"Invalid task IDs: {invalid}")
    if selected:
        rows = [row for row in rows if row["id"] in selected]
        missing = selected - {row["id"] for row in rows}
        if missing:
            raise ValueError(f"Tasks absent from taxonomy: {sorted(missing)}")
    if not rows:
        raise ValueError("No tasks selected")

    output = args.output_dir.expanduser().resolve()
    output.mkdir(parents=True, exist_ok=True)
    manifest: list[dict[str, str]] = []
    for row in sorted(rows, key=lambda item: item["id"]):
        task_id = row["id"]
        if not TASK_ID_RE.fullmatch(task_id):
            raise ValueError(f"Unexpected task ID in taxonomy: {task_id}")
        source = task_root / task_id
        instruction_source = source / "metadata" / "task.md"
        if not instruction_source.is_file():
            raise FileNotFoundError(instruction_source)
        base_commit = str(row.get("base_commit") or read_base_commit(source, task_id))
        if not COMMIT_RE.fullmatch(base_commit):
            raise ValueError(f"Invalid base commit for {task_id}: {base_commit}")
        raw_languages = row["Programming Languages"]
        languages = (
            raw_languages
            if isinstance(raw_languages, list)
            else ast.literal_eval(str(raw_languages))
        )
        if not isinstance(languages, list) or not all(isinstance(item, str) for item in languages):
            raise ValueError(f"Invalid language list for {task_id}: {languages!r}")

        target = output / task_id
        override_source = source / "metadata" / "test_override"
        override_snapshot: tempfile.TemporaryDirectory[str] | None = None
        if not override_source.is_dir():
            override_source = catalog_dir / task_id / "tests" / "test_override"
            if override_source.is_dir() and target == catalog_dir / task_id:
                override_snapshot = tempfile.TemporaryDirectory(
                    prefix=f"csbench-{task_id}-override."
                )
                snapshot_path = Path(override_snapshot.name) / "test_override"
                shutil.copytree(override_source, snapshot_path)
                override_source = snapshot_path
        if target.exists():
            if not args.overwrite:
                raise FileExistsError(f"Refusing to overwrite {target}; pass --overwrite")
            shutil.rmtree(target)
        tests = target / "tests"
        tests.mkdir(parents=True)
        environment = target / "environment"
        environment.mkdir()
        (environment / ".harbor-environment-placeholder").touch()
        image = (
            args.image_template.format(task_id=task_id)
            if args.image_template
            else f"{args.docker_repository}:{task_id}"
        )
        (target / "instruction.md").write_text(
            instruction_source.read_text(encoding="utf-8"), encoding="utf-8"
        )
        (target / "task.toml").write_text(
            task_toml(task_id, row, languages, base_commit, image), encoding="utf-8"
        )
        test_script = tests / "test.sh"
        test_script.write_text(verifier_script(base_commit), encoding="utf-8")
        test_script.chmod(test_script.stat().st_mode | stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH)
        copy_override(override_source, tests / "test_override")
        if override_snapshot is not None:
            override_snapshot.cleanup()
        manifest.append(
            {
                "task_id": task_id,
                "domain": str(row["Type"]),
                "topic": str(row["Topic"]),
                "base_commit": base_commit,
                "image": image,
                "instruction_sha256": sha256(instruction_source),
            }
        )

    manifest_path = output / "dataset_manifest.csv"
    with manifest_path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(manifest[0]))
        writer.writeheader()
        writer.writerows(manifest)
    summary = {
        "format": "Harbor task schema 1.4",
        "task_count": len(manifest),
        "metadata_source": metadata_source.name,
        "metadata_sha256": sha256(metadata_source),
        "docker_repository": args.docker_repository,
        "image_template": args.image_template,
        "manifest_sha256": sha256(manifest_path),
    }
    (output / "conversion_summary.json").write_text(
        json.dumps(summary, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
    )
    print(json.dumps(summary, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
