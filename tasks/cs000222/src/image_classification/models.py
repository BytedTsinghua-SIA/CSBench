"""
Model definitions for image classification project.
Supports training from scratch, feature extraction, and fine-tuning.
"""

import torch
import torch.nn as nn
import torchvision.models as models
from typing import Optional, List, Tuple


def get_model(model_name: str, num_classes: int, pretrained: bool = True,
              freeze_backbone: bool = False) -> nn.Module:
    """
    Get a classification model from torchvision.
    
    Args:
        model_name: Name of the model (e.g., 'resnet18', 'resnet50', 'regnet_y_400mf')
        num_classes: Number of output classes
        pretrained: Whether to use pretrained ImageNet weights
        freeze_backbone: Whether to freeze backbone layers (for feature extraction)
    
    Returns:
        PyTorch model
    """
    pass


def extract_features(model: nn.Module, dataloader: torch.utils.data.DataLoader,
                     device: torch.device) -> Tuple[torch.Tensor, torch.Tensor]:
    """
    Extract features from a model for feature extraction training approach.
    
    Args:
        model: PyTorch model (backbone should be frozen)
        dataloader: DataLoader for the dataset
        device: Device to run on
    
    Returns:
        Tuple of (features, labels) tensors
    """
    pass


class LinearClassifier(nn.Module):
    """
    Simple linear classifier for feature extraction approach.
    """
    
    def __init__(self, input_dim: int, num_classes: int):
        super(LinearClassifier, self).__init__()
        pass
    
    def forward(self, x):
        pass
