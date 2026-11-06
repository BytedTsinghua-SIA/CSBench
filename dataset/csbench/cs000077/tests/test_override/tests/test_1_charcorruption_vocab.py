import dataset


def test_charcorruption_vocab_specification():
    text = "dcba"
    ds = dataset.CharCorruptionDataset(text, block_size=32)

    assert ds.itos[0] == ds.PAD_CHAR
    assert ds.itos[1] == ds.MASK_CHAR

    sorted_chars = sorted(set(text))
    observed_chars = [ds.itos[idx] for idx in range(2, 2 + len(sorted_chars))]
    assert observed_chars == sorted_chars

    for ch in sorted_chars:
        assert ds.stoi[ch] >= 2

    # __getitem__ must be implemented so we can fetch training pairs.
    x, y = ds[0]
    assert x.shape == (ds.block_size,)
    assert y.shape == (ds.block_size,)

    # __getitem__ must be implemented so we can fetch training pairs.
    x, y = ds[0]
    assert x.shape == (ds.block_size,)
    assert y.shape == (ds.block_size,)
