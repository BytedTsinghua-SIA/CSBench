import torch

import dataset
import model


def test_vanilla_gpt_forward_shapes():
    cfg = model.GPTConfig(
        vocab_size=32,
        block_size=16,
        n_layer=2,
        n_head=2,
        n_embd=16,
    )
    net = model.GPT(cfg)

    # Leverage the corruption dataset to provide realistic token batches.
    ds = dataset.CharCorruptionDataset("hello world! this is a test corpus", block_size=cfg.block_size)
    x, y = ds[0]
    x = x.unsqueeze(0)
    y = y.unsqueeze(0)

    logits, loss = net(x, y)
    assert logits.shape == (1, cfg.block_size, cfg.vocab_size)
    assert loss.ndim == 0
