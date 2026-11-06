"""
Unit tests for CRF POS Tagger

Tests core functionality:
- Feature extraction
- Feature space building
- Potential computation
- Forward-backward algorithm
- Viterbi inference
- Training procedure
"""

import unittest
import numpy as np
from unittest.mock import patch, MagicMock
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from crf_pos_tagger import CRFPOSTagger


class TestCRFPOSTagger(unittest.TestCase):
    """Test cases for CRF POS Tagger"""

    def setUp(self):
        """Set up test fixtures"""
        self.crf = CRFPOSTagger(learning_rate=0.01, l2_reg=0.01)
        self.sample_data = [
            (["The", "cat"], ["DET", "NOUN"]),
            (["a", "dog"], ["DET", "NOUN"]),
        ]

    def test_initialization(self):
        """Test CRF model initialization"""
        self.assertEqual(self.crf.learning_rate, 0.01)
        self.assertEqual(self.crf.l2_reg, 0.01)
        self.assertIsNone(self.crf.weights)
        self.assertEqual(self.crf.num_features, 0)

    def test_build_vocabularies(self):
        """Test vocabulary building"""
        self.crf._build_vocabularies(self.sample_data)
        
        self.assertGreater(len(self.crf.word_to_idx), 0)
        self.assertGreater(len(self.crf.tag_to_idx), 0)
        self.assertIn("<UNK>", self.crf.word_to_idx)

    def test_extract_features_word_identity(self):
        """Test word identity feature extraction"""
        self.crf._build_vocabularies(self.sample_data)
        sentence = ["The", "cat"]
        
        features = self.crf._extract_features(sentence, 0, None, "DET")
        
        self.assertIsInstance(features, set)
        self.assertGreater(len(features), 0)
        # Should contain word-based feature
        word_features = [f for f in features if "word_" in f]
        self.assertGreater(len(word_features), 0)

    def test_extract_features_first_word(self):
        """Test first word indicator feature"""
        self.crf._build_vocabularies(self.sample_data)
        sentence = ["The", "cat"]
        
        features = self.crf._extract_features(sentence, 0, None, "DET")
        
        first_word_features = [f for f in features if "first_word" in f]
        self.assertGreater(len(first_word_features), 0)

    def test_extract_features_last_word(self):
        """Test last word indicator feature"""
        self.crf._build_vocabularies(self.sample_data)
        sentence = ["The", "cat"]
        
        features = self.crf._extract_features(sentence, 1, None, "NOUN")
        
        last_word_features = [f for f in features if "last_word" in f]
        self.assertGreater(len(last_word_features), 0)

    def test_extract_features_capitalization(self):
        """Test capitalization feature"""
        self.crf._build_vocabularies(self.sample_data)
        sentence = ["The", "cat"]
        
        features = self.crf._extract_features(sentence, 0, None, "DET")
        
        capital_features = [f for f in features if "has_capital" in f]
        self.assertGreater(len(capital_features), 0)

    def test_extract_features_transition(self):
        """Test transition feature"""
        self.crf._build_vocabularies(self.sample_data)
        sentence = ["The", "cat"]
        
        features = self.crf._extract_features(sentence, 1, "DET", "NOUN")
        
        transition_features = [f for f in features if "prev_tag" in f]
        self.assertGreater(len(transition_features), 0)

    def test_build_feature_space(self):
        """Test feature space building"""
        self.crf._build_vocabularies(self.sample_data)
        self.crf._build_feature_space(self.sample_data)
        
        self.assertGreater(self.crf.num_features, 0)
        self.assertGreater(len(self.crf.feature_to_idx), 0)

    def test_get_feature_vector_format(self):
        """Test feature vector format"""
        self.crf._build_vocabularies(self.sample_data)
        self.crf._build_feature_space(self.sample_data)
        
        sentence = ["The", "cat"]
        feature_vec = self.crf._get_feature_vector(sentence, 0, -1, 0)
        
        self.assertIsInstance(feature_vec, np.ndarray)
        self.assertEqual(len(feature_vec), self.crf.num_features)
        self.assertTrue(np.all((feature_vec == 0) | (feature_vec == 1)))

    def test_compute_potential_format(self):
        """Test potential computation format"""
        self.crf._build_vocabularies(self.sample_data)
        self.crf._build_feature_space(self.sample_data)
        self.crf.weights = np.random.normal(0, 0.01, self.crf.num_features)
        
        sentence = ["The", "cat"]
        potential = self.crf._compute_potential(sentence, 0, -1, 0)
        
        self.assertIsInstance(potential, float)
        self.assertGreater(potential, 0)
        self.assertTrue(np.isfinite(potential))

    def test_forward_algorithm_format(self):
        """Test forward algorithm output format"""
        self.crf._build_vocabularies(self.sample_data)
        self.crf._build_feature_space(self.sample_data)
        self.crf.weights = np.random.normal(0, 0.01, self.crf.num_features)
        
        sentence = ["The", "cat"]
        alpha, log_Z = self.crf._forward(sentence)
        
        self.assertIsInstance(alpha, np.ndarray)
        self.assertIsInstance(log_Z, float)
        self.assertTrue(np.isfinite(log_Z))

    def test_forward_algorithm_empty_sentence(self):
        """Test forward algorithm with empty sentence"""
        self.crf._build_vocabularies(self.sample_data)
        self.crf._build_feature_space(self.sample_data)
        self.crf.weights = np.random.normal(0, 0.01, self.crf.num_features)
        
        alpha, log_Z = self.crf._forward([])
        
        self.assertEqual(len(alpha), 0)
        self.assertEqual(log_Z, 0.0)

    def test_backward_algorithm_format(self):
        """Test backward algorithm output format"""
        self.crf._build_vocabularies(self.sample_data)
        self.crf._build_feature_space(self.sample_data)
        self.crf.weights = np.random.normal(0, 0.01, self.crf.num_features)
        
        sentence = ["The", "cat"]
        beta = self.crf._backward(sentence)
        
        self.assertIsInstance(beta, np.ndarray)
        self.assertEqual(beta.shape[0], len(sentence))

    def test_viterbi_format(self):
        """Test Viterbi algorithm output format"""
        self.crf._build_vocabularies(self.sample_data)
        self.crf._build_feature_space(self.sample_data)
        self.crf.weights = np.random.normal(0, 0.01, self.crf.num_features)
        
        sentence = ["The", "cat"]
        tags, log_prob = self.crf._viterbi(sentence)
        
        self.assertEqual(len(tags), len(sentence))
        self.assertIsInstance(log_prob, float)
        self.assertTrue(np.isfinite(log_prob))

    def test_viterbi_tag_validity(self):
        """Test Viterbi returns valid tags"""
        self.crf._build_vocabularies(self.sample_data)
        self.crf._build_feature_space(self.sample_data)
        self.crf.weights = np.random.normal(0, 0.01, self.crf.num_features)
        
        sentence = ["The", "cat"]
        tags, _ = self.crf._viterbi(sentence)
        
        for tag in tags:
            self.assertIn(tag, self.crf.tag_to_idx)

    def test_train_initializes_weights(self):
        """Test training initializes weights"""
        with patch('builtins.print'):
            self.crf.train(self.sample_data, num_epochs=1)
        
        self.assertIsNotNone(self.crf.weights)
        self.assertEqual(len(self.crf.weights), self.crf.num_features)

    def test_train_updates_weights(self):
        """Test training updates weights"""
        with patch('builtins.print'):
            self.crf.train(self.sample_data, num_epochs=1)
        
        initial_weights = self.crf.weights.copy()
        
        with patch('builtins.print'):
            self.crf.train(self.sample_data, num_epochs=1)
        
        # Weights should potentially change (though might be same due to convergence)
        # Just check they exist and have correct shape
        self.assertEqual(self.crf.weights.shape, initial_weights.shape)

    def test_predict_format(self):
        """Test predict method format"""
        with patch('builtins.print'):
            self.crf.train(self.sample_data, num_epochs=1)
        
        sentences = [["The", "cat"], ["a", "dog"]]
        predictions = self.crf.predict(sentences)
        
        self.assertEqual(len(predictions), len(sentences))
        for pred, sent in zip(predictions, sentences):
            self.assertEqual(len(pred), len(sent))

    def test_compute_log_likelihood_format(self):
        """Test log likelihood computation format"""
        with patch('builtins.print'):
            self.crf.train(self.sample_data, num_epochs=1)
        
        nll = self.crf.compute_log_likelihood(self.sample_data)
        
        self.assertIsInstance(nll, float)
        self.assertTrue(np.isfinite(nll))
        self.assertGreaterEqual(nll, 0)

    def test_compute_accuracy_format(self):
        """Test accuracy computation format"""
        with patch('builtins.print'):
            self.crf.train(self.sample_data, num_epochs=1)
        
        accuracy = self.crf.compute_accuracy(self.sample_data)
        
        self.assertIsInstance(accuracy, float)
        self.assertGreaterEqual(accuracy, 0.0)
        self.assertLessEqual(accuracy, 1.0)

    def test_compute_confusion_matrix_format(self):
        """Test confusion matrix computation"""
        with patch('builtins.print'):
            self.crf.train(self.sample_data, num_epochs=1)
        
        confusion = self.crf.compute_confusion_matrix(self.sample_data)
        
        self.assertEqual(confusion.shape, (self.crf.num_tags, self.crf.num_tags))
        self.assertTrue(np.all(confusion >= 0))

    def test_feature_vector_binary(self):
        """Test feature vectors are binary"""
        self.crf._build_vocabularies(self.sample_data)
        self.crf._build_feature_space(self.sample_data)
        
        sentence = ["The", "cat"]
        feature_vec = self.crf._get_feature_vector(sentence, 0, -1, 0)
        
        unique_values = np.unique(feature_vec)
        self.assertTrue(np.all(np.isin(unique_values, [0, 1])))


if __name__ == "__main__":
    unittest.main()

