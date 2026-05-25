from __future__ import annotations

import asyncio
import os
import sys
import json

from src.config import load_env
load_env()

from src.agents.utils.llm import LLMConfig
from src.agents.workflows.base_workflow import WorkflowConfig
from src.agents.workflows.code_act_workflow import CodeActWorkflow
from src.runtime.local_docker_container_runtime import LocalDockerContainerRuntime
from src.task.bench_task import BenchTask



async def main() -> None:
    if len(sys.argv) < 4:
        print("Usage: python -m scripts.run_agent <workflow_name> <task_name> <log_tag>")
        print("Example: python -m scripts.run_agent code_act_agent cs000013 attempt1")
        sys.exit(2)

    workflow_name = sys.argv[1]
    task_name = sys.argv[2]
    log_tag = sys.argv[3]

    task: BenchTask = BenchTask.from_name(task_name)
    runtime = LocalDockerContainerRuntime(image_name=task.to_image_name())
    runtime.start()
    try:
        llm_cfg = LLMConfig(
            provider=os.getenv("PROVIDER", "openai"),
            model=os.getenv("API_MODEL", "gpt-4o-mini"),
            api_key=os.getenv("API_KEY"),
            api_base=os.getenv("API_BASE"),
            api_version=os.getenv("OPENAI_API_VERSION"),
            temperature=1.0,
            timeout=float(os.getenv("API_TIMEOUT", "180.0")),
            max_tokens=int(os.getenv("MODEL_MAX_TOKENS", "32768")),
            api_mode=os.getenv("API_MODE", "chat"),
        )
        config = WorkflowConfig(llm_config=llm_cfg, max_turns=int(os.getenv("MAX_TURNS", "50")))
        if workflow_name.lower() in {"code_act_agent", "code_act", "code-act"}:
            workflow = CodeActWorkflow(config)
        else:
            print(f"Unknown workflow: {workflow_name}")
            sys.exit(2)
        try:
            await workflow.run(runtime, task)
        except ValueError as e:
            if "Missing required parameter" in str(e) or "Tool" in str(e) or "Expected assistant role" in str(e):
                workflow.conversations.append({
                    "role": "assistant",
                    "content": f"Error: {str(e)}",
                })
            else:
                raise e

        log_dir = task.to_log_dir()
        if log_tag:
            log_dir = log_dir / log_tag
        log_dir.mkdir(parents=True, exist_ok=True)

        def _to_jsonable(o):
            if isinstance(o, (str, int, float, bool)) or o is None:
                return o
            if isinstance(o, dict):
                return {k: _to_jsonable(v) for k, v in o.items()}
            if isinstance(o, list):
                return [_to_jsonable(x) for x in o]
            fn = getattr(o, 'function', None)
            if fn is not None:
                return {
                    'id': getattr(o, 'id', None),
                    'type': 'function',
                    'function': {
                        'name': getattr(fn, 'name', None),
                        'arguments': getattr(fn, 'arguments', None),
                    },
                }
            return repr(o)

        conv_path = log_dir / "conversation_history.json"
        conversations = getattr(workflow, "conversations", [])
        with open(conv_path, "w", encoding="utf-8") as f:
            json.dump(_to_jsonable(conversations), f, ensure_ascii=False, indent=2)

        base = task.to_base_commit()
        repo_root_in_container = "/testbed"
        patch_in_container = "/tmp/patch.diff"
        stage_cmd = f"bash -lc 'cd {repo_root_in_container} && git add -A'"
        runtime.execute(input=stage_cmd, timeout=120)
        diff_cmd = f"""bash -lc 'cd {repo_root_in_container} && git diff --cached {base} --binary --full-index \\
            ":(exclude)*.o" ":(exclude)*.a" ":(exclude)*.so" ":(exclude)*.dylib" \\
            ":(exclude)*.pyc" ":(glob,exclude)**/__pycache__/**" \\
            ":(exclude)*.class" ":(exclude)*.jar" ":(exclude)*.exe" ":(exclude)*.dll" \\
            ":(exclude)*.d" ":(exclude).base_commit" \\
            ":(exclude)test.sh" ":(glob,exclude)**/tests/**" \\
            ":(glob,exclude)**/conftest.py" \\
            ":(glob,exclude)**/pytest.ini" ":(glob,exclude)**/.pytest.ini" \\
            ":(glob,exclude)**/tox.ini" ":(glob,exclude)**/noxfile.py" \\
            > {patch_in_container}'"""
        runtime.execute(input=diff_cmd, timeout=120)
        runtime.transfer_file(patch_in_container, str(log_dir / "patch"), to_container=False)
    finally:
        runtime.stop()


if __name__ == "__main__":
    asyncio.run(main())
