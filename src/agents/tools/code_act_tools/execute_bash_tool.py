# Copyright (c) 2025 ByteDance Ltd. and/or its affiliates
# SPDX-License-Identifier: Apache-2.0
from src.agents.tools.base_tool import BaseTool
from src.runtime.base_runtime import BaseRuntime
import time

class ExecuteBashTool(BaseTool):
    
    EXECUTE_BASH_DESC = """
Execute a bash command in the terminal.
* Long running commands: For commands that may run indefinitely, it should be run in the background and the output should be redirected to a file, e.g. command = `python3 app.py > server.log 2>&1 &`.
* One command at a time: You can only execute one bash command at a time. If you need to run multiple commands sequentially, you can use `&&` or `;` to chain them together.
    """
    
    def __init__(self, **params) -> None:
        super().__init__(**params)
    
    async def run(self, runtime: BaseRuntime) -> str:
        start_time = time.time()
        run_log, exit_code = runtime.execute(input=self.params["command"], timeout=int(self.params.get("timeout", 30)))
        end_time = time.time()

        # Convert bytes to string
        if isinstance(run_log, bytes):
            run_log_str = run_log.decode('utf-8', errors='replace')
        else:
            run_log_str = str(run_log)
        
        if len(run_log_str) < 25600:
            observation = f"""{run_log_str}

    [Execution time: {end_time - start_time:.6f} seconds]
    [Command finished with exit code {exit_code}]""".strip()
        else:
            observation = f"""[The output of command are too long, truncated to 25600 characters.]
    {run_log_str[:12800]}

    (truncated)

    {run_log_str[-12800:]}
    [Execution time: {end_time - start_time:.6f} seconds]
    [Command finished with exit code {exit_code}]""".strip()

        return observation
    
    @classmethod
    def get_tool_schema(cls):
        return {
            'type': 'function',
            'function': {
                'name': 'execute_bash',
                'description': ExecuteBashTool.EXECUTE_BASH_DESC,
                'parameters': {
                    'type': 'object',
                    'properties': {
                        'command': {
                            'type': 'string',
                            'description': 'The bash command to execute. Can be empty string to view additional logs when previous exit code is `-1`. Can be `C-c` (Ctrl+C) to interrupt the currently running process. Note: You can only execute one bash command at a time. If you need to run multiple commands sequentially, you can use `&&` or `;` to chain them together.',
                        },
                        'timeout': {
                            'type': 'number',
                            'description': 'The timeout for the command in seconds. Defaults to 30.',
                        },
                    },
                    'required': ['command'],
                },
            },
        }