import pytest
import torch
from part4_link_prediction import LinkPredModel, train, evaluate


@pytest.fixture
def sample_batch():
    # Create a sample batch for link prediction
    class Batch:
        def __init__(self):
            # 10 nodes with 8 features each
            self.node_feature = torch.randn(10, 8)
            # Message passing edges
            self.edge_index = torch.tensor([
                [0, 1, 2, 3, 4, 5, 6, 7, 8, 9],
                [1, 2, 3, 4, 5, 6, 7, 8, 9, 0]
            ])
            # Supervision edges (4 positive, 4 negative)
            self.edge_label_index = torch.tensor([
                [0, 1, 2, 3, 4, 5, 6, 7],
                [1, 2, 3, 4, 5, 6, 7, 8]
            ])
            # Edge labels (1 for positive, 0 for negative)
            self.edge_label = torch.tensor([1, 1, 1, 1, 0, 0, 0, 0], dtype=torch.float)
        
        def to(self, device):
            # Mock the to method
            return self
    
    return Batch()


def test_link_pred_model_initialization():
    # Test model initialization
    model = LinkPredModel(input_dim=8, hidden_dim=16, num_classes=128)
    assert model.conv1 is not None
    assert model.conv2 is not None
    assert model.loss_fn is not None


def test_link_pred_model_forward(sample_batch):
    # Test forward pass
    model = LinkPredModel(input_dim=8, hidden_dim=16, num_classes=128)
    try:
        pred = model(sample_batch)
        # Should return a tensor with 8 predictions (one for each edge in edge_label_index)
        assert isinstance(pred, torch.Tensor)
        assert pred.shape == (8,)
    except Exception as e:
        pytest.fail(f"LinkPredModel forward failed: {e}")


def test_link_pred_model_loss(sample_batch):
    # Test loss calculation
    model = LinkPredModel(input_dim=8, hidden_dim=16, num_classes=128)
    try:
        # Mock the forward method to return some predictions
        model.forward = lambda x: torch.randn(8)
        loss = model.loss(model(sample_batch), sample_batch.edge_label)
        assert isinstance(loss, torch.Tensor)
        assert loss.shape == ()  # Scalar loss
    except Exception as e:
        pytest.fail(f"LinkPredModel loss calculation failed: {e}")


@pytest.fixture
def mock_dataloaders(sample_batch):
    # Create mock dataloaders
    class MockDataloader:
        def __init__(self, batch):
            self.batch = batch
        
        def __iter__(self):
            yield self.batch
    
    dataloaders = {
        'train': MockDataloader(sample_batch),
        'val': MockDataloader(sample_batch),
        'test': MockDataloader(sample_batch)
    }
    return dataloaders


def test_test_function(sample_batch, mock_dataloaders):
    # Test the test function
    model = LinkPredModel(input_dim=8, hidden_dim=16, num_classes=128)
    
    # Mock the forward method to return deterministic outputs for testing
    def mock_forward(batch):
        # Half 0s and half 1s to get a predictable AUC score
        return torch.tensor([0.1, 0.2, 0.3, 0.4, 0.6, 0.7, 0.8, 0.9])
    
    model.forward = mock_forward
    
    args = {"device": "cpu"}
    try:
        score = evaluate(model, mock_dataloaders['test'], args)
        assert isinstance(score, float)
        assert 0 <= score <= 1
    except Exception as e:
        pytest.fail(f"test function failed: {e}")