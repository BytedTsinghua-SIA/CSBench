from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]


def resolve_image(extra_env: dict[str, str]) -> tuple[str, str]:
    env = os.environ.copy()
    env.update(extra_env)
    env["ENV_FILE"] = os.devnull
    result = subprocess.run(
        [
            sys.executable,
            "-c",
            (
                "from src.config import get_default_image_name, get_default_image_ref; "
                "print(get_default_image_name('cs000003')); "
                "print(get_default_image_ref('cs000003'))"
            ),
        ],
        cwd=REPO_ROOT,
        env=env,
        check=True,
        capture_output=True,
        text=True,
    )
    name, ref = result.stdout.splitlines()
    return name, ref


def test_shared_repository_uses_task_id_as_tag() -> None:
    name, ref = resolve_image(
        {
            "DOCKER_REGISTRY": "docker.io",
            "DOCKER_REPOSITORY": "honglifish/csbench",
        }
    )
    assert name == "docker.io/honglifish/csbench"
    assert ref == "docker.io/honglifish/csbench:cs000003"


def test_historical_per_task_repository_remains_supported() -> None:
    name, ref = resolve_image(
        {
            "DOCKER_REGISTRY": "registry.example.com",
            "DOCKER_REPOSITORY": "",
            "DOCKER_NAMESPACE": "csbench",
            "DOCKER_TAG": "latest",
        }
    )
    assert name == "registry.example.com/csbench/cs000003"
    assert ref == "registry.example.com/csbench/cs000003:latest"
