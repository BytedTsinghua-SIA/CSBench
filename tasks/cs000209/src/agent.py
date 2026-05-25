"""Agent class for LLM-driven code generation and improvement."""

from typing import Any, Callable

from nodes import Node
from tree import Journal
from interpreter import ExecutionResult

# Type alias for execution callback
ExecCallbackType = Callable[[str, bool], ExecutionResult]


class Agent:
    """Agent that uses LLM to generate, improve, and debug code solutions."""
    
    def __init__(
        self,
        cfg: Any,
        journal: Journal,
        llm_model: Any,
    ):
        self.cfg = cfg
        self.journal = journal
        self.llm_model = llm_model
        self.data_preview = None

    def search_policy(self) -> Node | None:
        raise NotImplementedError

    def plan_and_code_query(
        self, 
        system_message: str, 
        user_message: str, 
        retries: int = 3
    ) -> tuple[str, str]:
        raise NotImplementedError

    def _draft(self) -> Node:
        raise NotImplementedError

    def _improve(self, parent_node: Node) -> Node:
        raise NotImplementedError

    def _debug(self, parent_node: Node) -> Node:
        raise NotImplementedError

    def update_data_preview(self) -> None:
        raise NotImplementedError

    def step(self, exec_callback: ExecCallbackType) -> None:
        raise NotImplementedError

    def parse_exec_result(self, node: Node, exec_result: ExecutionResult) -> None:
        raise NotImplementedError

