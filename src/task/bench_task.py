# Copyright (c) 2025 ByteDance Ltd. and/or its affiliates
# SPDX-License-Identifier: Apache-2.0
import subprocess
from dataclasses import dataclass
from pathlib import Path

from src.runtime.base_runtime import BaseRuntime
from src.config import (
    get_default_image_ref,
    get_task_dir,
    get_task_log_dir,
)


def _read_image_base_commit(image_ref: str) -> str:
    """Read the base commit embedded in a task image.

    We use `git rev-parse HEAD` inside `/testbed` as the single source of truth.
    """
    result = subprocess.run(
        [
            "docker",
            "run",
            "--platform",
            "linux/amd64",
            "--rm",
            image_ref,
            "bash",
            "-lc",
            "cd /testbed && git rev-parse HEAD",
        ],
        stdin=subprocess.DEVNULL,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    )
    base_commit = result.stdout.strip()
    if result.returncode == 0 and base_commit:
        return base_commit
    error = result.stderr.strip() or f"returncode={result.returncode}"
    raise RuntimeError(f"Failed to read base commit from image {image_ref}: {error}")

@dataclass
class BenchTask:
    task_name: str  # folder name
    task_instruction: str  # metadata/task.md
    @classmethod
    def from_name(cls, task_name: str) -> 'BenchTask':
        folder_path = get_task_dir(task_name)
        return cls.from_folder(folder_path)
    @classmethod
    def from_folder(cls, folder_path: Path) -> 'BenchTask':
        task_name = folder_path.name
        
        task_instruction_path = folder_path / 'metadata' / 'task.md'
        
        assert task_instruction_path.exists(), f"Task instruction file not found: {task_instruction_path}"
        
        task_instruction = task_instruction_path.read_text()
        
        return BenchTask(task_name, task_instruction)

    def to_image_name(self) -> str:
        return get_default_image_ref(self.task_name)

    def to_base_commit(self) -> str:
        """Resolve the task's base commit by probing the task image."""
        image_ref = self.to_image_name()
        return _read_image_base_commit(image_ref)

    def to_runtime(self, runtime_cls) -> BaseRuntime:
        return runtime_cls(image_name=self.to_image_name())
    

    def to_log_dir(self, attempt_id: int | None = None) -> Path:
        return get_task_log_dir(self.task_name, attempt_id)
