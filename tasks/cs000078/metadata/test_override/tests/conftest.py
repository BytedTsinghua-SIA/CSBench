import os
import sys

import pytest
import torch

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from config import BertConfig


@pytest.fixture(scope="session")
def tiny_config():
    return BertConfig(
        vocab_size=32,
        hidden_size=8,
        num_hidden_layers=1,
        num_attention_heads=2,
        intermediate_size=16,
        max_position_embeddings=16,
        type_vocab_size=2,
        hidden_dropout_prob=0.0,
        attention_probs_dropout_prob=0.0,
        pad_token_id=0,
    )


@pytest.fixture
def attention_inputs(tiny_config):
    torch.manual_seed(0)
    hidden = torch.randn(2, 3, tiny_config.hidden_size)
    mask = torch.zeros(hidden.size(0), 1, 1, hidden.size(1))
    return hidden, mask
