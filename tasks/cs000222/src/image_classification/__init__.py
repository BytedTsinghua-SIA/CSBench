"""
Image classification project module.
"""

from .dataset import CustomImageDataset, split_dataset, get_data_loaders
from .models import get_model, extract_features, LinearClassifier
from .train import Trainer, train_multiple_models
from .analysis import (compute_confusion_matrix, plot_confusion_matrix,
                      compute_saliency_map, GradCAM, visualize_predictions)

__all__ = [
    'CustomImageDataset',
    'split_dataset',
    'get_data_loaders',
    'get_model',
    'extract_features',
    'LinearClassifier',
    'Trainer',
    'train_multiple_models',
    'compute_confusion_matrix',
    'plot_confusion_matrix',
    'compute_saliency_map',
    'GradCAM',
    'visualize_predictions',
]

