# Copyright (c) 2025 ByteDance Ltd. and/or its affiliates
# SPDX-License-Identifier: Apache-2.0
import json
from dataclasses import dataclass
import inspect
import uuid

from src.agents.tools.base_tool import BaseTool
from src.runtime.base_runtime import BaseRuntime
from src.task.bench_task import BenchTask
from src.agents.utils.llm import LLMConfig, call_llm as _call_llm

@dataclass
class WorkflowConfig:
    llm_config: LLMConfig
    max_turns: int = 50

class BaseWorkflow:
    def __init__(self, config: WorkflowConfig) -> None:
        self.config = config
        self.conversations: list[dict] = []
        self.conversation_history = []
        self.tools = []
        self.use_responses_api = config.llm_config.api_mode.lower() == "responses"
        self.previous_response_id: str | None = None
        self.responses_input_cursor = 0
        self.csbench_session_id = f"csbench-{uuid.uuid4()}"
    
    async def run(self, runtime: BaseRuntime, task: BenchTask) -> None:
        raise NotImplementedError

    def get_tool_schema(self) -> list[dict]:
        assert all(inspect.isclass(t) and issubclass(t, BaseTool) for t in self.tools)
        tool_schema = [t.get_tool_schema() for t in self.tools]
        return tool_schema

    def call_llm(self, conversations: list[dict], **kwargs):
        request_messages = conversations
        if self.use_responses_api and self.previous_response_id:
            request_messages = conversations[self.responses_input_cursor:]
            kwargs["previous_response_id"] = self.previous_response_id

        extra_headers = dict(self.config.llm_config.extra_headers or {})
        extra_headers["extra"] = json.dumps({"session_id": self.csbench_session_id})
        kwargs["extra_headers"] = extra_headers

        if self.use_responses_api:
            print("role:", [x['role'] for x in request_messages])
            print(f"{self.csbench_session_id=}") # for azure router

        resp = _call_llm(self.config.llm_config, request_messages, **kwargs)
        if self.use_responses_api:
            response_id = resp.id
            assert response_id, "Response API returned an empty `id`."
            self.previous_response_id = response_id
            self.responses_input_cursor = len(conversations) + 1 # skip the assistant message
            print(resp.usage)
        return resp

    def get_tool_calls_payload(self, resp) -> list[dict]:
        if self.use_responses_api:
            payloads = []
            for item in list(resp.output):
                if item.type != "function_call":
                    continue
                call_id = item.call_id
                function_name = item.name
                arguments = item.arguments
                assert call_id, "Response API function_call item must include a non-empty `call_id`."
                assert function_name, "Response API function_call item must include a non-empty `name`."
                assert isinstance(arguments, str), "Response API function_call item `arguments` must be a JSON string."
                payloads.append({
                    "id": call_id,
                    "type": "function",
                    "function": {
                        "name": function_name,
                        "arguments": arguments,
                    },
                })
            return payloads
        return resp.choices[0].message.tool_calls or []

    # === Helpers ===
    def extract_assistant_message(self, resp) -> str | None:
        if self.use_responses_api:
            messages = []
            output_items = list(resp.output)
            for item in output_items:
                item_type = item.type
                if item_type != "message":
                    continue
                assert item.role == "assistant", f"Expected assistant role, got {role}"

                content_items = item.content
                for content in content_items:
                    content_type = content.type
                    text = content.text
                    assert content_type in {"output_text", "text"}, f"Unsupported response content type: {content_type}"
                    assert isinstance(text, str), "Response API assistant content `text` must be a string."
                    messages.append(text)
            if messages:
                return "".join(messages)
            for item in output_items:
                if item.type == "function_call":
                    return None
            return None

        message = resp.choices[0].message
        role = message.role
        content = message.content
        if role != "assistant":
            raise AssertionError(f"Expected assistant role, got {role}")
        return content

    def parse_tool_calls(self, resp) -> list[BaseTool]:
        # Try OpenAI-like tool_calls
        tcalls = self.get_tool_calls_payload(resp)

        # Build name -> tool class map
        name_to_tool = {}
        for t in self.tools:
            tool_name = t.tool_name()
            name_to_tool[tool_name] = t

        parsed_tools = []
        for tc in tcalls:
            if isinstance(tc, dict):
                assert "function" in tc and "id" in tc, "Tool call payload dict must include `id` and `function`."
                fn_obj = tc["function"]
                assert "name" in fn_obj and "arguments" in fn_obj, "Tool call payload function must include `name` and `arguments`."
                fn = fn_obj["name"]
                args_str = fn_obj["arguments"]
                tool_call_id = tc["id"]
            else:
                fn = tc.function.name
                args_str = tc.function.arguments
                tool_call_id = tc.id

            assert isinstance(args_str, str), f"Tool call arguments for `{fn}` must be a JSON string."
            args_json = json.loads(args_str)
            
            if fn not in name_to_tool:
                raise ValueError(f"Tool {fn} not found")
            
            fn_cls = name_to_tool[fn]
            tool_instance = fn_cls(tool_call_id=tool_call_id, **args_json)
            parsed_tools.append(tool_instance)
        
        if len(tcalls) > 1:
            raise ValueError(f"Multiple tools called: {tcalls}")
            parsed_tools = parsed_tools[:1]
        
        return parsed_tools
