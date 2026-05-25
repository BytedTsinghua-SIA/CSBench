"""Utility functions for saving solutions."""

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from tree import Journal
    from config import Config


def save_run(cfg: "Config", journal: "Journal") -> None:
    raise NotImplementedError

