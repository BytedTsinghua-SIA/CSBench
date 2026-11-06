from unittest.mock import patch

import dataset


def decode(ids, vocab):
    return "".join(vocab[int(i)] for i in ids)


def test_charcorruption_masked_example_structure():
    ds = dataset.CharCorruptionDataset("abcdefghijklmno", block_size=24)
    doc = ds.data[0]
    with patch("dataset.random.randint", return_value=12), patch(
        "dataset.random.gauss", return_value=3.5
    ):
        x, y = ds[0]

    assert len(x) == ds.block_size
    assert len(y) == ds.block_size

    x_str = decode(x, ds.itos)
    y_str = decode(y, ds.itos)
    masked_string = x_str + y_str[-1]

    assert masked_string.count(ds.MASK_CHAR) == 2
    prefix, suffix, masked_and_pads = masked_string.split(ds.MASK_CHAR)
    masked_content = masked_and_pads.rstrip(ds.PAD_CHAR)

    truncated_document = prefix + masked_content + suffix
    assert doc.startswith(truncated_document)
    assert 4 <= len(truncated_document) <= int(ds.block_size * 7 / 8)

    # Shifted target check: input shifted right by one character equals output sans last char.
    assert x_str[1:] == y_str[:-1]
