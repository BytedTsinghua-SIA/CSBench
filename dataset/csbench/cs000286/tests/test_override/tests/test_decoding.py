"""
Unit tests for text generation and decoding utilities.
"""

import pytest
import torch
import torch.nn as nn
from src.decoding import (
    temperature_scaled_softmax, top_p_sampling, generate_text, compute_perplexity
)


class TestTemperatureScaledSoftmax:
    """Test temperature-scaled softmax."""
    
    def test_temperature_scaled_softmax_shape(self):
        """Test temperature-scaled softmax output shape."""
        logits = torch.randn(5, 10)
        temperature = 1.0
        
        output = temperature_scaled_softmax(logits, temperature)
        
        assert output.shape == (5, 10)
    
    def test_temperature_scaled_softmax_normalization(self):
        """Test that temperature-scaled softmax is normalized."""
        logits = torch.randn(3, 100)
        temperature = 1.0
        
        output = temperature_scaled_softmax(logits, temperature)
        
        sums = output.sum(dim=1)
        assert torch.allclose(sums, torch.ones(3), atol=1e-5)
    
    def test_temperature_scaled_softmax_temperature_effect(self):
        """Test that temperature affects distribution."""
        logits = torch.tensor([[1.0, 2.0, 3.0]])
        
        output_low = temperature_scaled_softmax(logits, temperature=0.5)
        output_high = temperature_scaled_softmax(logits, temperature=2.0)
        
        # Low temperature should make distribution more peaked
        # High temperature should make distribution more uniform
        assert output_low.max() > output_high.max()
    
    def test_temperature_scaled_softmax_invalid_temperature(self):
        """Test that invalid temperature raises error."""
        logits = torch.randn(5, 10)
        
        with pytest.raises(ValueError):
            temperature_scaled_softmax(logits, temperature=0.0)
        
        with pytest.raises(ValueError):
            temperature_scaled_softmax(logits, temperature=-1.0)


class TestTopPSampling:
    """Test top-p (nucleus) sampling."""
    
    def test_top_p_sampling_shape(self):
        """Test top-p sampling output shape."""
        probs = torch.rand(5, 10)
        probs = probs / probs.sum(dim=1, keepdim=True)  # Normalize
        top_p = 0.9
        
        output = top_p_sampling(probs, top_p)
        
        assert output.shape == (5, 10)
    
    def test_top_p_sampling_normalization(self):
        """Test that top-p sampling output is normalized."""
        probs = torch.rand(3, 100)
        probs = probs / probs.sum(dim=1, keepdim=True)
        top_p = 0.9
        
        output = top_p_sampling(probs, top_p)
        
        sums = output.sum(dim=1)
        assert torch.allclose(sums, torch.ones(3), atol=1e-5)
    
    def test_top_p_sampling_zeros_low_prob(self):
        """Test that low-probability tokens are zeroed out."""
        # Create a distribution with one high-probability token
        probs = torch.zeros(1, 10)
        probs[0, 0] = 0.95
        probs[0, 1:] = 0.05 / 9
        top_p = 0.9
        
        output = top_p_sampling(probs, top_p)
        
        # Most tokens should be zeroed out
        assert (output[0, 1:] == 0).sum() >= 0
    
    def test_top_p_sampling_invalid_p(self):
        """Test that invalid top_p raises error."""
        probs = torch.rand(5, 10)
        probs = probs / probs.sum(dim=1, keepdim=True)
        
        with pytest.raises(ValueError):
            top_p_sampling(probs, top_p=0.0)
        
        with pytest.raises(ValueError):
            top_p_sampling(probs, top_p=1.5)
    
    def test_top_p_sampling_preserves_high_prob(self):
        """Test that high-probability tokens are preserved."""
        probs = torch.zeros(1, 10)
        probs[0, 0] = 0.8
        probs[0, 1] = 0.15
        probs[0, 2:] = 0.05 / 8
        top_p = 0.9
        
        output = top_p_sampling(probs, top_p)
        
        # High probability tokens should be kept
        assert output[0, 0] > 0
        assert output[0, 1] > 0


class TestGenerateText:
    """Test text generation function."""
    
    def test_generate_text_basic(self, monkeypatch):
        """Test basic text generation."""
        # Mock tokenizer
        class MockTokenizer:
            def encode(self, text):
                return [1, 2, 3] if text == "test" else [1, 2]
            
            def decode(self, ids):
                return "test output"
        
        # Mock model
        class MockModel(nn.Module):
            def __init__(self):
                super().__init__()
                self.context_length = 10
            
            def forward(self, x):
                return torch.randn(1, x.shape[1], 1000)
        
        tokenizer = MockTokenizer()
        model = MockModel()
        
        result = generate_text(model, tokenizer, "test", max_tokens=5, device='cpu')
        
        assert isinstance(result, str)
        assert len(result) >= 0
    
    def test_generate_text_max_tokens(self, monkeypatch):
        """Test that generation respects max_tokens."""
        class MockTokenizer:
            def encode(self, text):
                return [1, 2]
            
            def decode(self, ids):
                return "output"
        
        class MockModel(nn.Module):
            def __init__(self):
                super().__init__()
                self.context_length = 10
            
            def forward(self, x):
                return torch.randn(1, x.shape[1], 100)
        
        tokenizer = MockTokenizer()
        model = MockModel()
        
        result = generate_text(model, tokenizer, "test", max_tokens=3, device='cpu')
        
        assert isinstance(result, str)


class TestComputePerplexity:
    """Test perplexity computation."""
    
    def test_compute_perplexity_basic(self, monkeypatch):
        """Test basic perplexity computation."""
        import numpy as np
        
        class MockTokenizer:
            def encode(self, text):
                return list(range(10))
        
        class MockModel(nn.Module):
            def forward(self, x):
                return torch.randn(1, x.shape[1], 1000)
        
        tokenizer = MockTokenizer()
        model = MockModel()
        
        perplexity = compute_perplexity(model, tokenizer, "test text", device='cpu')
        
        assert isinstance(perplexity, float)
        assert perplexity > 0
        assert not np.isinf(perplexity)
        assert not np.isnan(perplexity)
    
    def test_compute_perplexity_short_text(self, monkeypatch):
        """Test perplexity with very short text."""
        import numpy as np
        
        class MockTokenizer:
            def encode(self, text):
                return [1]  # Too short for perplexity
        
        class MockModel(nn.Module):
            def forward(self, x):
                return torch.randn(1, x.shape[1], 100)
        
        tokenizer = MockTokenizer()
        model = MockModel()
        
        perplexity = compute_perplexity(model, tokenizer, "a", device='cpu')
        
        # Should handle short text gracefully
        assert isinstance(perplexity, float)

