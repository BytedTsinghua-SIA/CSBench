# Copyright (c) 2025 ByteDance Ltd. and/or its affiliates
# SPDX-License-Identifier: Apache-2.0
import os

from src.agents.tools.base_tool import BaseTool
from src.runtime.base_runtime import BaseRuntime


class StrReplaceTool(BaseTool):
    STR_REPLACE_DESC = """
Custom editing tool for viewing, creating and editing files in plain-text format
* State is persistent across command calls and discussions with the user
* If `path` is a file, `view` displays the result of applying `cat -n`. If `path` is a directory, `view` lists non-hidden files and directories up to 2 levels deep
* The `create` command cannot be used if the specified `path` already exists as a file
* If a `command` generates a long output, it will be truncated and marked with `<response clipped>`

Notes for using the `str_replace` command:
* The `old_str` parameter should match EXACTLY one or more consecutive lines from the original file. Be mindful of whitespaces!
* If the `old_str` parameter is not unique in the file, the replacement will not be performed. Make sure to include enough context in `old_str` to make it unique
* The `new_str` parameter should contain the edited lines that should replace the `old_str`
"""

    def __init__(self, **params) -> None:
        super().__init__(**params)

    async def run(self, runtime: BaseRuntime) -> str:
        path = self.params["path"]
        command = self.params["command"]

        try:
            if command == "view":
                return await self._view(runtime, path)
            if command == "create":
                return await self._create(runtime, path)
            if command == "str_replace":
                return await self._str_replace(runtime, path)
            if command == "insert":
                return await self._insert(runtime, path)
            return f"Error: Unknown command '{command}'"
        except Exception as e:  # pragma: no cover - unexpected paths reported to caller
            return f"Error executing {command} on {path}: {str(e)}"

    async def _view(self, runtime: BaseRuntime, path: str) -> str:
        """View file content or directory listing."""
        check_cmd = f"[ -d '{path}' ] && echo 'DIR' || [ -f '{path}' ] && echo 'FILE' || echo 'NOTFOUND'"
        output, exit_code = runtime.execute(check_cmd)
        path_type = output.strip()

        if path_type == "NOTFOUND":
            return f"Error: Path '{path}' does not exist"

        if path_type == "DIR":
            list_cmd = f"find '{path}' -maxdepth 2 -not -path '*/\\.*' | head -n 1000"
            output, exit_code = runtime.execute(list_cmd)
            if exit_code == 0:
                lines = output.strip().split("\n")
                formatted_output = "\n".join(lines[:500])
                if len(lines) > 500:
                    formatted_output += "\n<response clipped>"
                return f"=== Directory listing of {path} ===\n{formatted_output}\n=== End of listing ==="
            return f"Error listing directory {path}: {output}"

        # Viewing file logic
        view_range = self.params.get("view_range")
        
        # 为了保证 view 也能看到真实的行号，我们尽量使用 cat -n
        # 但如果只是为了查看内容，不涉及编辑，cat -n 的输出格式通常是可以接受的
        if view_range and len(view_range) == 2:
            start, end = view_range
            if end == -1:
                view_cmd = f"cat -n '{path}' | tail -n +{start}"
            else:
                view_cmd = f"cat -n '{path}' | sed -n '{start},{end}p'"
        else:
            view_cmd = f"cat -n '{path}'"

        output, exit_code = runtime.execute(view_cmd, use_tty=False)
        if exit_code != 0:
            return f"Error viewing file {path}: {output}"

        if isinstance(output, bytes):
            output = output.decode("utf-8", errors="replace")

        line_count = output.count("\n")
        if line_count > 1000:
            lines = output.split("\n", 1000)
            clipped_output = "\n".join(lines[:1000])
            return f"Here's the result of running `cat -n` on {path}:\n{clipped_output}\n<response clipped>"

        return f"Here's the result of running `cat -n` on {path}:\n{output}"

    async def _create(self, runtime: BaseRuntime, path: str) -> str:
        """Create a new file with the given content."""
        file_text = self.params.get("file_text", "")

        check_cmd = f"[ -f '{path}' ] && echo 'EXISTS' || echo 'NOTFOUND'"
        output, exit_code = runtime.execute(check_cmd)
        if output.strip() == "EXISTS":
            return f"Error: File '{path}' already exists. Use str_replace or insert to modify existing files."

        try:
            # Use runtime.write_file which uses docker cp - exact content preservation
            runtime.write_file(path, file_text)
            return f"File created successfully at: {path}"
        except Exception as e:
            return f"Error creating file {path}: {str(e)}"

    async def _str_replace(self, runtime: BaseRuntime, path: str) -> str:
        """Replace old_str with new_str in the file."""
        old_str = self.params.get("old_str")
        new_str = self.params.get("new_str", "")

        if not old_str:
            return "Error: 'old_str' parameter is required for str_replace command"

        try:
            # Use runtime.read_file which uses docker cp - exact content preservation
            original_content = runtime.read_file(path)
        except Exception as e:
            return f"Error reading file {path}: {str(e)}"

        if old_str not in original_content:
            return f"Error: old_str not found in {path}\n\nSearched for:\n{old_str}"

        count = original_content.count(old_str)
        if count > 1:
            return (
                f"Error: old_str appears {count} times in {path}. "
                "It must be unique. Please include more context in old_str to make it unique."
            )

        # Find line number for snippet display
        lines_before = original_content[: original_content.index(old_str)].split("\n")
        start_line = len(lines_before)

        # Perform replacement in Python memory - fully controlled
        new_content = original_content.replace(old_str, new_str, 1)

        try:
            # Use runtime.write_file which uses docker cp - exact content preservation
            runtime.write_file(path, new_content)
        except Exception as e:
            return f"Error writing to file {path}: {str(e)}"

        # Show edit result
        new_lines = new_str.split("\n")
        num_new_lines = len(new_lines)
        context_before = 3
        context_after = 5
        snippet_start = max(1, start_line - context_before)
        snippet_end = start_line + num_new_lines + context_after

        snippet_cmd = f"cat -n '{path}' | sed -n '{snippet_start},{snippet_end}p'"
        snippet_output, snippet_exit_code = runtime.execute(snippet_cmd, use_tty=False)
        if isinstance(snippet_output, bytes):
            snippet_output = snippet_output.decode("utf-8", errors="replace")

        result = f"The file {path} has been edited. Here's the result of running `cat -n` on a snippet of {path}:\n"
        if snippet_exit_code == 0 and snippet_output.strip():
            result += snippet_output
        else:
            result = f"File edited successfully at: {path}"

        result += "\nReview the changes and make sure they are as expected. Edit the file again if necessary."
        return result

    async def _insert(self, runtime: BaseRuntime, path: str) -> str:
        """Insert new_str after the specified line number."""
        insert_line = self.params.get("insert_line")
        new_str = self.params.get("new_str", "")

        if insert_line is None:
            return "Error: 'insert_line' parameter is required for insert command"
        if not new_str:
            return "Error: 'new_str' parameter is required for insert command"

        try:
            # Use runtime.read_file which uses docker cp - exact content preservation
            original_content = runtime.read_file(path)
        except Exception as e:
            return f"Error reading file {path}: {str(e)}"

        lines = original_content.split("\n")
        if insert_line < 0 or insert_line > len(lines):
            return f"Error: insert_line {insert_line} is out of range (file has {len(lines)} lines)"

        new_lines_to_add = new_str.split("\n")
        lines[insert_line:insert_line] = new_lines_to_add
        new_content = "\n".join(lines)

        try:
            # Use runtime.write_file which uses docker cp - exact content preservation
            runtime.write_file(path, new_content)
            return f"Content inserted successfully at line {insert_line} in: {path}"
        except Exception as e:
            return f"Error writing to file {path}: {str(e)}"

    @classmethod
    def get_tool_schema(cls):
        return {
            "type": "function",
            "function": {
                "name": "str_replace",
                "description": StrReplaceTool.STR_REPLACE_DESC,
                "parameters": {
                    "type": "object",
                    "properties": {
                        "command": {
                            "description": "The commands to run. Allowed options are: `view`, `create`, `str_replace`, `insert`.",
                            "enum": ["view", "create", "str_replace", "insert"],
                            "type": "string",
                        },
                        "path": {
                            "description": "Absolute path to file or directory, e.g. `/workspace/file.py` or `/workspace`.",
                            "type": "string",
                        },
                        "file_text": {
                            "description": "Required parameter of `create` command, with the content of the file to be created.",
                            "type": "string",
                        },
                        "old_str": {
                            "description": "Required parameter of `str_replace` command containing the string in `path` to replace.",
                            "type": "string",
                        },
                        "new_str": {
                            "description": "Optional parameter of `str_replace` command containing the new string (if not given, no string will be added). Required parameter of `insert` command containing the string to insert.",
                            "type": "string",
                        },
                        "insert_line": {
                            "description": "Required parameter of `insert` command. The `new_str` will be inserted AFTER the line `insert_line` of `path`.",
                            "type": "integer",
                        },
                        "view_range": {
                            "description": "Optional parameter of `view` command when `path` points to a file. If none is given, the full file is shown. If provided, the file will be shown in the indicated line number range, e.g. [11, 12] will show lines 11 and 12. Indexing at 1 to start. Setting `[start_line, -1]` shows all lines from `start_line` to the end of the file.",
                            "items": {"type": "integer"},
                            "type": "array",
                        },
                    },
                    "required": ["command", "path"],
                },
            },
        }