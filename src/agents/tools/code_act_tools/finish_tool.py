# Copyright (c) 2025 ByteDance Ltd. and/or its affiliates
# SPDX-License-Identifier: Apache-2.0
from src.agents.tools.base_tool import BaseTool
from src.runtime.base_runtime import BaseRuntime


class FinishTool(BaseTool):
    
    def __init__(self, **params) -> None:
        super().__init__(**params)
    
    async def run(self, runtime: BaseRuntime) -> str:
        observation = 'The task is complete.'
        return observation
    
    @classmethod
    def get_tool_schema(cls):
        return {
            'type': 'function',
            'function': {
                'name': 'finish',
                'description': """Finish the interaction when the task is complete OR if the assistant cannot proceed further with the task.""",
                'parameters': {
                    'type': 'object',
                    'properties': {},
                    'required': [],
                },
            },
        }
