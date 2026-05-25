import pathlib
import sys

import pytest

ROOT = pathlib.Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
import parser
from pathlib import Path

def test_preprocess_retains_alphabetic_tokens():
    sentence = "CS50 is Great!"
    assert parser.preprocess(sentence) == ["cs50", "is", "great"]
