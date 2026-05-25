from nltk import Tree

import pathlib
import sys

import pytest

ROOT = pathlib.Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
import parser
from pathlib import Path

def test_np_chunk_with_single_noun_phrase():
    tree = Tree.fromstring("(S (NP (N holmes)) (VP (V sat)))")
    chunks = parser.np_chunk(tree)
    chunk_words = [" ".join(chunk.flatten()) for chunk in chunks]
    assert chunk_words == ["holmes"]
