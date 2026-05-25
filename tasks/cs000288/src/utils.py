"""
Utility functions for scaling laws assignment.
"""


def estimate_parameters(num_layers: int, d_model: int) -> int:
    """
    Estimate the number of non-embedding parameters for a Transformer model.
    
    Formula: N = 12 * n_layer * d_model^2
    
    Args:
        num_layers: Number of Transformer layers
        d_model: Model embedding dimension
    
    Returns:
        Estimated number of non-embedding parameters
    """
    pass


def compute_dataset_size(compute_budget: float, num_parameters: int) -> float:
    """
    Compute the dataset size (number of tokens) for a given compute budget.
    
    Formula: C = 6 * N * D => D = C / (6 * N)
    
    Args:
        compute_budget: Total compute budget in FLOPs
        num_parameters: Number of model parameters
    
    Returns:
        Dataset size in tokens
    """
    pass
