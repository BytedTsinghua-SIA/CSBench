import csv
import json
import subprocess
import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parent.parent
SCRIPT = REPO_ROOT / "scripts" / "summarize_harbor_results.py"


def write_json(path: Path, value: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value), encoding="utf-8")


def test_summarizes_harbor_job(tmp_path: Path) -> None:
    job = tmp_path / "job-a"
    write_json(job / "result.json", {"n_total_trials": 2, "stats": {}})
    base = {
        "task_name": "csbench/cs000280",
        "agent_info": {"name": "mini-swe-agent", "model_info": {"name": "model-a"}},
        "agent_result": {
            "n_input_tokens": 10,
            "n_cache_tokens": 2,
            "n_output_tokens": 3,
            "cost_usd": 0.1,
        },
        "started_at": "2026-01-01T00:00:00Z",
        "finished_at": "2026-01-01T00:01:00Z",
    }
    write_json(
        job / "trial-1" / "result.json",
        {
            **base,
            "trial_name": "trial-1",
            "verifier_result": {"rewards": {"reward": 1.0}},
            "exception_info": None,
        },
    )
    write_json(
        job / "trial-2" / "result.json",
        {
            **base,
            "trial_name": "trial-2",
            "verifier_result": {"rewards": {"reward": 0.0}},
            "exception_info": {"exception_type": "AgentError", "message": "failed"},
        },
    )
    output = tmp_path / "export"

    subprocess.run(
        [sys.executable, str(SCRIPT), str(job), "--output-dir", str(output)],
        check=True,
        capture_output=True,
        text=True,
    )

    summary = json.loads((output / "summary.json").read_text(encoding="utf-8"))
    assert summary["overall"]["n_trials"] == 2
    assert summary["overall"]["n_passed"] == 1
    assert summary["overall"]["pass_rate"] == 0.5
    assert summary["overall"]["mean_reward"] == 0.5
    assert summary["overall"]["n_exceptions"] == 1
    assert summary["overall"]["cost_usd"] == 0.2

    with (output / "trials.csv").open(encoding="utf-8", newline="") as handle:
        rows = list(csv.DictReader(handle))
    assert [row["trial_name"] for row in rows] == ["trial-1", "trial-2"]
    assert rows[0]["passed"] == "True"
    assert rows[1]["exception_type"] == "AgentError"
