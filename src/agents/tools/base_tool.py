# SPDX-License-Identifier: Apache-2.0
from src.runtime.base_runtime import BaseRuntime


class BaseTool:
    def __init__(self, tool_call_id: str, **params) -> None:
        self.params = params
        self.tool_call_id = tool_call_id
        self.valid_parameters()  # valid self.params
    
    async def run(self, runtime: BaseRuntime) -> str:
        raise NotImplementedError
    
    @classmethod
    def get_tool_schema(cls) -> dict:
        raise NotImplementedError

    @classmethod
    def tool_name(cls) -> str:
        return cls.get_tool_schema()['function']['name']
    
    def valid_parameters(self) -> None:
        schema = self.get_tool_schema()
        required_params = schema['function']['parameters']['required']
        for param in required_params:
            if param not in self.params:
                raise ValueError(f"Missing required parameter: {param}")
