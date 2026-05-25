import torch

from bert import BertLayer


def test_bert_layer_forward_matches_sequential_ops(tiny_config, attention_inputs):
    layer = BertLayer(tiny_config)
    layer.eval()
    hidden, mask = attention_inputs

    attn_value = layer.self_attention(hidden, mask)
    first_add = layer.add_norm(hidden, attn_value, layer.attention_dense, layer.attention_dropout, layer.attention_layer_norm)
    feed_forward = layer.interm_af(layer.interm_dense(first_add))
    expected = layer.add_norm(first_add, feed_forward, layer.out_dense, layer.out_dropout, layer.out_layer_norm)

    actual = layer(hidden, mask)
    assert actual.shape == hidden.shape
    assert torch.allclose(actual, expected, atol=1e-6)
