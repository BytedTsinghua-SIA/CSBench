"""
Unit tests for U-Net components
"""
import pytest
import torch
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from lab_three import (
    FourierEncoder,
    ResidualLayer,
    Encoder,
    Decoder,
    Midcoder,
    MNISTUNet
)


class TestFourierEncoder:
    """Test cases for FourierEncoder"""
    
    def test_initialization(self):
        """Test FourierEncoder initialization"""
        encoder = FourierEncoder(dim=40)
        
        assert encoder.half_dim == 20
        assert encoder.weights.shape == (1, 20)
    
    def test_initialization_odd_dim_raises_error(self):
        """Test that odd dimension raises assertion error"""
        with pytest.raises(AssertionError):
            FourierEncoder(dim=41)
    
    def test_forward_output_shape(self):
        """Test forward output shape with different batch sizes"""
        encoder = FourierEncoder(dim=40)
        
        for bs in [1, 4, 8]:
            t = torch.rand(bs, 1, 1, 1)
            output = encoder(t)
            assert output.shape == (bs, 40)
            # Values should be bounded (sin/cos are in [-1, 1] * sqrt(2))
            assert torch.all(torch.abs(output) <= 2.0)


class TestResidualLayer:
    """Test cases for ResidualLayer"""
    
    def test_initialization(self):
        """Test ResidualLayer initialization"""
        layer = ResidualLayer(channels=32, time_embed_dim=40, y_embed_dim=40)
        
        assert layer.block1 is not None
        assert layer.block2 is not None
        assert layer.time_adapter is not None
        assert layer.y_adapter is not None
    
    def test_forward_preserves_shape(self):
        """Test that forward preserves input shape"""
        layer = ResidualLayer(channels=32, time_embed_dim=40, y_embed_dim=40)
        
        shapes = [(4, 32, 16, 16), (2, 32, 8, 8)]
        for shape in shapes:
            x = torch.randn(*shape)
            t_embed = torch.randn(shape[0], 40)
            y_embed = torch.randn(shape[0], 40)
            
            output = layer(x, t_embed, y_embed)
            assert output.shape == shape


class TestEncoder:
    """Test cases for Encoder"""
    
    def test_initialization(self):
        """Test Encoder initialization"""
        encoder = Encoder(
            channels_in=32,
            channels_out=64,
            num_residual_layers=2,
            t_embed_dim=40,
            y_embed_dim=40
        )
        
        assert len(encoder.res_blocks) == 2
        assert encoder.downsample is not None
    
    def test_forward_downsample_and_channel_increase(self):
        """Test that encoder downsamples spatial dimensions and increases channels"""
        encoder = Encoder(
            channels_in=32,
            channels_out=64,
            num_residual_layers=2,
            t_embed_dim=40,
            y_embed_dim=40
        )
        
        x = torch.randn(4, 32, 32, 32)
        t_embed = torch.randn(4, 40)
        y_embed = torch.randn(4, 40)
        
        output = encoder(x, t_embed, y_embed)
        
        assert output.shape == (4, 64, 16, 16)


class TestDecoder:
    """Test cases for Decoder"""
    
    def test_initialization(self):
        """Test Decoder initialization"""
        decoder = Decoder(
            channels_in=64,
            channels_out=32,
            num_residual_layers=2,
            t_embed_dim=40,
            y_embed_dim=40
        )
        
        assert len(decoder.res_blocks) == 2
        assert decoder.upsample is not None
    
    def test_forward_upsample_and_channel_decrease(self):
        """Test that decoder upsamples spatial dimensions and decreases channels"""
        decoder = Decoder(
            channels_in=64,
            channels_out=32,
            num_residual_layers=2,
            t_embed_dim=40,
            y_embed_dim=40
        )
        
        x = torch.randn(4, 64, 8, 8)
        t_embed = torch.randn(4, 40)
        y_embed = torch.randn(4, 40)
        
        output = decoder(x, t_embed, y_embed)
        
        assert output.shape == (4, 32, 16, 16)


class TestMidcoder:
    """Test cases for Midcoder"""
    
    def test_initialization(self):
        """Test Midcoder initialization"""
        midcoder = Midcoder(
            channels=128,
            num_residual_layers=2,
            t_embed_dim=40,
            y_embed_dim=40
        )
        
        assert len(midcoder.res_blocks) == 2
    
    def test_forward_preserves_shape(self):
        """Test that midcoder preserves shape"""
        midcoder = Midcoder(
            channels=128,
            num_residual_layers=2,
            t_embed_dim=40,
            y_embed_dim=40
        )
        
        x = torch.randn(4, 128, 8, 8)
        t_embed = torch.randn(4, 40)
        y_embed = torch.randn(4, 40)
        
        output = midcoder(x, t_embed, y_embed)
        
        assert output.shape == (4, 128, 8, 8)


class TestMNISTUNet:
    """Test cases for MNISTUNet"""
    
    def test_initialization(self):
        """Test MNISTUNet initialization"""
        unet = MNISTUNet(
            channels=[32, 64, 128],
            num_residual_layers=2,
            t_embed_dim=40,
            y_embed_dim=40
        )
        
        assert unet.init_conv is not None
        assert unet.time_embedder is not None
        assert unet.y_embedder is not None
        assert len(unet.encoders) == 2
        assert len(unet.decoders) == 2
        assert unet.midcoder is not None
        assert unet.final_conv is not None
    
    def test_forward_output_shape(self):
        """Test forward output shape with different batch sizes and labels"""
        unet = MNISTUNet(
            channels=[32, 64, 128],
            num_residual_layers=2,
            t_embed_dim=40,
            y_embed_dim=40
        )
        
        # Test with different batch sizes
        for bs in [1, 4]:
            x = torch.randn(bs, 1, 32, 32)
            t = torch.rand(bs, 1, 1, 1)
            y = torch.randint(0, 11, (bs,))
            
            output = unet(x, t, y)
            assert output.shape == (bs, 1, 32, 32)
        
        # Test with null label
        x = torch.randn(4, 1, 32, 32)
        t = torch.rand(4, 1, 1, 1)
        y = torch.ones(4, dtype=torch.long) * 10
        output = unet(x, t, y)
        assert output.shape == (4, 1, 32, 32)

