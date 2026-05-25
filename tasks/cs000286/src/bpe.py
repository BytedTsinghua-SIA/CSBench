import re
import regex
from typing import Dict, List, Tuple, Iterable, Iterator, Optional
from collections import Counter, defaultdict
import multiprocessing
from functools import partial


GPT2_PATTERN = r"""'(?:[sdmt]|ll|ve|re)| ?\p{L}+| ?\p{N}+| ?[^\s\p{L}\p{N}]+|\s+(?!\S)|\s+"""


def train_bpe(
    input_path: str,
    vocab_size: int,
    special_tokens: Optional[List[str]] = None
) -> Tuple[Dict[int, bytes], List[Tuple[bytes, bytes]]]:
    pass


class Tokenizer:
    def __init__(
        self,
        vocab: Dict[int, bytes],
        merges: List[Tuple[bytes, bytes]],
        special_tokens: Optional[List[str]] = None
    ):
        self.vocab = vocab
        self.merges = merges
        self.special_tokens = special_tokens or []
    
    @classmethod
    def from_files(
        cls,
        vocab_filepath: str,
        merges_filepath: str,
        special_tokens: Optional[List[str]] = None
    ) -> 'Tokenizer':
        pass
    
    def encode(self, text: str) -> List[int]:
        pass
    
    def encode_iterable(self, iterable: Iterable[str]) -> Iterator[int]:
        pass
    
    def decode(self, ids: List[int]) -> str:
        pass
