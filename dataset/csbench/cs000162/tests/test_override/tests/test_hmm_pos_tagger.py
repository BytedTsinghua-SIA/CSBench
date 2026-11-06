"""
Unit tests for HMM POS Tagger

Tests core functionality:
- Model initialization
- Vocabulary building
- Parameter learning
- Viterbi inference
- Log likelihood computation
"""

import unittest
import numpy as np
from unittest.mock import patch, MagicMock
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from hmm_pos_tagger import HMMPOSTagger


class TestHMMPOSTagger(unittest.TestCase):
    """Test cases for HMM POS Tagger"""

    def setUp(self):
        """Set up test fixtures"""
        self.hmm = HMMPOSTagger(smoothing_lambda=0.01)
        self.sample_data = [
            (["the", "cat"], ["DET", "NOUN"]),
            (["a", "dog"], ["DET", "NOUN"]),
        ]

    def test_initialization(self):
        """Test HMM model initialization"""
        self.assertEqual(self.hmm.smoothing_lambda, 0.01)
        self.assertIsNone(self.hmm.transition_matrix)
        self.assertIsNone(self.hmm.emission_matrix)
        self.assertEqual(self.hmm.num_tags, 0)

    def test_build_vocabularies(self):
        """Test vocabulary building from training data"""
        self.hmm._build_vocabularies(self.sample_data)
        
        self.assertGreater(len(self.hmm.word_to_idx), 0)
        self.assertGreater(len(self.hmm.tag_to_idx), 0)
        self.assertIn("<UNK>", self.hmm.word_to_idx)
        self.assertEqual(self.hmm.num_tags, len(self.hmm.tag_to_idx))

    def test_vocabulary_consistency(self):
        """Test vocabulary mappings are consistent"""
        self.hmm._build_vocabularies(self.sample_data)
        
        for word, idx in self.hmm.word_to_idx.items():
            self.assertEqual(self.hmm.idx_to_word[idx], word)
        
        for tag, idx in self.hmm.tag_to_idx.items():
            self.assertEqual(self.hmm.idx_to_tag[idx], tag)

    def test_train_basic(self):
        """Test basic training functionality"""
        self.hmm.train(self.sample_data)
        
        self.assertIsNotNone(self.hmm.transition_matrix)
        self.assertIsNotNone(self.hmm.emission_matrix)
        self.assertIsNotNone(self.hmm.initial_dist)
        
        # Check matrix dimensions
        self.assertEqual(self.hmm.transition_matrix.shape[0], self.hmm.num_tags)
        self.assertEqual(self.hmm.transition_matrix.shape[1], self.hmm.num_tags)
        self.assertEqual(self.hmm.emission_matrix.shape[0], self.hmm.num_tags)

    def test_transition_matrix_properties(self):
        """Test transition matrix has correct properties"""
        self.hmm.train(self.sample_data)
        
        # Rows should sum to approximately 1 (or 0 if no transitions observed)
        row_sums = self.hmm.transition_matrix.sum(axis=1)
        # Allow rows to sum to 0 (when tag has no observed transitions) or 1
        for row_sum in row_sums:
            self.assertTrue(np.isclose(row_sum, 0.0, rtol=1e-5) or 
                          np.isclose(row_sum, 1.0, rtol=1e-5))

    def test_emission_matrix_properties(self):
        """Test emission matrix has correct properties"""
        self.hmm.train(self.sample_data)
        
        # Rows should sum to approximately 1
        row_sums = self.hmm.emission_matrix.sum(axis=1)
        np.testing.assert_allclose(row_sums, 1.0, rtol=1e-5)
        
        # All values should be non-negative
        self.assertTrue(np.all(self.hmm.emission_matrix >= 0))

    def test_initial_distribution_properties(self):
        """Test initial distribution has correct properties"""
        self.hmm.train(self.sample_data)
        
        # Should sum to 1
        self.assertAlmostEqual(self.hmm.initial_dist.sum(), 1.0, places=5)
        
        # All values should be non-negative
        self.assertTrue(np.all(self.hmm.initial_dist >= 0))

    def test_viterbi_empty_sentence(self):
        """Test Viterbi with empty sentence"""
        self.hmm.train(self.sample_data)
        tags, log_prob = self.hmm.viterbi([])
        
        self.assertEqual(len(tags), 0)
        self.assertEqual(log_prob, 0.0)

    def test_viterbi_single_word(self):
        """Test Viterbi with single word sentence"""
        self.hmm.train(self.sample_data)
        tags, log_prob = self.hmm.viterbi(["the"])
        
        self.assertEqual(len(tags), 1)
        self.assertIsInstance(log_prob, float)

    def test_viterbi_output_format(self):
        """Test Viterbi output format"""
        self.hmm.train(self.sample_data)
        sentence = ["the", "cat"]
        tags, log_prob = self.hmm.viterbi(sentence)
        
        self.assertEqual(len(tags), len(sentence))
        self.assertIsInstance(log_prob, float)
        self.assertTrue(np.isfinite(log_prob))

    def test_viterbi_tag_validity(self):
        """Test Viterbi returns valid tags"""
        self.hmm.train(self.sample_data)
        sentence = ["a", "dog"]
        tags, _ = self.hmm.viterbi(sentence)
        
        for tag in tags:
            self.assertIn(tag, self.hmm.tag_to_idx)

    def test_predict_multiple_sentences(self):
        """Test prediction for multiple sentences"""
        self.hmm.train(self.sample_data)
        sentences = [["the", "cat"], ["a", "dog"]]
        predictions = self.hmm.predict(sentences)
        
        self.assertEqual(len(predictions), len(sentences))
        for pred, sent in zip(predictions, sentences):
            self.assertEqual(len(pred), len(sent))

    def test_compute_log_likelihood_format(self):
        """Test log likelihood computation returns valid format"""
        self.hmm.train(self.sample_data)
        nll = self.hmm.compute_log_likelihood(self.sample_data, joint=True)
        
        self.assertIsInstance(nll, float)
        self.assertTrue(np.isfinite(nll))
        self.assertGreaterEqual(nll, 0)

    def test_compute_log_likelihood_consistency(self):
        """Test log likelihood is consistent"""
        self.hmm.train(self.sample_data)
        
        nll1 = self.hmm.compute_log_likelihood(self.sample_data, joint=True)
        nll2 = self.hmm.compute_log_likelihood(self.sample_data, joint=True)
        
        self.assertAlmostEqual(nll1, nll2, places=5)

    def test_compute_accuracy_format(self):
        """Test accuracy computation returns valid format"""
        self.hmm.train(self.sample_data)
        accuracy = self.hmm.compute_accuracy(self.sample_data)
        
        self.assertIsInstance(accuracy, float)
        self.assertGreaterEqual(accuracy, 0.0)
        self.assertLessEqual(accuracy, 1.0)

    def test_compute_confusion_matrix_format(self):
        """Test confusion matrix computation"""
        self.hmm.train(self.sample_data)
        confusion = self.hmm.compute_confusion_matrix(self.sample_data)
        
        self.assertEqual(confusion.shape, (self.hmm.num_tags, self.hmm.num_tags))
        self.assertTrue(np.all(confusion >= 0))
        self.assertEqual(confusion.dtype, int)

    def test_smoothing_effect(self):
        """Test that smoothing affects emission probabilities"""
        hmm_no_smooth = HMMPOSTagger(smoothing_lambda=0.0)
        hmm_smooth = HMMPOSTagger(smoothing_lambda=0.1)
        
        hmm_no_smooth.train(self.sample_data)
        hmm_smooth.train(self.sample_data)
        
        # With smoothing, all emission probabilities should be positive
        self.assertTrue(np.all(hmm_smooth.emission_matrix > 0))

    def test_unknown_word_handling(self):
        """Test handling of unknown words"""
        self.hmm.train(self.sample_data)
        
        # Test with word not in training
        unknown_sentence = ["unknown", "word"]
        tags, _ = self.hmm.viterbi(unknown_sentence)
        
        self.assertEqual(len(tags), len(unknown_sentence))
        for tag in tags:
            self.assertIn(tag, self.hmm.tag_to_idx)

    def test_get_transition_matrix(self):
        """Test transition matrix getter"""
        self.hmm.train(self.sample_data)
        A = self.hmm.get_transition_matrix()
        
        self.assertIsInstance(A, np.ndarray)
        self.assertEqual(A.shape, self.hmm.transition_matrix.shape)
        # Should be a copy, not reference
        A[0, 0] = 999
        self.assertNotEqual(A[0, 0], self.hmm.transition_matrix[0, 0])


if __name__ == "__main__":
    unittest.main()

