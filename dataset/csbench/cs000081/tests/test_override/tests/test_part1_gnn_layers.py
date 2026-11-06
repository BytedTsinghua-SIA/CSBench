import pytest
import torch
from part1_gnn_layers import GraphSage, GAT, GNNStack


@pytest.fixture
def sample_data():
    # Create a small sample graph with 5 nodes and 8 edges
    x = torch.randn(5, 16)  # 5 nodes, 16 features each
    edge_index = torch.tensor([
        [0, 1, 1, 2, 2, 3, 3, 4],
        [1, 0, 2, 1, 3, 2, 4, 3]
    ])
    return x, edge_index


def test_graphsage_initialization():
    # Test if GraphSage initializes correctly
    in_channels = 16
    out_channels = 32
    model = GraphSage(in_channels, out_channels)
    assert model.in_channels == in_channels
    assert model.out_channels == out_channels
    assert model.lin_l is not None
    assert model.lin_r is not None


def test_graphsage_forward(sample_data):
    # Test if GraphSage forward pass works
    x, edge_index = sample_data
    model = GraphSage(16, 32)
    # Mock the linear layers to avoid initialization issues
    model.lin_l = torch.nn.Linear(16, 32)
    model.lin_r = torch.nn.Linear(16, 32)
    try:
        output = model(x, edge_index)
        assert output.shape == (5, 32)
    except Exception as e:
        pytest.fail(f"GraphSage forward failed: {e}")


def test_gat_initialization():
    # Test if GAT initializes correctly
    in_channels = 16
    out_channels = 32
    heads = 2
    model = GAT(in_channels, out_channels, heads=heads)
    assert model.in_channels == in_channels
    assert model.out_channels == out_channels
    assert model.heads == heads
    assert model.lin_l is not None
    assert model.lin_r is not None
    assert model.att_l is not None
    assert model.att_r is not None


def test_gat_forward(sample_data):
    # Test if GAT forward pass works
    x, edge_index = sample_data
    model = GAT(16, 32, heads=2)
    # Mock the linear layers and attention parameters
    model.lin_l = torch.nn.Linear(16, 32 * 2)  # 2 heads
    model.lin_r = model.lin_l
    model.att_l = torch.nn.Parameter(torch.randn(2, 32))
    model.att_r = torch.nn.Parameter(torch.randn(2, 32))
    try:
        output = model(x, edge_index)
        assert output.shape == (5, 2 * 32)  # heads * out_channels
    except Exception as e:
        pytest.fail(f"GAT forward failed: {e}")


@pytest.fixture
def mock_args():
    class Args:
        def __init__(self):
            self.model_type = "GraphSage"
            self.num_layers = 2
            self.heads = 1
            self.dropout = 0.5
    return Args()


def test_gnn_stack_initialization(mock_args):
    # Test if GNNStack initializes correctly
    model = GNNStack(16, 32, 7, mock_args)
    assert len(model.convs) == mock_args.num_layers
    assert len(model.post_mp) > 0