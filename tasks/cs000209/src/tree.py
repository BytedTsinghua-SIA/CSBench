"""Journal class for managing solution tree."""

from dataclasses import dataclass, field
from dataclasses_json import DataClassJsonMixin

from nodes import Node


@dataclass
class Journal(DataClassJsonMixin):
    """A collection of nodes representing the solution tree."""

    nodes: list[Node] = field(default_factory=list)

    def __getitem__(self, idx: int) -> Node:
        return self.nodes[idx]

    def __len__(self) -> int:
        return len(self.nodes)

    def append(self, node: Node) -> None:
        raise NotImplementedError

    @property
    def draft_nodes(self) -> list[Node]:
        raise NotImplementedError

    @property
    def buggy_nodes(self) -> list[Node]:
        raise NotImplementedError

    @property
    def good_nodes(self) -> list[Node]:
        raise NotImplementedError

    def get_metric_history(self) -> list[float]:
        raise NotImplementedError

    def get_good_nodes(self) -> list[Node]:
        raise NotImplementedError

    def get_best_node(self, only_good: bool = True) -> None | Node:
        raise NotImplementedError

    def generate_summary(self, include_code: bool = False) -> str:
        raise NotImplementedError

