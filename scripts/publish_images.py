#!/usr/bin/env python3
"""Batch retag and publish unchanged CSBench images to Docker Hub.

The script never builds an image. It is dry-run by default. Publishing requires
both ``--execute`` and an exact ``--confirm-target`` value.
"""

from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path


TASK_ID_RE = re.compile(r"^cs\d{6}$")
AUTHORIZED_TARGET_REPOSITORY = "docker.io/honglifish/csbench"


def run(command: list[str], *, capture: bool = False) -> subprocess.CompletedProcess[str]:
    return subprocess.run(command, check=True, text=True, capture_output=capture)


def discover_tasks(root: Path) -> list[str]:
    task_root = root.expanduser().resolve() / "tasks"
    tasks = sorted(path.name for path in task_root.iterdir() if path.is_dir() and TASK_ID_RE.fullmatch(path.name))
    if not tasks:
        raise ValueError(f"No csNNNNNN task directories found under {task_root}")
    return tasks


def image_id(image: str) -> str:
    result = run(["docker", "image", "inspect", "--format", "{{.Id}}", image], capture=True)
    value = result.stdout.strip()
    if not value.startswith("sha256:"):
        raise RuntimeError(f"Unexpected image ID for {image}: {value!r}")
    return value


def append_state(path: Path, record: dict[str, str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(record, sort_keys=True) + "\n")


def parse_args() -> argparse.Namespace:
    repo_root = Path(__file__).resolve().parent.parent
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--csbench-root", type=Path, default=repo_root)
    parser.add_argument(
        "--source-repository",
        default=os.getenv("CSBENCH_SOURCE_REPOSITORY"),
        help="Existing local image repository, or set CSBENCH_SOURCE_REPOSITORY",
    )
    parser.add_argument("--target-repository", default=AUTHORIZED_TARGET_REPOSITORY)
    parser.add_argument("--task", action="append", dest="tasks", help="Task ID; repeatable")
    parser.add_argument("--state-file", type=Path, default=Path("release-state.jsonl"))
    parser.add_argument("--execute", action="store_true", help="Actually tag and push")
    parser.add_argument(
        "--confirm-target",
        help=(
            "Required with --execute; must exactly equal "
            f"{AUTHORIZED_TARGET_REPOSITORY}"
        ),
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    if not args.source_repository:
        raise SystemExit(
            "Provide --source-repository or set CSBENCH_SOURCE_REPOSITORY"
        )
    tasks = args.tasks or discover_tasks(args.csbench_root)
    invalid = sorted({task for task in tasks if not TASK_ID_RE.fullmatch(task)})
    if invalid:
        raise ValueError(f"Invalid task IDs: {invalid}")
    tasks = sorted(set(tasks))

    if args.execute:
        if args.target_repository != AUTHORIZED_TARGET_REPOSITORY:
            raise SystemExit(
                "Refusing to publish outside the authorized repository: "
                f"{AUTHORIZED_TARGET_REPOSITORY!r}"
            )
        if args.confirm_target != AUTHORIZED_TARGET_REPOSITORY:
            raise SystemExit(
                "Refusing to publish: --confirm-target must exactly match "
                f"{AUTHORIZED_TARGET_REPOSITORY!r}"
            )

    print(f"mode={'EXECUTE' if args.execute else 'DRY-RUN'} tasks={len(tasks)}")
    print(f"source={args.source_repository}")
    print(f"target={args.target_repository}")
    for task in tasks:
        source = f"{args.source_repository}/{task}:latest"
        target = f"{args.target_repository}:{task}"
        print(f"{source} -> {target}")
        if not args.execute:
            continue
        before = image_id(source)
        run(["docker", "image", "tag", source, target])
        after = image_id(target)
        if before != after:
            raise RuntimeError(f"Retag changed image identity for {task}: {before} != {after}")
        run(["docker", "image", "push", target])
        append_state(
            args.state_file,
            {
                "task_id": task,
                "source": source,
                "target": target,
                "image_id": before,
                "published_at": datetime.now(timezone.utc).isoformat(),
            },
        )
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except subprocess.CalledProcessError as error:
        print(f"Docker command failed with exit code {error.returncode}", file=sys.stderr)
        raise SystemExit(error.returncode) from error
