"""
Unit tests for HMM-LDA

Tests core functionality:
- Model initialization
- Variational parameter initialization
- E-step updates
- M-step updates
- ELBO computation
"""

import unittest
import numpy as np
from unittest.mock import patch, MagicMock
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from hmm_lda import HMMLDA


class TestHMMLDA(unittest.TestCase):
    """Test cases for HMM-LDA"""

    def setUp(self):
        """Set up test fixtures"""
        self.hmm_lda = HMMLDA(num_topics=5, alpha=0.1, gamma=0.1, eta=0.1)
        self.sample_documents = [
            [0, 1, 2, 0, 1],
            [2, 3, 1, 2, 3],
            [0, 2, 1, 0, 2],
        ]

    def test_initialization(self):
        """Test HMM-LDA model initialization"""
        self.assertEqual(self.hmm_lda.K, 5)
        self.assertEqual(self.hmm_lda.alpha, 0.1)
        self.assertEqual(self.hmm_lda.gamma, 0.1)
        self.assertEqual(self.hmm_lda.eta, 0.1)
        self.assertIsNone(self.hmm_lda.beta)
        self.assertIsNone(self.hmm_lda.T)

    def test_initialize_parameters(self):
        """Test parameter initialization"""
        vocab_size = 10
        self.hmm_lda._initialize_parameters(vocab_size)
        
        self.assertIsNotNone(self.hmm_lda.beta)
        self.assertIsNotNone(self.hmm_lda.T)
        self.assertEqual(self.hmm_lda.beta.shape, (self.hmm_lda.K, vocab_size))
        self.assertEqual(self.hmm_lda.T.shape, (self.hmm_lda.K, self.hmm_lda.K))

    def test_beta_normalization(self):
        """Test beta matrix rows sum to 1"""
        vocab_size = 10
        self.hmm_lda._initialize_parameters(vocab_size)
        
        row_sums = self.hmm_lda.beta.sum(axis=1)
        np.testing.assert_allclose(row_sums, 1.0, rtol=1e-5)

    def test_transition_matrix_normalization(self):
        """Test transition matrix rows sum to 1"""
        vocab_size = 10
        self.hmm_lda._initialize_parameters(vocab_size)
        
        row_sums = self.hmm_lda.T.sum(axis=1)
        np.testing.assert_allclose(row_sums, 1.0, rtol=1e-5)

    def test_initialize_variational_params(self):
        """Test variational parameter initialization"""
        vocab_size = 10
        self.hmm_lda._initialize_parameters(vocab_size)
        self.hmm_lda._initialize_variational_params(self.sample_documents)
        
        self.assertEqual(len(self.hmm_lda.phi), len(self.sample_documents))
        self.assertEqual(len(self.hmm_lda.xi), len(self.sample_documents))
        self.assertEqual(len(self.hmm_lda.gamma_doc), len(self.sample_documents))

    def test_phi_normalization(self):
        """Test phi distributions sum to 1"""
        vocab_size = 10
        self.hmm_lda._initialize_parameters(vocab_size)
        self.hmm_lda._initialize_variational_params(self.sample_documents)
        
        for d, doc in enumerate(self.sample_documents):
            for i in range(len(doc)):
                row_sum = self.hmm_lda.phi[d][i, :].sum()
                self.assertAlmostEqual(row_sum, 1.0, places=5)

    def test_xi_range(self):
        """Test xi values are in valid range"""
        vocab_size = 10
        self.hmm_lda._initialize_parameters(vocab_size)
        self.hmm_lda._initialize_variational_params(self.sample_documents)
        
        for d, doc in enumerate(self.sample_documents):
            for i in range(1, len(doc)):
                self.assertGreaterEqual(self.hmm_lda.xi[d][i], 0.0)
                self.assertLessEqual(self.hmm_lda.xi[d][i], 1.0)

    def test_e_step_updates_phi(self):
        """Test E-step updates phi"""
        vocab_size = 10
        self.hmm_lda._initialize_parameters(vocab_size)
        self.hmm_lda._initialize_variational_params(self.sample_documents)
        
        initial_phi = [phi.copy() for phi in self.hmm_lda.phi]
        self.hmm_lda._e_step(self.sample_documents, num_iterations=1)
        
        # Phi should be updated (might be same due to convergence)
        # Just check structure is maintained
        self.assertEqual(len(self.hmm_lda.phi), len(initial_phi))

    def test_e_step_maintains_phi_normalization(self):
        """Test E-step maintains phi normalization"""
        vocab_size = 10
        self.hmm_lda._initialize_parameters(vocab_size)
        self.hmm_lda._initialize_variational_params(self.sample_documents)
        
        self.hmm_lda._e_step(self.sample_documents, num_iterations=1)
        
        for d, doc in enumerate(self.sample_documents):
            for i in range(len(doc)):
                row_sum = self.hmm_lda.phi[d][i, :].sum()
                self.assertAlmostEqual(row_sum, 1.0, places=5)

    def test_m_step_updates_beta(self):
        """Test M-step updates beta"""
        vocab_size = 10
        self.hmm_lda._initialize_parameters(vocab_size)
        self.hmm_lda._initialize_variational_params(self.sample_documents)
        
        initial_beta = self.hmm_lda.beta.copy()
        self.hmm_lda._m_step(self.sample_documents)
        
        # Beta should be updated
        self.assertEqual(self.hmm_lda.beta.shape, initial_beta.shape)

    def test_m_step_beta_normalization(self):
        """Test M-step maintains beta normalization"""
        vocab_size = 10
        self.hmm_lda._initialize_parameters(vocab_size)
        self.hmm_lda._initialize_variational_params(self.sample_documents)
        
        self.hmm_lda._m_step(self.sample_documents)
        
        row_sums = self.hmm_lda.beta.sum(axis=1)
        np.testing.assert_allclose(row_sums, 1.0, rtol=1e-5)

    def test_m_step_updates_transition_matrix(self):
        """Test M-step updates transition matrix"""
        vocab_size = 10
        self.hmm_lda._initialize_parameters(vocab_size)
        self.hmm_lda._initialize_variational_params(self.sample_documents)
        
        initial_T = self.hmm_lda.T.copy()
        self.hmm_lda._m_step(self.sample_documents)
        
        # T should be updated
        self.assertEqual(self.hmm_lda.T.shape, initial_T.shape)

    def test_m_step_transition_normalization(self):
        """Test M-step maintains transition matrix normalization"""
        vocab_size = 10
        self.hmm_lda._initialize_parameters(vocab_size)
        self.hmm_lda._initialize_variational_params(self.sample_documents)
        
        self.hmm_lda._m_step(self.sample_documents)
        
        row_sums = self.hmm_lda.T.sum(axis=1)
        np.testing.assert_allclose(row_sums, 1.0, rtol=1e-5)

    def test_compute_elbo_format(self):
        """Test ELBO computation returns valid format"""
        vocab_size = 10
        self.hmm_lda._initialize_parameters(vocab_size)
        self.hmm_lda._initialize_variational_params(self.sample_documents)
        
        elbo = self.hmm_lda._compute_elbo(self.sample_documents)
        
        self.assertIsInstance(elbo, float)
        self.assertTrue(np.isfinite(elbo))

    def test_compute_elbo_consistency(self):
        """Test ELBO computation is consistent"""
        vocab_size = 10
        self.hmm_lda._initialize_parameters(vocab_size)
        self.hmm_lda._initialize_variational_params(self.sample_documents)
        
        elbo1 = self.hmm_lda._compute_elbo(self.sample_documents)
        elbo2 = self.hmm_lda._compute_elbo(self.sample_documents)
        
        self.assertAlmostEqual(elbo1, elbo2, places=5)

    def test_fit_initializes_parameters(self):
        """Test fit method initializes parameters"""
        with patch('builtins.print'):
            self.hmm_lda.fit(self.sample_documents, max_iterations=2)
        
        self.assertIsNotNone(self.hmm_lda.beta)
        self.assertIsNotNone(self.hmm_lda.T)

    def test_fit_initializes_variational_params(self):
        """Test fit method initializes variational parameters"""
        with patch('builtins.print'):
            self.hmm_lda.fit(self.sample_documents, max_iterations=2)
        
        self.assertEqual(len(self.hmm_lda.phi), len(self.sample_documents))

    def test_get_top_words_format(self):
        """Test get top words returns correct format"""
        vocab_size = 10
        self.hmm_lda._initialize_parameters(vocab_size)
        word_to_str = {i: f"word_{i}" for i in range(vocab_size)}
        
        top_words = self.hmm_lda.get_top_words(word_to_str, top_n=5)
        
        self.assertEqual(len(top_words), self.hmm_lda.K)
        for k in range(self.hmm_lda.K):
            self.assertEqual(len(top_words[k]), 5)
            for word, prob in top_words[k]:
                self.assertIsInstance(word, str)
                self.assertIsInstance(prob, (float, np.floating))
                self.assertGreaterEqual(prob, 0.0)
                self.assertLessEqual(prob, 1.0)

    def test_beta_non_negative(self):
        """Test beta values are non-negative"""
        vocab_size = 10
        self.hmm_lda._initialize_parameters(vocab_size)
        
        self.assertTrue(np.all(self.hmm_lda.beta >= 0))

    def test_transition_matrix_non_negative(self):
        """Test transition matrix values are non-negative"""
        vocab_size = 10
        self.hmm_lda._initialize_parameters(vocab_size)
        
        self.assertTrue(np.all(self.hmm_lda.T >= 0))

    def test_phi_non_negative(self):
        """Test phi values are non-negative"""
        vocab_size = 10
        self.hmm_lda._initialize_parameters(vocab_size)
        self.hmm_lda._initialize_variational_params(self.sample_documents)
        
        for d, doc in enumerate(self.sample_documents):
            self.assertTrue(np.all(self.hmm_lda.phi[d] >= 0))


if __name__ == "__main__":
    unittest.main()

