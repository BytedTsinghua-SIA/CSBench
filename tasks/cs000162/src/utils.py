"""
Utility functions for PGM Homework 2

This module provides helper functions for data loading, visualization, and evaluation.
"""

import numpy as np
import matplotlib.pyplot as plt
from typing import List, Tuple, Dict
import seaborn as sns


def load_pos_data(data_dir: str) -> Tuple[List, List, Dict, List]:
    """
    Load POS tagging data.
    
    Args:
        data_dir: Directory containing data files
        
    Returns:
        Tuple of (train_data, test_data, vocab, tagset)
        where train_data and test_data are lists of (sentence, tags) tuples
    """
    import os
    
    # Load vocabulary
    vocab_file = os.path.join(data_dir, 'vocab.txt')
    with open(vocab_file, 'r') as f:
        vocab = {word.strip(): idx for idx, word in enumerate(f)}
    
    # Load tagset
    tagset_file = os.path.join(data_dir, 'tagset.txt')
    with open(tagset_file, 'r') as f:
        tagset = [tag.strip() for tag in f]
    
    # Load training data
    train_file = os.path.join(data_dir, 'train set.npy')
    train_sentences = np.load(train_file, allow_pickle=True)
    
    # Load test data
    test_file = os.path.join(data_dir, 'test set.npy')
    test_sentences = np.load(test_file, allow_pickle=True)
    
    # Convert to list of (sentence, tags) tuples
    train_data = []
    for sent in train_sentences:
        words = [w[0] for w in sent]
        tags = [w[1] for w in sent]
        train_data.append((words, tags))
    
    test_data = []
    for sent in test_sentences:
        words = [w[0] for w in sent]
        tags = [w[1] for w in sent]
        test_data.append((words, tags))
    
    return train_data, test_data, vocab, tagset


def plot_confusion_matrix(confusion: np.ndarray, tag_names: List[str], 
                          title: str = "Confusion Matrix", save_path: str = None):
    """
    Plot confusion matrix.
    
    Args:
        confusion: Confusion matrix (num_tags x num_tags)
        tag_names: List of tag names
        title: Plot title
        save_path: Path to save figure
    """
    plt.figure(figsize=(12, 10))
    sns.heatmap(confusion, annot=True, fmt='d', cmap='Blues', 
                xticklabels=tag_names, yticklabels=tag_names)
    plt.xlabel('Predicted Tag')
    plt.ylabel('True Tag')
    plt.title(title)
    plt.tight_layout()
    
    if save_path:
        plt.savefig(save_path, dpi=150, bbox_inches='tight')
    plt.close()


def load_premier_league_data(data_path: str) -> np.ndarray:
    """
    Load Premier League data.
    
    Args:
        data_path: Path to data file
        
    Returns:
        380×4 numpy array with columns [y_{g0}, y_{g1}, h(g), a(g)]
    """
    data = np.loadtxt(data_path)
    return data.astype(int)


def print_transition_matrix(A: np.ndarray, tag_names: List[str], 
                           precision: int = 3):
    """
    Print transition matrix in readable format.
    
    Args:
        A: Transition matrix
        tag_names: List of tag names
        precision: Number of decimal places
    """
    print("\nState Transition Matrix A:")
    print("=" * 80)
    
    # Header
    print(f"{'From\\To':<15}", end="")
    for tag in tag_names:
        print(f"{tag[:8]:>10}", end="")
    print()
    print("-" * 80)
    
    # Rows
    for i, tag_from in enumerate(tag_names):
        print(f"{tag_from[:15]:<15}", end="")
        for j in range(len(tag_names)):
            print(f"{A[i, j]:>10.{precision}f}", end="")
        print()
    print()


def evaluate_pos_tagger(tagger, test_data: List[Tuple[List[str], List[str]]], 
                      tag_names: List[str], model_name: str = "Model"):
    """
    Evaluate POS tagger and print results.
    
    Args:
        tagger: Trained POS tagger (HMM or CRF)
        test_data: Test data
        tag_names: List of tag names
        model_name: Name of the model
    """
    print(f"\n{model_name} Evaluation Results:")
    print("=" * 80)
    
    # Compute accuracy
    accuracy = tagger.compute_accuracy(test_data)
    print(f"Per-word Accuracy: {accuracy:.4f}")
    
    # Compute confusion matrix
    confusion = tagger.compute_confusion_matrix(test_data)
    
    # Print confusion matrix summary
    print("\nConfusion Matrix (first 10x10):")
    print(confusion[:10, :10])
    
    return accuracy, confusion

