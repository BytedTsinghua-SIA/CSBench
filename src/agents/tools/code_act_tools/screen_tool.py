# Copyright (c) 2025 ByteDance Ltd. and/or its affiliates
# SPDX-License-Identifier: Apache-2.0
from src.agents.tools.base_tool import BaseTool
from src.runtime.base_runtime import BaseRuntime, StatefulRuntime
import time
from typing import Coroutine, Any

class ScreenTool(BaseTool):
    
    SCREEN_TOOL_DESC = """Manage interactive screen sessions, similar to tmux. Allows running long-running or interactive commands.

Sessions are persistent across tool calls. You must specify an action:
- `create`: Start a new screen session.
- `send`: Send keys or commands to a session. To execute a command, use the '[enter]' key sequence.
- `capture`: Capture the visible text from a session.
- `stop`: Terminate a screen session.

Special key sequences supported:
- '[enter]' or '[return]' for Enter key
- '[ctrl-c]' or '[^c]' for Ctrl+C
- '[ctrl-d]' or '[^d]' for Ctrl+D
- '[tab]' for Tab key
- '[space]' for Space key
- '[esc]' for Escape key

To input literal brackets, use '[[' for '[' and ']]' for ']'.

Examples:
- To execute 'ls -l', send 'ls -l[enter]'
- To send Ctrl+C, send '[ctrl-c]'
- To send multiple commands: 'ls -l[enter]pwd[enter]'
- To send literal '[enter]': '[[enter]]'
"""
    
    def __init__(self, **params) -> None:
        super().__init__(**params)
    
    async def run(self, runtime: StatefulRuntime) -> str:
        action = self.params.get("action")
        screen_name = self.params.get("screen_name")


        if not screen_name:
            return "Error: screen_name must be provided."

        try:
            if action == "create":
                runtime.create_screen(screen_name)
                return f"Screen session '{screen_name}' created successfully."
            
            elif action == "send":
                keys = self.params.get("keys")
                if keys is None:
                    return "Error: 'keys' parameter is required for 'send' action."
                
                runtime.send_keys(screen_name, keys)
                
                wait_and_capture_seconds = self.params.get("wait_and_capture_seconds")
                if wait_and_capture_seconds is not None:
                    time.sleep(wait_and_capture_seconds)
                    output = runtime.capture_screen(screen_name)
                    return f"""Sent keys to screen '{screen_name}' and captured after {wait_and_capture_seconds}s:
=== Screen content of '{screen_name}' ===
{output}
=== End of screen content ===
"""
                else:
                    return f"Sent keys to screen '{screen_name}'."

            elif action == "capture":
                output = runtime.capture_screen(screen_name)
                return f"""=== Screen content of '{screen_name}' ===
{output}
=== End of screen content ===
"""

            elif action == "stop":
                runtime.stop_screen(screen_name)
                return f"Screen session '{screen_name}' stopped."

            else:
                return f"Error: Invalid action '{action}'. Must be one of ['create', 'send', 'capture', 'stop']."
        
        except Exception as e:
            return f"Error executing screen action '{action}' on session '{screen_name}': {e}"

    @classmethod
    def get_tool_schema(cls):
        return {
            'type': 'function',
            'function': {
                'name': 'screen',
                'description': cls.SCREEN_TOOL_DESC,
                'parameters': {
                    'type': 'object',
                    'properties': {
                        'action': {
                            'type': 'string',
                            'description': 'The action to perform on the screen session.',
                            'enum': ['create', 'send', 'capture', 'stop']
                        },
                        'screen_name': {
                            'type': 'string',
                            'description': 'A user-defined name for the screen session to operate on.'
                        },
                        'keys': {
                            'type': 'string',
                            'description': "The keys or commands to send. Required for the 'send' action. To execute a command, it must end with the '[enter]' key sequence. Special key sequences like '[enter]', '[ctrl-c]' will be automatically converted. To input literal brackets, use '[[' for '[' and ']]' for ']'. Examples: 'ls -l[enter]' to execute the ls command, '[enter]' to send an enter key, '[[enter]]' to send the literal string '[enter]'."
                        },
                        'wait_and_capture_seconds': {
                            'type': 'number',
                            'description': "Optional. If provided for the 'send' action, wait this many seconds after sending keys, then capture and return the screen content. This avoids a separate 'capture' call."
                        }
                    },
                    'required': ['action', 'screen_name'],
                },
            },
        }