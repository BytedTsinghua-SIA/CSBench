# SPDX-License-Identifier: Apache-2.0
"""
CSBench configuration module.

Reads path-related settings from environment variables or `.env`.
"""

import os
from pathlib import Path

def load_env():
    import dotenv
    env_file = os.getenv("ENV_FILE", None)
    # print(env_file, "loaded")
    dotenv.load_dotenv(env_file)

load_env()

OUTPUT_ROOT = Path(os.getenv("OUTPUT_ROOT", ".")).resolve()

LOGS_DIR = OUTPUT_ROOT / "logs"
REPORTS_DIR = OUTPUT_ROOT / "reports"
TASKS_DIR = Path(os.getenv("TASK_ROOT", "tasks")).resolve()
BUILD_ROOT = Path(os.getenv("BUILD_ROOT", "build")).resolve()
DOCKER_REGISTRY = os.getenv("DOCKER_REGISTRY", "docker.io")
DOCKER_NAMESPACE = os.getenv("DOCKER_NAMESPACE", "honglifish/csbench")
DOCKER_REPOSITORY = os.getenv("DOCKER_REPOSITORY", "").strip("/")
DOCKER_TAG = os.getenv("DOCKER_TAG", "latest")


def get_task_log_dir(task_name: str, attempt_id: int | None = None) -> Path:
    """Get log directory for a specific task and attempt.
    
    Args:
        attempt_id: Attempt number (e.g., 1, 2, 3...). If None, returns task log base dir.
    
    Returns:
        Path to the log directory: logs/{task_name}/attempt{attempt_id}
    """
    base_dir = LOGS_DIR / task_name
    if attempt_id is not None:
        return base_dir / f"attempt{attempt_id}"
    return base_dir
    
def get_report_path(task_name: str, attempt_id: int | None = None) -> Path:
    """Get the report file path for a specific task and attempt.
    
    Args:
        task_name: Name of the task (e.g., cs000013)
        attempt_id: Attempt number. If None, returns base report path.
    
    Returns:
        Path to the report file: reports/{task_name}_attempt{attempt_id}.json
    """
    if attempt_id is not None:
        return REPORTS_DIR / f"{task_name}_attempt{attempt_id}.json"
    return REPORTS_DIR / f"{task_name}.json"

def get_task_dir(task_name: str) -> Path:
    """Get the task directory.
    
    Args:
        task_name: Name of the task (e.g., cs000013)
    
    Returns:
        Path to the task directory: tasks/{task_name}
    """
    return TASKS_DIR / task_name

def get_task_build_dir(task_name: str) -> Path:
    """Get the staged Docker build context directory for a task.

    Args:
        task_name: Name of the task (e.g., cs000013)

    Returns:
        Path to the task build directory: BUILD_ROOT/{task_name}
    """
    return BUILD_ROOT / task_name

def get_default_image_name(task_name: str, tag: str | None = None) -> str:
    """Get the default Docker image name for a task.

    Args:
        task_name: Name of the task (e.g., cs000013)
        tag: Optional image tag. If omitted, returns the image repository only.

    Returns:
        With ``DOCKER_REPOSITORY`` set, the shared repository name is returned
        and tasks are selected by tag. Otherwise the historical per-task
        repository layout is used.
    """
    if DOCKER_REPOSITORY:
        image = f"{DOCKER_REGISTRY.rstrip('/')}/{DOCKER_REPOSITORY}"
    else:
        image = f"{DOCKER_REGISTRY.rstrip('/')}/{DOCKER_NAMESPACE}/{task_name}"
    if tag is None:
        return image
    return f"{image}:{tag}"

def get_default_image_ref(task_name: str, tag: str | None = None) -> str:
    """Get the default Docker image reference for a task.

    Args:
        task_name: Name of the task (e.g., cs000013)
        tag: Optional image tag. If omitted, uses DOCKER_TAG.

    Returns:
        Image reference using either ``registry/repository:task_name`` or the
        historical ``registry/namespace/task_name:tag`` layout.
    """
    effective_tag = tag or (task_name if DOCKER_REPOSITORY else DOCKER_TAG)
    return get_default_image_name(task_name, effective_tag)

def get_test_override_dir(task_name: str) -> Path:
    """Get the test_override directory for a task.
    
    Args:
        task_name: Name of the task
    
    Returns:
        Path to test_override: tasks/{task_name}/metadata/test_override
    """
    return TASKS_DIR / task_name / "metadata" / "test_override"
