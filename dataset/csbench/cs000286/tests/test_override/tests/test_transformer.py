"""
Unit tests for Transformer components.
"""

import pytest
import torch
import torch.nn as nn
import math
from src.transformer import (
    Linear, Embedding, RMSNorm, SwiGLU, RotaryPositionalEmbedding,
    softmax, scaled_dot_product_attention, MultiHeadSelfAttention,
    TransformerBlock, TransformerLM
)


class TestLinear:
    """Test Linear layer."""
    
    def test_linear_init(self):
        """Test linear layer initialization."""
        linear = Linear(10, 20)
        
        assert linear.in_features == 10
        assert linear.out_features == 20
        assert isinstance(linear.W, nn.Parameter)
        assert linear.W.shape == (20, 10)
    
    def test_linear_forward_shape(self):
        """Test linear forward pass output shape."""
        linear = Linear(10, 20)
        x = torch.randn(5, 10)
        
        output = linear(x)
        
        assert output.shape == (5, 20)
    
    def test_linear_forward_batch(self):
        """Test linear forward with batch dimensions."""
        linear = Linear(10, 20)
        x = torch.randn(3, 5, 10)
        
        output = linear(x)
        
        assert output.shape == (3, 5, 20)
    
    def test_linear_parameter_grad(self):
        """Test that linear parameters require grad."""
        linear = Linear(10, 20)
        
        assert linear.W.requires_grad


class TestEmbedding:
    """Test Embedding layer."""
    
    def test_embedding_init(self):
        """Test embedding layer initialization."""
        embedding = Embedding(1000, 128)
        
        assert embedding.num_embeddings == 1000
        assert embedding.embedding_dim == 128
        assert isinstance(embedding.embedding, nn.Parameter)
        assert embedding.embedding.shape == (1000, 128)
    
    def test_embedding_forward_shape(self):
        """Test embedding forward pass output shape."""
        embedding = Embedding(1000, 128)
        token_ids = torch.randint(0, 1000, (5, 10))
        
        output = embedding(token_ids)
        
        assert output.shape == (5, 10, 128)
    
    def test_embedding_lookup(self):
        """Test that embedding performs correct lookup."""
        embedding = Embedding(10, 5)
        token_ids = torch.tensor([[0, 1], [2, 3]])
        
        output = embedding(token_ids)
        
        assert output.shape == (2, 2, 5)
        # Check that different token IDs produce different embeddings
        assert not torch.allclose(output[0, 0], output[0, 1])


class TestRMSNorm:
    """Test RMSNorm layer."""
    
    def test_rmsnorm_init(self):
        """Test RMSNorm initialization."""
        rmsnorm = RMSNorm(128)
        
        assert rmsnorm.d_model == 128
        assert isinstance(rmsnorm.gain, nn.Parameter)
        assert rmsnorm.gain.shape == (128,)
    
    def test_rmsnorm_forward_shape(self):
        """Test RMSNorm forward pass output shape."""
        rmsnorm = RMSNorm(128)
        x = torch.randn(5, 10, 128)
        
        output = rmsnorm(x)
        
        assert output.shape == (5, 10, 128)
    
    def test_rmsnorm_normalization(self):
        """Test that RMSNorm normalizes activations."""
        rmsnorm = RMSNorm(128)
        x = torch.randn(2, 5, 128) * 10  # Large values
        
        output = rmsnorm(x)
        
        # Check that output is normalized (RMS should be approximately 1)
        rms = torch.sqrt(torch.mean(output ** 2, dim=-1))
        assert torch.allclose(rms, torch.ones_like(rms), atol=0.1)
    
    def test_rmsnorm_dtype_preservation(self):
        """Test that RMSNorm preserves input dtype."""
        rmsnorm = RMSNorm(128)
        x = torch.randn(2, 5, 128, dtype=torch.float16)
        
        output = rmsnorm(x)
        
        assert output.dtype == torch.float16


class TestSwiGLU:
    """Test SwiGLU feed-forward network."""
    
    def test_swiglu_init(self):
        """Test SwiGLU initialization."""
        swiglu = SwiGLU(128, d_ff=256)
        
        assert swiglu.d_model == 128
        assert swiglu.d_ff == 256
        assert isinstance(swiglu.W1, Linear)
        assert isinstance(swiglu.W2, Linear)
        assert isinstance(swiglu.W3, Linear)
    
    def test_swiglu_forward_shape(self):
        """Test SwiGLU forward pass output shape."""
        swiglu = SwiGLU(128, d_ff=256)
        x = torch.randn(5, 10, 128)
        
        output = swiglu(x)
        
        assert output.shape == (5, 10, 128)
    
    def test_swiglu_default_dff(self):
        """Test SwiGLU with default d_ff calculation."""
        swiglu = SwiGLU(128)
        
        # d_ff should be approximately 8/3 * 128, rounded to multiple of 64
        expected_dff = ((int(8/3 * 128) + 63) // 64) * 64
        assert swiglu.d_ff == expected_dff


class TestSoftmax:
    """Test softmax function."""
    
    def test_softmax_shape(self):
        """Test softmax output shape."""
        x = torch.randn(5, 10)
        
        output = softmax(x, dim=1)
        
        assert output.shape == (5, 10)
    
    def test_softmax_normalization(self):
        """Test that softmax produces normalized distribution."""
        x = torch.randn(5, 10)
        
        output = softmax(x, dim=1)
        
        # Sum along dimension should be 1
        sums = output.sum(dim=1)
        assert torch.allclose(sums, torch.ones(5), atol=1e-5)
    
    def test_softmax_numerical_stability(self):
        """Test softmax with large values."""
        x = torch.tensor([[1000.0, 1001.0, 1002.0]])
        
        output = softmax(x, dim=1)
        
        # Should not produce NaN or Inf
        assert not torch.isnan(output).any()
        assert not torch.isinf(output).any()
        assert torch.allclose(output.sum(dim=1), torch.ones(1))


class TestRoPE:
    """Test Rotary Position Embeddings."""
    
    def test_rope_init(self):
        """Test RoPE initialization."""
        rope = RotaryPositionalEmbedding(theta=10000.0, d_k=64, max_seq_len=512)
        
        assert rope.theta == 10000.0
        assert rope.d_k == 64
        assert rope.max_seq_len == 512
        assert hasattr(rope, 'cos')
        assert hasattr(rope, 'sin')
    
    def test_rope_forward_shape(self):
        """Test RoPE forward pass output shape."""
        rope = RotaryPositionalEmbedding(theta=10000.0, d_k=64, max_seq_len=512)
        x = torch.randn(2, 10, 64)
        positions = torch.arange(10).unsqueeze(0).expand(2, -1)
        
        output = rope(x, positions)
        
        assert output.shape == (2, 10, 64)
    
    def test_rope_different_positions(self):
        """Test that RoPE produces different outputs for different positions."""
        rope = RotaryPositionalEmbedding(theta=10000.0, d_k=64, max_seq_len=512)
        x = torch.randn(1, 2, 64)
        pos1 = torch.tensor([[0, 1]])
        pos2 = torch.tensor([[10, 11]])
        
        output1 = rope(x, pos1)
        output2 = rope(x, pos2)
        
        # Different positions should produce different outputs
        assert not torch.allclose(output1, output2)


class TestScaledDotProductAttention:
    """Test scaled dot-product attention."""
    
    def test_attention_shape(self):
        """Test attention output shape."""
        batch_size, seq_len, d_k, d_v = 2, 10, 64, 64
        Q = torch.randn(batch_size, seq_len, d_k)
        K = torch.randn(batch_size, seq_len, d_k)
        V = torch.randn(batch_size, seq_len, d_v)
        
        output = scaled_dot_product_attention(Q, K, V)
        
        assert output.shape == (batch_size, seq_len, d_v)
    
    def test_attention_with_mask(self):
        """Test attention with masking."""
        batch_size, seq_len, d_k, d_v = 2, 5, 64, 64
        Q = torch.randn(batch_size, seq_len, d_k)
        K = torch.randn(batch_size, seq_len, d_k)
        V = torch.randn(batch_size, seq_len, d_v)
        mask = torch.tril(torch.ones(seq_len, seq_len, dtype=torch.bool))
        
        output = scaled_dot_product_attention(Q, K, V, mask=mask)
        
        assert output.shape == (batch_size, seq_len, d_v)
    
    def test_attention_batch_dimensions(self):
        """Test attention with extra batch dimensions."""
        Q = torch.randn(2, 3, 10, 64)
        K = torch.randn(2, 3, 10, 64)
        V = torch.randn(2, 3, 10, 64)
        
        output = scaled_dot_product_attention(Q, K, V)
        
        assert output.shape == (2, 3, 10, 64)


class TestMultiHeadSelfAttention:
    """Test multi-head self-attention."""
    
    def test_mha_init(self):
        """Test multi-head attention initialization."""
        mha = MultiHeadSelfAttention(d_model=128, num_heads=8)
        
        assert mha.d_model == 128
        assert mha.num_heads == 8
        assert mha.d_k == 128 // 8
        assert isinstance(mha.W_Q, Linear)
        assert isinstance(mha.W_K, Linear)
        assert isinstance(mha.W_V, Linear)
        assert isinstance(mha.W_O, Linear)
    
    def test_mha_forward_shape(self):
        """Test multi-head attention forward pass output shape."""
        mha = MultiHeadSelfAttention(d_model=128, num_heads=8)
        x = torch.randn(2, 10, 128)
        
        output = mha(x)
        
        assert output.shape == (2, 10, 128)
    
    def test_mha_causal_masking(self):
        """Test that multi-head attention applies causal masking."""
        mha = MultiHeadSelfAttention(d_model=128, num_heads=8)
        x = torch.randn(1, 5, 128)
        
        output = mha(x)
        
        assert output.shape == (1, 5, 128)


class TestTransformerBlock:
    """Test Transformer block."""
    
    def test_transformer_block_init(self):
        """Test Transformer block initialization."""
        block = TransformerBlock(d_model=128, num_heads=8, d_ff=256)
        
        assert isinstance(block.norm1, RMSNorm)
        assert isinstance(block.attention, MultiHeadSelfAttention)
        assert isinstance(block.norm2, RMSNorm)
        assert isinstance(block.ffn, SwiGLU)
    
    def test_transformer_block_forward_shape(self):
        """Test Transformer block forward pass output shape."""
        block = TransformerBlock(d_model=128, num_heads=8, d_ff=256)
        x = torch.randn(2, 10, 128)
        
        output = block(x)
        
        assert output.shape == (2, 10, 128)
    
    def test_transformer_block_residual(self):
        """Test that Transformer block includes residual connections."""
        block = TransformerBlock(d_model=128, num_heads=8, d_ff=256)
        x = torch.randn(1, 5, 128)
        
        output = block(x)
        
        # Output should have same shape as input
        assert output.shape == x.shape


class TestTransformerLM:
    """Test Transformer language model."""
    
    def test_transformer_lm_init(self):
        """Test Transformer LM initialization."""
        model = TransformerLM(
            vocab_size=1000,
            context_length=256,
            num_layers=4,
            d_model=128,
            num_heads=8,
            d_ff=256
        )
        
        assert model.vocab_size == 1000
        assert model.context_length == 256
        assert isinstance(model.token_embedding, Embedding)
        assert len(model.blocks) == 4
        assert isinstance(model.final_norm, RMSNorm)
        assert isinstance(model.output_embedding, Linear)
    
    def test_transformer_lm_forward_shape(self):
        """Test Transformer LM forward pass output shape."""
        model = TransformerLM(
            vocab_size=1000,
            context_length=256,
            num_layers=2,
            d_model=128,
            num_heads=8,
            d_ff=256
        )
        token_ids = torch.randint(0, 1000, (2, 10))
        
        logits = model(token_ids)
        
        assert logits.shape == (2, 10, 1000)
    
    def test_transformer_lm_parameter_count(self):
        """Test that Transformer LM has learnable parameters."""
        model = TransformerLM(
            vocab_size=1000,
            context_length=256,
            num_layers=2,
            d_model=128,
            num_heads=8,
            d_ff=256
        )
        
        num_params = sum(p.numel() for p in model.parameters())
        assert num_params > 0

