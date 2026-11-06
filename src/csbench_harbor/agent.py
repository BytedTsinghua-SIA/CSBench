"""Run CSBench's original CodeAct workflow as a Harbor external agent.

Harbor owns the container lifecycle. ``HarborRuntimeBridge`` only translates
the synchronous runtime API used by CSBench to Harbor's asynchronous
``BaseEnvironment`` API, so the original prompt, tools, model calls, and turn
loop remain unchanged.
"""

from __future__ import annotations

import asyncio
import json
import os
import shlex
import subprocess
import sys
import tempfile
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Coroutine, TypeVar

from harbor.agents.base import BaseAgent
from harbor.environments.base import BaseEnvironment
from harbor.models.agent.context import AgentContext


_T = TypeVar("_T")


def _sanitize_no_proxy() -> None:
    """Drop unbracketed IPv6 tokens that httpx 0.28 cannot parse."""

    for name in ("NO_PROXY", "no_proxy"):
        value = os.environ.get(name)
        if not value:
            continue
        tokens = [token.strip() for token in value.split(",") if token.strip()]
        compatible = [
            token
            for token in tokens
            if token.count(":") < 2 or token.startswith("[")
        ]
        if compatible != tokens:
            os.environ[name] = ",".join(compatible)


def _load_csbench() -> Path:
    bundled_root = Path(__file__).resolve().parents[2]
    root = Path(os.environ.get("CSBENCH_ROOT", bundled_root))
    root = root.expanduser().resolve()
    expected = root / "src" / "agents" / "workflows" / "code_act_workflow.py"
    if not expected.is_file():
        raise FileNotFoundError(
            "CSBENCH_ROOT does not point to a CSBench checkout containing "
            f"{expected.relative_to(root)}: {root}"
        )
    root_text = str(root)
    if root_text not in sys.path:
        sys.path.insert(0, root_text)
    return root


_CSBENCH_ROOT = _load_csbench()

from src.agents.utils.llm import LLMConfig  # noqa: E402
from src.agents.workflows.base_workflow import WorkflowConfig  # noqa: E402
from src.agents.workflows.code_act_workflow import CodeActWorkflow  # noqa: E402
from src.runtime.base_runtime import BaseRuntime  # noqa: E402


class _SecretSafeLLMConfig(LLMConfig):
    """LLMConfig whose debug representation never includes credentials."""

    def __repr__(self) -> str:
        return (
            "LLMConfig("
            f"provider={self.provider!r}, model={self.model!r}, "
            "api_key='<redacted>', "
            f"api_base={self.api_base!r}, api_version={self.api_version!r}, "
            f"azure_deployment={self.azure_deployment!r}, timeout={self.timeout!r}, "
            f"temperature={self.temperature!r}, max_tokens={self.max_tokens!r}, "
            f"top_p={self.top_p!r}, extra_headers={self.extra_headers!r})"
        )


@dataclass(frozen=True)
class _TaskProxy:
    task_name: str
    task_instruction: str


def _jsonable(value: Any) -> Any:
    if value is None or isinstance(value, (str, int, float, bool)):
        return value
    if isinstance(value, dict):
        return {str(key): _jsonable(item) for key, item in value.items()}
    if isinstance(value, (list, tuple)):
        return [_jsonable(item) for item in value]
    function = getattr(value, "function", None)
    if function is not None:
        return {
            "id": getattr(value, "id", None),
            "type": "function",
            "function": {
                "name": getattr(function, "name", None),
                "arguments": getattr(function, "arguments", None),
            },
        }
    return repr(value)


class HarborRuntimeBridge(BaseRuntime):
    """Synchronous CSBench runtime facade backed by a Harbor environment."""

    def __init__(
        self,
        environment: BaseEnvironment,
        harbor_loop: asyncio.AbstractEventLoop,
        workdir: str = "/testbed",
    ) -> None:
        super().__init__(image_name="harbor-managed")
        self._environment = environment
        self._harbor_loop = harbor_loop
        self._workdir = workdir

    def _submit(self, coroutine: Coroutine[Any, Any, _T], timeout: float | None = None) -> _T:
        future = asyncio.run_coroutine_threadsafe(coroutine, self._harbor_loop)
        return future.result(timeout=timeout)

    def start(self) -> None:
        """Harbor starts the environment before invoking the agent."""

    def stop(self) -> None:
        """Harbor stops the environment after verification."""

    def execute(
        self,
        input: str,
        timeout: int | float = 30,
        use_tty: bool = False,
        interactive: bool = False,
    ) -> tuple[str, int]:
        del use_tty, interactive
        timeout_sec = max(1, min(int(timeout), 3600))
        try:
            result = self._submit(
                self._environment.exec(
                    command=input,
                    cwd=self._workdir,
                    timeout_sec=timeout_sec,
                ),
                timeout=timeout_sec + 30,
            )
        except TimeoutError:
            return f"Command timed out after {timeout_sec} seconds", -1
        output = "\n".join(part for part in (result.stdout, result.stderr) if part)
        return output, result.return_code

    def transfer_file(
        self,
        src: str | Path,
        dst: str | Path,
        to_container: bool = True,
    ) -> None:
        if to_container:
            destination = str(dst)
            parent = str(Path(destination).parent)
            _, return_code = self.execute(f"mkdir -p {shlex.quote(parent)}")
            if return_code != 0:
                raise RuntimeError(f"Could not create container directory: {parent}")
            self._submit(self._environment.upload_file(str(src), destination), timeout=360)
        else:
            self._submit(self._environment.download_file(str(src), str(dst)), timeout=360)

    def read_file(self, path: str | Path) -> str:
        with tempfile.TemporaryDirectory(prefix="csbench-harbor-read-") as temp_dir:
            local_path = Path(temp_dir) / "content"
            self.transfer_file(path, local_path, to_container=False)
            with local_path.open("r", encoding="utf-8", newline="") as handle:
                return handle.read()

    def write_file(self, path: str | Path, content: str) -> None:
        with tempfile.TemporaryDirectory(prefix="csbench-harbor-write-") as temp_dir:
            local_path = Path(temp_dir) / "content"
            with local_path.open("w", encoding="utf-8", newline="") as handle:
                handle.write(content)
            self.transfer_file(local_path, path, to_container=True)


class CSBenchCodeActAgent(BaseAgent):
    """CSBench's original minimalist OpenHands-derived CodeAct agent."""

    SUPPORTS_ATIF = False

    @staticmethod
    def name() -> str:
        return "csbench-codeact"

    def version(self) -> str:
        return "0.1.0"

    async def setup(self, environment: BaseEnvironment) -> None:
        probe = await environment.exec(
            command=(
                "git config --global --add safe.directory /testbed && "
                "rm -f /testbed/.harbor-environment-placeholder && "
                "test -d /testbed && git -C /testbed rev-parse --is-inside-work-tree"
            ),
            timeout_sec=30,
            user="root",
        )
        if probe.return_code != 0:
            detail = probe.stderr or probe.stdout or "no diagnostic output"
            raise RuntimeError(f"CSBench image is not a Git checkout at /testbed: {detail}")

    def _resolved_model(self) -> tuple[str, str]:
        raw_model = os.getenv("OPENAI_MODEL") or os.getenv("API_MODEL") or self.model_name
        if not raw_model:
            raise RuntimeError("Pass --model to Harbor or set OPENAI_MODEL")
        provider = os.getenv("PROVIDER", "").strip()
        model = raw_model
        if "/" in raw_model:
            model_provider, model = raw_model.split("/", 1)
            provider = provider or model_provider
        return provider or "openai", model

    async def run(
        self,
        instruction: str,
        environment: BaseEnvironment,
        context: AgentContext,
    ) -> None:
        _sanitize_no_proxy()
        provider, model = self._resolved_model()
        api_key = os.getenv("OPENAI_API_KEY") or os.getenv("API_KEY")
        if not api_key:
            raise RuntimeError("OPENAI_API_KEY or API_KEY is required by the CSBench CodeAct agent")

        temperature = float(os.getenv("CSBENCH_TEMPERATURE", "1.0"))
        max_tokens = int(os.getenv("MODEL_MAX_TOKENS", "32768"))
        max_turns = int(os.getenv("MAX_TURNS", "50"))
        llm_config = _SecretSafeLLMConfig(
            provider=provider,
            model=model,
            api_key=api_key,
            api_base=os.getenv("OPENAI_API_BASE") or os.getenv("API_BASE"),
            temperature=temperature,
            timeout=float(os.getenv("CSBENCH_LLM_TIMEOUT", "180")),
            max_tokens=max_tokens,
        )
        workflow = CodeActWorkflow(WorkflowConfig(llm_config=llm_config, max_turns=max_turns))
        task_name = environment.environment_name.rsplit("/", 1)[-1]
        task = _TaskProxy(task_name=task_name, task_instruction=instruction)
        runtime = HarborRuntimeBridge(environment, asyncio.get_running_loop())

        def run_original_workflow() -> None:
            asyncio.run(workflow.run(runtime, task))  # type: ignore[arg-type]

        await asyncio.to_thread(run_original_workflow)

        self.logs_dir.mkdir(parents=True, exist_ok=True)
        conversations = _jsonable(getattr(workflow, "conversations", []))
        (self.logs_dir / "conversation_history.json").write_text(
            json.dumps(conversations, indent=2, ensure_ascii=False) + "\n",
            encoding="utf-8",
        )
        (self.logs_dir / "resolved_config.json").write_text(
            json.dumps(
                {
                    "source_agent": "CSBench CodeActWorkflow",
                    "csbench_commit": _git_revision(_CSBENCH_ROOT),
                    "provider": provider,
                    "model": model,
                    "temperature": temperature,
                    "max_tokens": max_tokens,
                    "max_turns": max_turns,
                    "workdir": "/testbed",
                },
                indent=2,
            )
            + "\n",
            encoding="utf-8",
        )
        context.metadata = {
            **(context.metadata or {}),
            "source_agent": "csbench-original-codeact",
            "max_turns": max_turns,
            "conversation_messages": len(conversations),
        }


def _git_revision(root: Path) -> str | None:
    try:
        result = subprocess.run(
            ["git", "-C", str(root), "rev-parse", "HEAD"],
            check=True,
            capture_output=True,
            text=True,
        )
    except (OSError, subprocess.CalledProcessError):
        return None
    return result.stdout.strip() or None
