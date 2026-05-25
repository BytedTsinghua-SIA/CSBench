"""Node class for solution tree representation."""

import time
import uuid
from dataclasses import dataclass, field
from typing import Literal, Optional, TYPE_CHECKING, Any

from dataclasses_json import DataClassJsonMixin

if TYPE_CHECKING:
    from interpreter import ExecutionResult


@dataclass(eq=False)
class Node(DataClassJsonMixin):
    """A single node in the solution tree. Contains code, execution results, and evaluation information."""

    code: str
    plan: str = field(default=None, kw_only=True)
    step: int = field(default=None, kw_only=True)
    id: str = field(default_factory=lambda: uuid.uuid4().hex, kw_only=True)
    ctime: float = field(default_factory=lambda: time.time(), kw_only=True)
    parent: Optional["Node"] = field(default=None, kw_only=True)
    children: set["Node"] = field(default_factory=set, kw_only=True)
    _term_out: list[str] = field(default=None, kw_only=True)
    exec_time: float = field(default=None, kw_only=True)
    exc_type: str | None = field(default=None, kw_only=True)
    exc_info: dict | None = field(default=None, kw_only=True)
    exc_stack: list[tuple] | None = field(default=None, kw_only=True)
    analysis: str = field(default=None, kw_only=True)
    metric: float = field(default=None, kw_only=True)
    is_buggy: bool = field(default=None, kw_only=True)

    def __post_init__(self) -> None:
        if self.parent is not None:
            self.parent.children.add(self)

    @property
    def stage_name(self) -> Literal["draft", "debug", "improve"]:
        raise NotImplementedError

    def absorb_exec_result(self, exec_result: Any):
        raise NotImplementedError

    @property
    def term_out(self) -> str:
        raise NotImplementedError

    @property
    def is_leaf(self) -> bool:
        raise NotImplementedError

    def __eq__(self, other):
        return isinstance(other, Node) and self.id == other.id

    def __hash__(self):
        return hash(self.id)

    @property
    def debug_depth(self) -> int:
        raise NotImplementedError

