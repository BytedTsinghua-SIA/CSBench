import pathlib
import sys

import pytest

ROOT = pathlib.Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
import parser
from pathlib import Path

def test_preprocess_strips_non_alpha_tokens():
    sentence = "Holmes, sat 28."
    assert parser.preprocess(sentence) == ["holmes", "sat"]
