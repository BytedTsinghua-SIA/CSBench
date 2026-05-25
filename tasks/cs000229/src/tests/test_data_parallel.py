import sys
from pathlib import Path
import pytest
import torch

# Follow test_example.py format for path handling
cwd = Path(__file__).resolve().parent.parent
sys.path.append(str(cwd))

from data_parallel.dataset import partition_dataset


@pytest.mark.a5_1_1
@pytest.mark.parametrize("total_num", [64, 128, 512])
@pytest.mark.parametrize("split_size", [2, 4, 8])
def test_data_partition(total_num, split_size):
    data = [torch.tensor(i) for i in range(total_num)]
    bsz = total_num // split_size
    partitions = [partition_dataset(i, split_size, data, bsz) for i in range(split_size)]
    visited_sets = set()
    for part in partitions:
        for d in part:
            assert d not in visited_sets
            visited_sets.add(d)
