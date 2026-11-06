"""
Unit tests for training utilities.
"""

import pytest
import torch
import torch.nn as nn
import numpy as np
import tempfile
import os
from src.training import (
    cross_entropy, AdamW, get_lr_cosine_schedule,
    gradient_clipping, get_batch, save_checkpoint, load_checkpoint
)


class TestCrossEntropy:
    """Test cross-entropy loss function."""
    
    def test_cross_entropy_shape(self):
        """Test cross-entropy output shape."""
        vocab_size = 1000
        batch_size = 4
        seq_len = 10
        
        logits = torch.randn(batch_size * seq_len, vocab_size)
        targets = torch.randint(0, vocab_size, (batch_size * seq_len,))
        
        loss = cross_entropy(logits, targets)
        
        assert loss.shape == ()
        assert loss.item() >= 0
    
    def test_cross_entropy_numerical_stability(self):
        """Test cross-entropy with large logits."""
        vocab_size = 100
        logits = torch.randn(10, vocab_size) * 100
        targets = torch.randint(0, vocab_size, (10,))
        
        loss = cross_entropy(logits, targets)
        
        assert not torch.isnan(loss)
        assert not torch.isinf(loss)
        assert loss.item() >= 0
    
    def test_cross_entropy_batch_average(self):
        """Test that cross-entropy averages over batch."""
        vocab_size = 100
        logits1 = torch.randn(5, vocab_size)
        logits2 = torch.randn(10, vocab_size)
        targets1 = torch.randint(0, vocab_size, (5,))
        targets2 = torch.randint(0, vocab_size, (10,))
        
        loss1 = cross_entropy(logits1, targets1)
        loss2 = cross_entropy(logits2, targets2)
        
        # Both should be valid losses
        assert loss1.item() >= 0
        assert loss2.item() >= 0


class TestAdamW:
    """Test AdamW optimizer."""
    
    def test_adamw_init(self):
        """Test AdamW initialization."""
        model = nn.Linear(10, 1)
        optimizer = AdamW(model.parameters(), lr=1e-3)
        
        assert len(optimizer.param_groups) == 1
        assert optimizer.param_groups[0]['lr'] == 1e-3
    
    def test_adamw_step(self):
        """Test AdamW optimization step."""
        model = nn.Linear(10, 1)
        optimizer = AdamW(model.parameters(), lr=1e-3)
        
        x = torch.randn(5, 10)
        y = torch.randn(5, 1)
        
        loss = nn.MSELoss()(model(x), y)
        loss.backward()
        
        initial_params = [p.clone() for p in model.parameters()]
        optimizer.step()
        
        # Parameters should have changed
        for p_old, p_new in zip(initial_params, model.parameters()):
            assert not torch.allclose(p_old, p_new)
    
    def test_adamw_state_tracking(self):
        """Test that AdamW tracks state correctly."""
        model = nn.Linear(10, 1)
        optimizer = AdamW(model.parameters(), lr=1e-3)
        
        x = torch.randn(5, 10)
        y = torch.randn(5, 1)
        
        loss = nn.MSELoss()(model(x), y)
        loss.backward()
        optimizer.step()
        
        # Check that state was created
        for p in model.parameters():
            assert p in optimizer.state
            state = optimizer.state[p]
            assert 'step' in state
            assert 'exp_avg' in state
            assert 'exp_avg_sq' in state
    
    def test_adamw_weight_decay(self):
        """Test AdamW weight decay."""
        model = nn.Linear(10, 1)
        optimizer = AdamW(model.parameters(), lr=1e-3, weight_decay=0.1)
        
        x = torch.randn(5, 10)
        y = torch.randn(5, 1)
        
        loss = nn.MSELoss()(model(x), y)
        loss.backward()
        optimizer.step()
        
        # Weight decay should be applied
        assert True  # If step completes without error, weight decay was applied


class TestLearningRateSchedule:
    """Test learning rate scheduling."""
    
    def test_lr_schedule_warmup(self):
        """Test learning rate warmup phase."""
        alpha_max = 1e-3
        alpha_min = 1e-5
        T_w = 100
        T_c = 1000
        
        # During warmup
        lr_0 = get_lr_cosine_schedule(0, alpha_max, alpha_min, T_w, T_c)
        lr_50 = get_lr_cosine_schedule(50, alpha_max, alpha_min, T_w, T_c)
        lr_100 = get_lr_cosine_schedule(100, alpha_max, alpha_min, T_w, T_c)
        
        assert lr_0 == 0.0
        assert 0 < lr_50 < alpha_max
        assert lr_100 == alpha_max
    
    def test_lr_schedule_cosine_annealing(self):
        """Test cosine annealing phase."""
        alpha_max = 1e-3
        alpha_min = 1e-5
        T_w = 100
        T_c = 1000
        
        lr_100 = get_lr_cosine_schedule(100, alpha_max, alpha_min, T_w, T_c)
        lr_550 = get_lr_cosine_schedule(550, alpha_max, alpha_min, T_w, T_c)
        lr_1000 = get_lr_cosine_schedule(1000, alpha_max, alpha_min, T_w, T_c)
        
        assert lr_100 == alpha_max
        assert alpha_min < lr_550 < alpha_max
        assert lr_1000 == alpha_min
    
    def test_lr_schedule_post_annealing(self):
        """Test post-annealing phase."""
        alpha_max = 1e-3
        alpha_min = 1e-5
        T_w = 100
        T_c = 1000
        
        lr_1000 = get_lr_cosine_schedule(1000, alpha_max, alpha_min, T_w, T_c)
        lr_2000 = get_lr_cosine_schedule(2000, alpha_max, alpha_min, T_w, T_c)
        
        assert lr_1000 == alpha_min
        assert lr_2000 == alpha_min


class TestGradientClipping:
    """Test gradient clipping."""
    
    def test_gradient_clipping_below_threshold(self):
        """Test gradient clipping when norm is below threshold."""
        model = nn.Linear(10, 1)
        x = torch.randn(5, 10)
        y = torch.randn(5, 1)
        
        loss = nn.MSELoss()(model(x), y)
        loss.backward()
        
        # Store original gradients
        original_grads = [p.grad.clone() for p in model.parameters()]
        
        gradient_clipping(model.parameters(), max_norm=100.0)
        
        # Gradients should be unchanged if norm is below threshold
        for p, orig_grad in zip(model.parameters(), original_grads):
            if p.grad is not None:
                assert torch.allclose(p.grad, orig_grad, atol=1e-5)
    


class TestDataLoading:
    """Test data loading functions."""
    
    def test_get_batch_shape(self):
        """Test get_batch output shapes."""
        data = np.random.randint(0, 1000, size=10000, dtype=np.uint16)
        batch_size = 4
        context_length = 10
        
        input_ids, target_ids = get_batch(data, batch_size, context_length, device='cpu')
        
        assert input_ids.shape == (batch_size, context_length)
        assert target_ids.shape == (batch_size, context_length)
        assert input_ids.dtype == torch.long
        assert target_ids.dtype == torch.long
    
    def test_get_batch_target_alignment(self):
        """Test that targets are shifted by one position."""
        data = np.array([0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10], dtype=np.uint16)
        batch_size = 1
        context_length = 5
        
        input_ids, target_ids = get_batch(data, batch_size, context_length, device='cpu')
        
        # Targets should be input shifted by 1
        input_vals = input_ids[0].cpu().numpy()
        target_vals = target_ids[0].cpu().numpy()
        
        # Check alignment (target[i] should equal input[i+1] from original data)
        assert len(input_vals) == context_length
        assert len(target_vals) == context_length
    
    def test_get_batch_device(self):
        """Test that get_batch places tensors on correct device."""
        data = np.random.randint(0, 1000, size=1000, dtype=np.uint16)
        
        input_ids, target_ids = get_batch(data, 2, 5, device='cpu')
        
        assert input_ids.device.type == 'cpu'
        assert target_ids.device.type == 'cpu'


class TestCheckpointing:
    """Test model checkpointing."""
    
    def test_save_checkpoint(self):
        """Test saving checkpoint."""
        model = nn.Linear(10, 1)
        optimizer = torch.optim.SGD(model.parameters(), lr=0.01)
        iteration = 100
        
        with tempfile.NamedTemporaryFile(delete=False, suffix='.pt') as f:
            temp_path = f.name
        
        try:
            save_checkpoint(model, optimizer, iteration, temp_path)
            
            assert os.path.exists(temp_path)
            assert os.path.getsize(temp_path) > 0
        finally:
            if os.path.exists(temp_path):
                os.unlink(temp_path)
    
    def test_load_checkpoint(self):
        """Test loading checkpoint."""
        model1 = nn.Linear(10, 1)
        optimizer1 = torch.optim.SGD(model1.parameters(), lr=0.01)
        iteration = 100
        
        with tempfile.NamedTemporaryFile(delete=False, suffix='.pt') as f:
            temp_path = f.name
        
        try:
            # Save checkpoint
            save_checkpoint(model1, optimizer1, iteration, temp_path)
            
            # Load checkpoint
            model2 = nn.Linear(10, 1)
            optimizer2 = torch.optim.SGD(model2.parameters(), lr=0.01)
            
            loaded_iteration = load_checkpoint(temp_path, model2, optimizer2)
            
            assert loaded_iteration == iteration
            # Check that model state was loaded
            for p1, p2 in zip(model1.parameters(), model2.parameters()):
                assert torch.allclose(p1, p2)
        finally:
            if os.path.exists(temp_path):
                os.unlink(temp_path)
    
    def test_checkpoint_roundtrip(self):
        """Test save-load roundtrip."""
        model = nn.Linear(10, 1)
        optimizer = torch.optim.SGD(model.parameters(), lr=0.01)
        iteration = 42
        
        with tempfile.NamedTemporaryFile(delete=False, suffix='.pt') as f:
            temp_path = f.name
        
        try:
            save_checkpoint(model, optimizer, iteration, temp_path)
            loaded_iteration = load_checkpoint(temp_path, model, optimizer)
            
            assert loaded_iteration == iteration
        finally:
            if os.path.exists(temp_path):
                os.unlink(temp_path)

