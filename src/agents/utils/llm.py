# SPDX-License-Identifier: Apache-2.0
from __future__ import annotations
from dataclasses import dataclass
from typing import Any, Dict, List, Optional
from tenacity import retry, wait_exponential, stop_after_attempt
import litellm
import os

from src.config import load_env
load_env()



@dataclass
class LLMConfig:
    provider: str  # "openai" | "azure" | "anthropic"
    model: str
    api_key: Optional[str] = None
    api_base: Optional[str] = None
    api_version: Optional[str] = None  # Azure only
    azure_deployment: Optional[str] = None  # Azure: overrides model when provided
    timeout: Optional[float] = 30.0
    temperature: Optional[float] = None
    max_tokens: Optional[int] = None
    top_p: Optional[float] = None
    extra_headers: Optional[Dict[str, str]] = None
    api_mode: str = "chat"  # "chat" | "responses"

    ## 验证参数
    def __post_init__(self):
        valid_provider = ["openai", "azure", "anthropic", "openrouter"]
        valid_api_mode = ["chat", "responses"]
        assert self.provider.lower() in valid_provider, f"Invalid provider: {self.provider}, valid providers are {valid_provider}"
        assert self.api_mode.lower() in valid_api_mode, f"Invalid api_mode: {self.api_mode}, valid api_modes are {valid_api_mode}"

    def to_litellm_args(self) -> Dict[str, Any]:
        args: Dict[str, Any] = {}
        # Model routing
        if self.provider.lower() == "azure":
            # Use azure/<deployment_name> for explicit routing
            deployment = self.azure_deployment or self.model
            args["model"] = f"azure/{deployment}"
            if self.api_base:
                args["api_base"] = self.api_base
            if self.api_version:
                args["api_version"] = self.api_version
            if self.api_key:
                args["api_key"] = self.api_key
        elif self.provider.lower() == "anthropic":
            # Either anthropic/<model> or plain model; prefix to be explicit
            args["model"] = f"anthropic/{self.model}"
            if self.api_base:
                args["api_base"] = self.api_base
            if self.api_key:
                args["api_key"] = self.api_key
        elif self.provider.lower() == "openrouter":
            # openrouter/<model>
                args["model"] = f"openrouter/{self.model}"
                if self.api_base:
                    args["api_base"] = self.api_base
                if self.api_key:
                    args["api_key"] = self.api_key
        else:  # openai (default)
            args["model"] = f"openai/{self.model}"
            if self.api_base:
                args["api_base"] = self.api_base
            if self.api_key:
                args["api_key"] = self.api_key

        # Common optional params
        if self.timeout is not None:
            args["timeout"] = self.timeout
        if self.temperature is not None:
            args["temperature"] = self.temperature
        if self.max_tokens is not None:
            args["max_tokens"] = self.max_tokens
        if self.top_p is not None:
            args["top_p"] = self.top_p
        if self.extra_headers:
            args["extra_headers"] = self.extra_headers
        return args




def _responses_tools_from_chat_tools(tools: Any) -> Any:
    if not isinstance(tools, list):
        return tools

    normalized_tools = []
    for tool in tools:
        if not isinstance(tool, dict):
            normalized_tools.append(tool)
            continue

        if tool.get("type") == "function" and isinstance(tool.get("function"), dict):
            function_def = tool["function"]
            normalized_tools.append({
                "type": "function",
                "name": function_def.get("name"),
                "description": function_def.get("description"),
                "parameters": function_def.get("parameters", {}),
            })
        else:
            normalized_tools.append(tool)
    return normalized_tools

def _messages_to_responses_input(messages: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    responses_input: List[Dict[str, Any]] = []

    for message in messages:
        role = message.get("role")
        if role in {"system", "user", "assistant"}:
            content = message.get("content")
            assert content and isinstance(content, str), "Expects message content to be a plain string."
            responses_input.append({
                "type": "message",
                "role": role,
                "content": [{"type": "input_text", "text": content}],
            })

            if role == "assistant":
                for tool_call in message.get("tool_calls") or []:
                    if not isinstance(tool_call, dict):
                        continue
                    function_def = tool_call.get("function") or {}
                    responses_input.append({
                        "type": "function_call",
                        "call_id": tool_call.get("id"),
                        "name": function_def.get("name"),
                        "arguments": function_def.get("arguments", "{}"),
                    })
        elif role == "tool":
            responses_input.append({
                "type": "function_call_output",
                "call_id": message.get("tool_call_id"),
                "output": message.get("content", ""),
            })

    return responses_input

def call_llm(config: LLMConfig, messages: List[Dict[str, Any]], stream: bool = False, **kwargs: Any) -> Any:
    """
    Updated version of llm call using litellm with custom retry wrapper.
    STRICTLY disables litellm's internal retry mechanism in favor of the custom tenacity wrapper.
    """
    # 1. Prepare base args from config
    llm_args = config.to_litellm_args()
    
    # 2. Update with kwargs and method args
    llm_args.update(kwargs)
    api_mode = str(llm_args.pop("api_mode", config.api_mode or "chat")).lower()
    previous_response_id = llm_args.pop("previous_response_id", None)
    if "doubao" in config.model:
        print("doubao")
        for m in messages:
            if m["role"] == "system":
                m["role"] = "user"
    print(config)
    llm_args["stream"] = stream
    if api_mode == "responses":
        llm_args["input"] = _messages_to_responses_input(messages)
        llm_args["tools"] = _responses_tools_from_chat_tools(llm_args.get("tools"))
        if previous_response_id is not None:
            llm_args["previous_response_id"] = previous_response_id
        if "max_tokens" in llm_args and "max_output_tokens" not in llm_args:
            llm_args["max_output_tokens"] = llm_args.pop("max_tokens")
    else:
        llm_args["messages"] = messages
    
    # 3. STRICTLY DISABLE litellm's internal retry
    llm_args["max_retries"] = 0
    
    # 4. Handle API Key rotation logic (if applicable)
    # The current LLMConfig might have comma-separated keys.
    base_api_key = llm_args.get("api_key")
    api_keys = [k.strip() for k in base_api_key.split(",")] if (base_api_key and "," in base_api_key) else None

    # 5. Define retry callback
    def _before_sleep_print(retry_state):
        exc = retry_state.outcome.exception() if retry_state.outcome else None
        if exc:
            import datetime
            print(f"{datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')} [LiteLLM] Retry {retry_state.attempt_number}: {str(exc)}")

    # 6. Define the wrapped call
    retry_time = 0

    def predicate(exc: BaseException) -> bool:
        untriable_msgs = [
            "Request contains an invalid argument",
            "invalid_parameter_error",
            "context_length_exceeded",
            "Exceeded limit on max bytes to request body"
        ]
        return isinstance(exc, Exception) and not any(ue in str(exc) for ue in untriable_msgs)

    from tenacity import retry_if_exception
    @retry(
        retry=retry_if_exception(predicate),
        wait=wait_exponential(multiplier=5, min=5, max=90),
        stop=stop_after_attempt(10),
        reraise=True,
        before_sleep=_before_sleep_print
    )
    def _do_call() -> Any:
        nonlocal retry_time
        retry_time += 1
        # If we have multiple keys, rotate them
        if api_keys:
            current_key = api_keys[(retry_time - 1) % len(api_keys)]
            llm_args["api_key"] = current_key
        if api_mode == "responses":
            if not hasattr(litellm, "responses"):
                raise RuntimeError("The installed litellm package does not support responses(). Please upgrade litellm.")
            return litellm.responses(**llm_args)
        return litellm.completion(**llm_args)

    try:
        return _do_call()
    except Exception as e:
        print(f"Final Error: {str(e)}")
        raise

if __name__ == "__main__":
    import dotenv
    import json

    dotenv.load_dotenv(os.getenv("ENV_FILE", ""))
    if os.getenv("PROVIDER") is None or os.getenv("API_MODEL") is None:
        raise ValueError("PROVIDER and API_MODEL must be set in the environment variables.")
    cfg = LLMConfig(
        provider=os.getenv("PROVIDER"), # type: ignore
        model=os.getenv("API_MODEL"), # type: ignore
        api_key=os.getenv("API_KEY"),
        api_base=os.getenv("API_BASE"),
        api_version=os.getenv("OPENAI_API_VERSION"),
        azure_deployment=None,
        timeout=float(os.getenv("API_TIMEOUT", "30.0")),
        max_tokens=16,
        api_mode="responses",
    )
    session = "qaq-cs-test"

    resp1 = call_llm(
        cfg,
        [{"role": "user", "content": "ping" * 1100}],
        stream=False,
        store=True,
        extra_headers={"extra": json.dumps({"session_id": session})},
    )
    assert resp1.id
    print("resp1.id:", resp1.id)

    resp2 = call_llm(
        cfg,
        [{"role": "user", "content": "pong"}],
        stream=False,
        store=True,
        previous_response_id=resp1.id,
        extra_headers={"extra": json.dumps({"session_id": session})},
    )
    assert resp2.id
    print("resp2.id:", resp2.id)
    print(f"{resp2.usage=}")
