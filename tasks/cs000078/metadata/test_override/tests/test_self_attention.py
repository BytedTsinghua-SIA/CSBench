import math

import torch

from bert import BertSelfAttention


def test_self_attention_matches_reference(tiny_config, attention_inputs):
    attn = BertSelfAttention(tiny_config)
    attn.eval()
    hidden, mask = attention_inputs

    key = attn.transform(hidden, attn.key)
    value = attn.transform(hidden, attn.value)
    query = attn.transform(hidden, attn.query)

    scale = math.sqrt(attn.attention_head_size)
    scores = torch.matmul(query, key.transpose(-2, -1)) / scale
    scores = scores + mask
    probs = torch.softmax(scores, dim=-1)
    expected = torch.matmul(probs, value)
    expected = expected.transpose(1, 2).contiguous().view(hidden.size(0), hidden.size(1), -1)

    actual = attn.attention(key, query, value, mask)
    assert torch.allclose(actual, expected, atol=1e-6)
