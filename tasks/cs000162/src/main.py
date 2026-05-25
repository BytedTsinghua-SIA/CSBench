"""
Main script for PGM Homework 2

This script demonstrates the usage of all implemented models:
1. HMM POS Tagger
2. CRF POS Tagger
3. HMM-LDA (Variational Inference)
4. MCMC for Premier League Model
"""

import numpy as np
import argparse
import os
import sys

# Add src directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from hmm_pos_tagger import HMMPOSTagger
from crf_pos_tagger import CRFPOSTagger
from hmm_lda import HMMLDA
from mcmc_premier_league import PremierLeagueMCMC
from utils import (load_pos_data, plot_confusion_matrix, 
                   load_premier_league_data, print_transition_matrix,
                   evaluate_pos_tagger)


def run_hmm_pos_tagger(data_dir: str):
    """Run HMM POS tagging experiments."""
    print("\n" + "="*80)
    print("HMM POS Tagging")
    print("="*80)
    
    # Load data
    print("Loading data...")
    train_data, test_data, vocab, tagset = load_pos_data(data_dir)
    print(f"Training sentences: {len(train_data)}")
    print(f"Test sentences: {len(test_data)}")
    print(f"Vocabulary size: {len(vocab)}")
    print(f"Number of tags: {len(tagset)}")
    
    # Train HMM
    print("\nTraining HMM...")
    hmm = HMMPOSTagger(smoothing_lambda=0.01)
    hmm.train(train_data)
    
    # Print transition matrix
    A = hmm.get_transition_matrix()
    print_transition_matrix(A, tagset, precision=4)
    
    # Compute log likelihood
    train_nll = hmm.compute_log_likelihood(train_data, joint=True)
    test_nll = hmm.compute_log_likelihood(test_data, joint=True)
    print(f"\nNegative Log Likelihood (joint):")
    print(f"  Train: {train_nll:.4f}")
    print(f"  Test: {test_nll:.4f}")
    
    # Evaluate
    accuracy, confusion = evaluate_pos_tagger(hmm, test_data, tagset, "HMM")
    
    # Plot confusion matrix
    plot_confusion_matrix(confusion, tagset, 
                         title="HMM Confusion Matrix",
                         save_path="hmm_confusion_matrix.png")
    
    return hmm


def run_crf_pos_tagger(data_dir: str):
    """Run CRF POS tagging experiments."""
    print("\n" + "="*80)
    print("CRF POS Tagging")
    print("="*80)
    
    # Load data
    print("Loading data...")
    train_data, test_data, vocab, tagset = load_pos_data(data_dir)
    
    # Train CRF
    print("\nTraining CRF...")
    crf = CRFPOSTagger(learning_rate=0.01, l2_reg=0.01)
    crf.train(train_data, num_epochs=10)
    
    # Compute log conditional likelihood
    train_nll = crf.compute_log_likelihood(train_data)
    test_nll = crf.compute_log_likelihood(test_data)
    print(f"\nNegative Log Conditional Likelihood:")
    print(f"  Train: {train_nll:.4f}")
    print(f"  Test: {test_nll:.4f}")
    
    # Evaluate
    accuracy, confusion = evaluate_pos_tagger(crf, test_data, tagset, "CRF")
    
    # Plot confusion matrix
    plot_confusion_matrix(confusion, tagset,
                         title="CRF Confusion Matrix",
                         save_path="crf_confusion_matrix.png")
    
    return crf


def run_hmm_lda(data_path: str):
    """Run HMM-LDA variational EM."""
    print("\n" + "="*80)
    print("HMM-LDA Variational Inference")
    print("="*80)
    
    # Load documents (assuming format: one document per line, space-separated word indices)
    print("Loading documents...")
    documents = []
    word_to_str = {}
    
    with open(data_path, 'r') as f:
        for line in f:
            words = line.strip().split()
            if words:
                doc = [int(w) for w in words]
                documents.append(doc)
    
    print(f"Number of documents: {len(documents)}")
    
    # Train HMM-LDA
    print("\nTraining HMM-LDA...")
    hmm_lda = HMMLDA(num_topics=10, alpha=0.1, gamma=0.1, eta=0.1)
    hmm_lda.fit(documents, max_iterations=50, tolerance=1e-4)
    
    # Print topics
    hmm_lda.print_topics(word_to_str, top_n=10)
    
    return hmm_lda


def run_mcmc_premier_league(data_path: str):
    """Run MCMC for Premier League model."""
    print("\n" + "="*80)
    print("MCMC for Premier League Model")
    print("="*80)
    
    # Load data
    print("Loading data...")
    data = load_premier_league_data(data_path)
    print(f"Data shape: {data.shape}")
    
    # Initialize MCMC
    mcmc = PremierLeagueMCMC(data)
    
    # Run MCMC with different parameter settings
    sigma_values = [0.005, 0.05, 0.5]
    t_values = [1, 5, 20, 50]
    
    results = {}
    
    for sigma in sigma_values:
        for t in t_values:
            print(f"\nRunning MCMC with σ={sigma}, t={t}...")
            samples, acceptance_flags = mcmc.metropolis_hastings(
                sigma=sigma,
                num_burnin=5000,
                num_samples=5000,
                thinning=t,
                start_point=0.1
            )
            
            # Compute rejection ratio
            rejection_ratio = 1 - (np.sum(acceptance_flags) / len(acceptance_flags))
            results[(sigma, t)] = {
                'samples': samples,
                'rejection_ratio': rejection_ratio,
                'acceptance_flags': acceptance_flags
            }
            
            print(f"Rejection ratio: {rejection_ratio:.4f}")
            
            # Plot trace for home variable
            mcmc.plot_trace(samples, param_name='home',
                          save_path=f"trace_sigma_{sigma}_t_{t}.png")
    
    # Print results table
    print("\nRejection Ratios:")
    print("=" * 80)
    print(f"{'σ':<10} {'t':<10} {'Rejection Ratio':<20}")
    print("-" * 80)
    for (sigma, t), result in results.items():
        print(f"{sigma:<10.3f} {t:<10} {result['rejection_ratio']:<20.4f}")
    
    # Find optimal setting (low rejection ratio, good mixing)
    best_setting = min(results.items(), key=lambda x: x[1]['rejection_ratio'])
    best_sigma, best_t = best_setting[0]
    best_samples = best_setting[1]['samples']
    
    print(f"\nOptimal setting: σ={best_sigma}, t={best_t}")
    
    # Plot posterior histogram for home
    mcmc.plot_posterior_histogram(best_samples, param_name='home',
                                  save_path="posterior_histogram_home.png")
    
    # Plot team strengths
    mcmc.plot_team_strengths(best_samples, save_path="team_strengths.png")
    
    # Compute posterior means
    posterior_means = mcmc.compute_posterior_means(best_samples)
    print("\nPosterior Means:")
    print(f"  home: {posterior_means['home']:.4f}")
    print(f"  μ_att: {posterior_means['mu_att']:.4f}")
    print(f"  μ_def: {posterior_means['mu_def']:.4f}")
    
    return mcmc, best_samples


def main():
    """Main function."""
    parser = argparse.ArgumentParser(description='PGM Homework 2')
    parser.add_argument('--task', type=str, choices=['hmm', 'crf', 'hmm_lda', 'mcmc', 'all'],
                       default='all', help='Task to run')
    parser.add_argument('--pos_data_dir', type=str, default='data/pos-data',
                       help='Directory containing POS tagging data')
    parser.add_argument('--lda_data_path', type=str, default='data/wikipedia_corpus.txt',
                       help='Path to LDA corpus file')
    parser.add_argument('--premier_data_path', type=str,
                       default='data/premier_league_2013_2014.dat',
                       help='Path to Premier League data file')
    
    args = parser.parse_args()
    
    if args.task in ['hmm', 'all']:
        if os.path.exists(args.pos_data_dir):
            run_hmm_pos_tagger(args.pos_data_dir)
        else:
            print(f"POS data directory not found: {args.pos_data_dir}")
    
    if args.task in ['crf', 'all']:
        if os.path.exists(args.pos_data_dir):
            run_crf_pos_tagger(args.pos_data_dir)
        else:
            print(f"POS data directory not found: {args.pos_data_dir}")
    
    if args.task in ['hmm_lda', 'all']:
        if os.path.exists(args.lda_data_path):
            run_hmm_lda(args.lda_data_path)
        else:
            print(f"LDA data file not found: {args.lda_data_path}")
    
    if args.task in ['mcmc', 'all']:
        if os.path.exists(args.premier_data_path):
            run_mcmc_premier_league(args.premier_data_path)
        else:
            print(f"Premier League data file not found: {args.premier_data_path}")


if __name__ == '__main__':
    main()

