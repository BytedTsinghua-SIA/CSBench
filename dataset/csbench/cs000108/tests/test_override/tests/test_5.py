from nltk import Tree

import pathlib
import sys

import pytest

ROOT = pathlib.Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
import parser
from pathlib import Path

def test_np_chunk_excludes_parent_when_nested_np_present():
    tree = Tree.fromstring(
        """
        (S
          (NP (Det the) (N day))
          (VP
            (V had)
            (NP
              (Det a)
              (N walk)
              (PP (P on) (NP (N thursday)))
            )
          )
        )
        """
    )
    chunks = parser.np_chunk(tree)
    chunk_words = {" ".join(chunk.flatten()) for chunk in chunks}
    assert chunk_words == {"the day", "thursday"}
