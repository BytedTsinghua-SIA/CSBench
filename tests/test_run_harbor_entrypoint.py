import json
import os
import subprocess
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parent.parent


def test_wrapper_forwards_attempts_concurrency_and_bare_task_id(tmp_path: Path) -> None:
    environment = os.environ.copy()
    environment.update(
        {
            "CSBENCH_ENV_LOADED": "1",
            "API_MODEL": "dummy",
            "CSBENCH_TASK": "cs000280",
            "CSBENCH_JOB_NAME": "nonreportable-config-test",
            "CSBENCH_JOBS_DIR": str(tmp_path / "jobs"),
        }
    )
    completed = subprocess.run(
        [
            str(REPO_ROOT / "scripts" / "run_harbor.sh"),
            "-k",
            "2",
            "-n",
            "8",
            "--print-config",
        ],
        cwd=REPO_ROOT,
        env=environment,
        check=True,
        capture_output=True,
        text=True,
    )

    config = json.loads(completed.stdout)
    assert config["n_attempts"] == 2
    assert config["n_concurrent_trials"] == 8
    assert config["datasets"][0]["task_names"] == ["cs000280"]


def test_wrapper_passes_proxy_to_native_harbor_agent_by_reference(tmp_path: Path) -> None:
    environment = os.environ.copy()
    for name in (
        "HTTP_PROXY",
        "HTTPS_PROXY",
        "ALL_PROXY",
        "http_proxy",
        "https_proxy",
        "all_proxy",
    ):
        environment.pop(name, None)
    environment.update(
        {
            "CSBENCH_ENV_LOADED": "1",
            "API_MODEL": "dummy",
            "CSBENCH_AGENT": "codex",
            "CSBENCH_JOB_NAME": "nonreportable-proxy-config-test",
            "CSBENCH_JOBS_DIR": str(tmp_path / "jobs"),
            "HTTPS_PROXY": "http://proxy.example:8118",
        }
    )
    completed = subprocess.run(
        [str(REPO_ROOT / "scripts" / "run_harbor.sh"), "--print-config"],
        cwd=REPO_ROOT,
        env=environment,
        check=True,
        capture_output=True,
        text=True,
    )

    config = json.loads(completed.stdout)
    assert config["agents"][0]["name"] == "codex"
    assert config["agents"][0]["env"] == {"HTTPS_PROXY": "${HTTPS_PROXY}"}
