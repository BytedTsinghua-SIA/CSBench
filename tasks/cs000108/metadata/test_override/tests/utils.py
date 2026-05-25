from pathlib import Path

import nltk

nltk.download("punkt", quiet=True)


def load_parser():
    import parser

    return parser


def load_sentence(name: str) -> str:
    for parent in Path(__file__).resolve().parents:
        candidate = parent / "sentences" / name
        if candidate.is_file():
            return candidate.read_text()
    raise FileNotFoundError(f"Could not locate sentence file: {name}")
