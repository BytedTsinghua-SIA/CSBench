import torch

import model


def test_perceiver_variant_round_trip_shapes():
    cfg = model.GPTConfig(
        vocab_size=48,
        block_size=20,
        n_layer=4,
        n_head=4,
        n_embd=32,
        perceiver=True,
        bottleneck_dim=8,
    )
    net = model.GPT(cfg)
    assert net.perceiver
    assert hasattr(net, "down_block")
    assert hasattr(net, "up_block")

    sample = torch.randint(0, cfg.vocab_size, (2, cfg.block_size))
    logits, _ = net(sample)
    assert logits.shape == (2, cfg.block_size, cfg.vocab_size)
