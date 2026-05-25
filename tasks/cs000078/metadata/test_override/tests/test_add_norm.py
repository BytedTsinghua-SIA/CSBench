import torch

from bert import BertLayer


def test_add_norm_combines_residual_and_normalization(tiny_config, attention_inputs):
    layer = BertLayer(tiny_config)
    layer.eval()
    hidden, _ = attention_inputs
    output = torch.randn_like(hidden)

    dense = layer.attention_dense
    dropout = layer.attention_dropout
    norm = layer.attention_layer_norm

    expected = norm(hidden + dropout(dense(output)))
    actual = layer.add_norm(hidden, output, dense, dropout, norm)
    assert torch.allclose(actual, expected, atol=1e-6)
