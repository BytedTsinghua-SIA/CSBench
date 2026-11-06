from __future__ import annotations

import asyncio
import importlib
import os
from pathlib import Path
from types import SimpleNamespace


REPO_ROOT = Path(__file__).resolve().parents[1]


class FakeEnvironment:
    async def exec(self, command: str, **_: object) -> SimpleNamespace:
        return SimpleNamespace(stdout=f"ran:{command}", stderr=None, return_code=0)


def test_runtime_bridge_returns_text() -> None:
    os.environ.setdefault("CSBENCH_ROOT", str(REPO_ROOT))
    module = importlib.import_module("csbench_harbor.agent")

    async def exercise() -> None:
        loop = asyncio.get_running_loop()
        bridge = module.HarborRuntimeBridge(FakeEnvironment(), loop)
        output, code = await asyncio.to_thread(bridge.execute, "pwd")
        assert output == "ran:pwd"
        assert code == 0

    asyncio.run(exercise())


def test_llm_config_repr_redacts_api_key() -> None:
    os.environ.setdefault("CSBENCH_ROOT", str(REPO_ROOT))
    module = importlib.import_module("csbench_harbor.agent")
    config = module._SecretSafeLLMConfig(
        provider="openai",
        model="test-model",
        api_key="do-not-print-this",
    )
    rendered = repr(config)
    assert "do-not-print-this" not in rendered
    assert "<redacted>" in rendered


def test_sanitize_no_proxy_drops_unbracketed_ipv6(monkeypatch) -> None:
    os.environ.setdefault("CSBENCH_ROOT", str(REPO_ROOT))
    module = importlib.import_module("csbench_harbor.agent")
    monkeypatch.setenv("NO_PROXY", "localhost,127.0.0.1,::1,2001:db8::/32,.example.com")
    monkeypatch.setenv("no_proxy", "localhost,::1")
    module._sanitize_no_proxy()
    assert os.environ["NO_PROXY"] == "localhost,127.0.0.1,.example.com"
    assert os.environ["no_proxy"] == "localhost"
