"""
Python interpreter for executing code snippets and capturing their output.

DO NOT MODIFY THIS CELL
"""

from dataclasses import dataclass
from dataclasses_json import DataClassJsonMixin


@dataclass
class ExecutionResult(DataClassJsonMixin):
    """
    Result of executing a code snippet in the interpreter.
    Contains the output, execution time, and exception information.
    """
    term_out: list[str]
    exec_time: float
    exc_type: str | None
    exc_info: dict | None = None
    exc_stack: list[tuple] | None = None


def exception_summary(e: BaseException, exec_file_name: str) -> tuple[str, str, dict, list[tuple]]:
    raise NotImplementedError


class RedirectQueue:
    """Redirects stdout/stderr to a queue."""
    
    def __init__(self, queue, timeout: int = 5):
        pass

    def write(self, msg: str):
        raise NotImplementedError

    def flush(self):
        pass


class Interpreter:
    """Simulates a standalone Python REPL with an execution time limit."""
    
    def __init__(
        self,
        timeout: int = 3600,
        agent_file_name: str = "runfile.py",
    ):
        self.timeout = timeout
        self.agent_file_name = agent_file_name
        self.process = None

    def child_proc_setup(self, result_outq) -> None:
        raise NotImplementedError

    def _run_session(
        self, code_inq, result_outq, event_outq
    ) -> None:
        raise NotImplementedError

    def create_process(self) -> None:
        raise NotImplementedError

    def cleanup_session(self):
        pass

    def run(self, code: str, reset_session: bool = True) -> ExecutionResult:
        raise NotImplementedError

