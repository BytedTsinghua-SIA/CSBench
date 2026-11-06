#!/usr/bin/env python3
"""Export Harbor job results into a flat CSV and aggregate JSON summary.

Harbor itself owns the job/trial result format. This helper only reads
``result.json`` files; it never edits a Harbor job or uploads anything.
"""

from __future__ import annotations

import argparse
import csv
import json
import math
from collections import defaultdict
from pathlib import Path
from typing import Any


TRIAL_FIELDS = (
    "job_name",
    "trial_name",
    "task_name",
    "task_id",
    "agent",
    "model",
    "reward",
    "passed",
    "exception_type",
    "exception_message",
    "n_input_tokens",
    "n_cache_tokens",
    "n_output_tokens",
    "cost_usd",
    "started_at",
    "finished_at",
    "trial_dir",
)


def read_json(path: Path) -> dict[str, Any]:
    with path.open(encoding="utf-8") as handle:
        value = json.load(handle)
    if not isinstance(value, dict):
        raise ValueError(f"Expected a JSON object: {path}")
    return value


def is_job_result(value: dict[str, Any]) -> bool:
    return "n_total_trials" in value and "stats" in value


def is_trial_result(value: dict[str, Any]) -> bool:
    return "trial_name" in value and "task_name" in value and "verifier_result" in value


def discover_jobs(path: Path) -> list[Path]:
    path = path.expanduser().resolve()
    if not path.is_dir():
        raise ValueError(f"Not a directory: {path}")
    own_result = path / "result.json"
    if own_result.is_file() and is_job_result(read_json(own_result)):
        return [path]
    jobs: list[Path] = []
    for candidate in sorted(path.iterdir()):
        result = candidate / "result.json"
        if candidate.is_dir() and result.is_file() and is_job_result(read_json(result)):
            jobs.append(candidate)
    if not jobs:
        raise ValueError(f"No Harbor job directories found under: {path}")
    return jobs


def scalar_model_name(model_info: Any) -> str:
    if model_info is None:
        return ""
    if isinstance(model_info, str):
        return model_info
    if isinstance(model_info, dict):
        for key in ("name", "model", "model_name", "id"):
            value = model_info.get(key)
            if value:
                return str(value)
        return json.dumps(model_info, ensure_ascii=False, sort_keys=True)
    return str(model_info)


def exception_fields(exception_info: Any) -> tuple[str, str]:
    if not exception_info:
        return "", ""
    if isinstance(exception_info, dict):
        kind = exception_info.get("exception_type") or exception_info.get("type") or "Exception"
        message = exception_info.get("exception_message") or exception_info.get("message") or ""
        return str(kind), str(message)
    return type(exception_info).__name__, str(exception_info)


def trial_row(job: Path, trial: Path, value: dict[str, Any], root: Path) -> dict[str, Any]:
    verifier_result = value.get("verifier_result") or {}
    rewards = verifier_result.get("rewards") or {}
    reward = rewards.get("reward")
    exception_type, exception_message = exception_fields(value.get("exception_info"))
    agent_info = value.get("agent_info") or {}
    agent_result = value.get("agent_result") or {}
    task_name = str(value.get("task_name") or "")
    return {
        "job_name": job.name,
        "trial_name": value.get("trial_name") or trial.name,
        "task_name": task_name,
        "task_id": task_name.rsplit("/", 1)[-1],
        "agent": agent_info.get("name") or "",
        "model": scalar_model_name(agent_info.get("model_info")),
        "reward": reward if reward is not None else "",
        "passed": bool(reward == 1.0 and not exception_type),
        "exception_type": exception_type,
        "exception_message": exception_message,
        "n_input_tokens": agent_result.get("n_input_tokens"),
        "n_cache_tokens": agent_result.get("n_cache_tokens"),
        "n_output_tokens": agent_result.get("n_output_tokens"),
        "cost_usd": agent_result.get("cost_usd"),
        "started_at": value.get("started_at") or "",
        "finished_at": value.get("finished_at") or "",
        "trial_dir": trial.relative_to(root).as_posix(),
    }


def collect_rows(root: Path) -> tuple[list[Path], list[dict[str, Any]]]:
    jobs = discover_jobs(root)
    rows: list[dict[str, Any]] = []
    for job in jobs:
        for candidate in sorted(job.iterdir()):
            result = candidate / "result.json"
            if not candidate.is_dir() or not result.is_file():
                continue
            value = read_json(result)
            if is_trial_result(value):
                rows.append(trial_row(job, candidate, value, root.resolve()))
    if not rows:
        raise ValueError(f"No Harbor trial result.json files found under: {root}")
    return jobs, rows


def number(value: Any) -> float | None:
    if value in (None, ""):
        return None
    try:
        result = float(value)
    except (TypeError, ValueError):
        return None
    return result if math.isfinite(result) else None


def aggregate(rows: list[dict[str, Any]], jobs: list[Path]) -> dict[str, Any]:
    groups: dict[tuple[str, str], list[dict[str, Any]]] = defaultdict(list)
    for row in rows:
        groups[(str(row["agent"]), str(row["model"]))].append(row)

    def summarize(group: list[dict[str, Any]]) -> dict[str, Any]:
        rewards = []
        costs = []
        for row in group:
            reward = number(row["reward"])
            if reward is not None:
                rewards.append(reward)
            cost = number(row["cost_usd"])
            if cost is not None:
                costs.append(cost)
        passed = sum(bool(row["passed"]) for row in group)
        exceptions = sum(bool(row["exception_type"]) for row in group)
        return {
            "n_trials": len(group),
            "n_scored": len(rewards),
            "n_passed": passed,
            "pass_rate": passed / len(group) if group else None,
            "mean_reward": sum(rewards) / len(rewards) if rewards else None,
            "n_exceptions": exceptions,
            "input_tokens": sum(int(row["n_input_tokens"] or 0) for row in group),
            "cache_tokens": sum(int(row["n_cache_tokens"] or 0) for row in group),
            "output_tokens": sum(int(row["n_output_tokens"] or 0) for row in group),
            "cost_usd": sum(costs) if costs else None,
        }

    return {
        "schema_version": 1,
        "source_format": "Harbor 0.20 job/trial result.json",
        "jobs": [job.name for job in jobs],
        "overall": summarize(rows),
        "by_agent_model": {
            f"{agent}::{model or '(no model)'}": summarize(group)
            for (agent, model), group in sorted(groups.items())
        },
    }


def write_outputs(output_dir: Path, rows: list[dict[str, Any]], summary: dict[str, Any]) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)
    with (output_dir / "trials.csv").open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=TRIAL_FIELDS)
        writer.writeheader()
        writer.writerows(rows)
    with (output_dir / "summary.json").open("w", encoding="utf-8") as handle:
        json.dump(summary, handle, ensure_ascii=False, indent=2, sort_keys=True)
        handle.write("\n")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("path", type=Path, help="A Harbor job directory or jobs root")
    parser.add_argument(
        "--output-dir",
        type=Path,
        help="Output directory (default: <path>/analysis for one job, otherwise <path>/_analysis)",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    root = args.path.expanduser().resolve()
    jobs, rows = collect_rows(root)
    output_dir = args.output_dir
    if output_dir is None:
        output_dir = root / ("analysis" if len(jobs) == 1 and jobs[0] == root else "_analysis")
    output_dir = output_dir.expanduser().resolve()
    summary = aggregate(rows, jobs)
    write_outputs(output_dir, rows, summary)
    print(json.dumps(summary, ensure_ascii=False, indent=2, sort_keys=True))
    print(f"wrote: {output_dir / 'trials.csv'}")
    print(f"wrote: {output_dir / 'summary.json'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
