"""
HMM-based Part-of-Speech Tagger

This module implements a supervised Hidden Markov Model for POS tagging.
It includes:
1. HMM model definition (observations, states, parameters)
2. Learning algorithm with smoothing
3. Viterbi algorithm for inference
"""

import numpy as np
from collections import defaultdict
from typing import List, Tuple, Dict


class HMMPOSTagger:
    """
    Hidden Markov Model for Part-of-Speech Tagging.
    
    Model Definition:
    - Observations: words in the sequence x = (x1, ..., xT)
    - Latent States: POS tags y = (y1, ..., yT)
    - Parameters:
        - A: state transition matrix (tag -> tag)
        - B: emission probability matrix (tag -> word)
        - π: initial state distribution (start -> tag)
    """
    
    def __init__(self, smoothing_lambda: float = 0.01):
        """
        Initialize HMM POS Tagger.
        
        Args:
            smoothing_lambda: Smoothing parameter for emission probabilities
        """
        self.smoothing_lambda = smoothing_lambda
        self.tag_to_idx = {}
        self.word_to_idx = {}
        self.idx_to_tag = {}
        self.idx_to_word = {}
        
        # Model parameters
        self.transition_matrix = None  # A: |tags| x |tags|
        self.emission_matrix = None    # B: |tags| x |vocab|
        self.initial_dist = None       # π: |tags|
        
        self.num_tags = 0
        self.vocab_size = 0
    
    def _build_vocabularies(self, train_data: List[Tuple[List[str], List[str]]]):
        """
        Build word and tag vocabularies from training data.
        
        Args:
            train_data: List of (sentence, tags) tuples
        """
        pass
    
    def train(self, train_data: List[Tuple[List[str], List[str]]]):
        """
        Learn HMM parameters from tagged training sentences.
        
        Uses maximum likelihood estimation with smoothing for emission probabilities.
        
        Args:
            train_data: List of (sentence, tags) tuples
        """
        pass
    
    def viterbi(self, sentence: List[str]) -> Tuple[List[str], float]:
        """
        Viterbi algorithm for finding the most likely sequence of tags.
        
        Solves: y* = arg max_y P_HMM(y | x)
        
        Args:
            sentence: List of words
            
        Returns:
            Tuple of (predicted_tags, log_probability)
        """
        pass
    
    def predict(self, sentences: List[List[str]]) -> List[List[str]]:
        """
        Predict tags for multiple sentences.
        
        Args:
            sentences: List of sentences (each is a list of words)
            
        Returns:
            List of predicted tag sequences
        """
        pass
    
    def compute_log_likelihood(self, data: List[Tuple[List[str], List[str]]], 
                              joint: bool = True) -> float:
        """
        Compute negative log likelihood of the data.
        
        Args:
            data: List of (sentence, tags) tuples
            joint: If True, compute -log P(x, y); if False, compute -log P(x)
            
        Returns:
            Negative log likelihood
        """
        pass
    
    def get_transition_matrix(self) -> np.ndarray:
        """Return the state transition matrix A."""
        pass
    
    def compute_accuracy(self, data: List[Tuple[List[str], List[str]]]) -> float:
        """
        Compute per-word accuracy.
        
        Args:
            data: List of (sentence, tags) tuples
            
        Returns:
            Per-word accuracy (0-1)
        """
        pass
    
    def compute_confusion_matrix(self, data: List[Tuple[List[str], List[str]]]) -> np.ndarray:
        """
        Compute confusion matrix between predicted and true tags.
        
        Args:
            data: List of (sentence, tags) tuples
            
        Returns:
            Confusion matrix of shape (num_tags, num_tags)
        """
        pass
