"""
Metropolis-Hastings MCMC for Premier League Bayesian Hierarchical Model

This module implements Metropolis-Hastings algorithm for posterior inference
in a Bayesian hierarchical model predicting Premier League goal scores.

Model:
- Goals: y_{gj} | θ_{gj} ~ Poisson(θ_{gj})
- Log-linear intensities:
  - log θ_{g0} = home + att_{h(g)} - def_{a(g)}
  - log θ_{g1} = att_{a(g)} - def_{h(g)}
- Priors:
  - home ~ N(0, τ₀⁻¹), τ₀ = 0.0001
  - att_t ~ N(μ_{att}, τ_{att}⁻¹)
  - def_t ~ N(μ_{def}, τ_{def}⁻¹)
  - μ_{att} ~ N(0, τ₁⁻¹), μ_{def} ~ N(0, τ₁⁻¹), τ₁ = 0.0001
  - τ_{att} ~ Gamma(α, β), τ_{def} ~ Gamma(α, β), α = β = 0.1
- Constraint: att₀ = def₀ = 0 (identifiability)
"""

import numpy as np
import matplotlib.pyplot as plt
from typing import Tuple, List, Dict
from scipy.stats import poisson, norm, gamma


class PremierLeagueMCMC:
    """
    Metropolis-Hastings MCMC for Premier League model.
    
    Parameters to infer:
    - home: home team advantage
    - att_t: attacking strength for team t (t=0..19, att₀=0)
    - def_t: defending strength for team t (t=0..19, def₀=0)
    - μ_{att}, μ_{def}: hyperparameters for attack/defense means
    - τ_{att}, τ_{def}: hyperparameters for attack/defense precisions
    """
    
    def __init__(self, data: np.ndarray):
        """
        Initialize MCMC sampler.
        
        Args:
            data: 380×4 matrix with columns [y_{g0}, y_{g1}, h(g), a(g)]
        """
        self.data = data
        self.num_games = data.shape[0]
        self.num_teams = 20
        
        # Hyperparameters
        self.tau0 = 0.0001  # Precision for home
        self.tau1 = 0.0001  # Precision for μ_{att}, μ_{def}
        self.alpha = 0.1    # Gamma shape for τ_{att}, τ_{def}
        self.beta = 0.1     # Gamma rate for τ_{att}, τ_{def}
        
        # Parameter dimensions
        # Total: 1 (home) + 19 (att, excluding team 0) + 19 (def, excluding team 0)
        #        + 2 (μ_{att}, μ_{def}) + 2 (τ_{att}, τ_{def}) = 43
        self.param_dim = 1 + 19 + 19 + 2 + 2
        
        # Team names mapping (for visualization)
        self.team_names = [
            "Arsenal", "Aston Villa", "Cardiff City", "Chelsea", "Crystal Palace",
            "Everton", "Fulham", "Hull City", "Liverpool", "Manchester City",
            "Manchester United", "Newcastle United", "Norwich City", "Southampton", "Stoke City",
            "Sunderland", "Swansea City", "Tottenham Hotspurs", 
            "West Bromwich Albion", "West Ham United"
        ]
    
    def _unpack_params(self, params: np.ndarray) -> Dict:
        """
        Unpack parameter vector into named components.
        
        Args:
            params: Parameter vector of length 43
            
        Returns:
            Dictionary with parameter components
        """
        pass
    
    def _pack_params(self, param_dict: Dict) -> np.ndarray:
        """Pack parameter dictionary into vector."""
        pass
    
    def _compute_log_likelihood(self, params: np.ndarray) -> float:
        """
        Compute log joint likelihood: log p(y, θ, η)
        
        Args:
            params: Parameter vector
            
        Returns:
            Log joint likelihood
        """
        pass
    
    def metropolis_hastings(self, sigma: float, num_burnin: int, 
                          num_samples: int, thinning: int, 
                          start_point: float = 0.1) -> Tuple[np.ndarray, List[bool]]:
        """
        Run Metropolis-Hastings algorithm.
        
        Args:
            sigma: Standard deviation for isotropic Gaussian proposal
            num_burnin: Number of burn-in steps
            num_samples: Number of samples to collect
            thinning: Thinning parameter (collect every t-th sample)
            start_point: Starting point for all parameters
            
        Returns:
            Tuple of (samples, acceptance_flags)
        """
        pass
    
    def plot_trace(self, samples: np.ndarray, param_name: str = 'home', 
                   save_path: str = None):
        """
        Plot trace plot for a parameter.
        
        Args:
            samples: MCMC samples (collected after burn-in)
            param_name: Name of parameter to plot ('home', 'att', 'def', etc.)
            save_path: Path to save figure
        """
        pass
    
    def plot_posterior_histogram(self, samples: np.ndarray, param_name: str = 'home',
                                 save_path: str = None):
        """Plot posterior histogram for a parameter."""
        pass
    
    def plot_team_strengths(self, samples: np.ndarray, save_path: str = None):
        """
        Plot attacking vs defending strength for each team.
        
        Args:
            samples: MCMC samples
            save_path: Path to save figure
        """
        pass
    
    def compute_posterior_means(self, samples: np.ndarray) -> Dict:
        """
        Compute posterior means for all parameters.
        
        Returns:
            Dictionary with posterior means
        """
        pass
