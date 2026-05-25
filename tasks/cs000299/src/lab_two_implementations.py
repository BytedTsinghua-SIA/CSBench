"""
Lab Two: Flow Matching and Score Matching - Student Implementations

This file contains all the student implementations required for Lab Two.
All comments are in English as required.
"""

import torch
from typing import List
from abc import ABC, abstractmethod


class Alpha(ABC):
    def __init__(self):
        assert torch.allclose(
            self(torch.zeros(1, 1)), torch.zeros(1, 1)
        )
        assert torch.allclose(
            self(torch.ones(1, 1)), torch.ones(1, 1)
        )
    
    @abstractmethod
    def __call__(self, t: torch.Tensor) -> torch.Tensor:
        pass
    
    def dt(self, t: torch.Tensor) -> torch.Tensor:
        from torch.func import vmap, jacrev
        t = t.unsqueeze(1)
        dt = vmap(jacrev(self))(t)
        return dt.view(-1, 1)


class Beta(ABC):
    def __init__(self):
        assert torch.allclose(
            self(torch.zeros(1, 1)), torch.ones(1, 1)
        )
        assert torch.allclose(
            self(torch.ones(1, 1)), torch.zeros(1, 1)
        )
    
    @abstractmethod
    def __call__(self, t: torch.Tensor) -> torch.Tensor:
        pass
    
    def dt(self, t: torch.Tensor) -> torch.Tensor:
        from torch.func import vmap, jacrev
        t = t.unsqueeze(1)
        dt = vmap(jacrev(self))(t)
        return dt.view(-1, 1)


class LinearAlpha(Alpha):
    def __init__(self):
        pass
    
    def __call__(self, t: torch.Tensor) -> torch.Tensor:
        raise NotImplementedError
    
    def dt(self, t: torch.Tensor) -> torch.Tensor:
        raise NotImplementedError


class SquareRootBeta(Beta):
    def __init__(self):
        pass
    
    def __call__(self, t: torch.Tensor) -> torch.Tensor:
        raise NotImplementedError
    
    def dt(self, t: torch.Tensor) -> torch.Tensor:
        raise NotImplementedError


class Sampleable(ABC):
    @property
    @abstractmethod
    def dim(self) -> int:
        pass
    
    @abstractmethod
    def sample(self, num_samples: int) -> torch.Tensor:
        pass


class ConditionalProbabilityPath(torch.nn.Module, ABC):
    def __init__(self, p_simple: Sampleable, p_data: Sampleable):
        super().__init__()
        self.p_simple = p_simple
        self.p_data = p_data
    
    @abstractmethod
    def sample_conditioning_variable(self, num_samples: int) -> torch.Tensor:
        pass
    
    @abstractmethod
    def sample_conditional_path(self, z: torch.Tensor, t: torch.Tensor) -> torch.Tensor:
        pass
    
    @abstractmethod
    def conditional_vector_field(self, x: torch.Tensor, z: torch.Tensor, t: torch.Tensor) -> torch.Tensor:
        pass
    
    @abstractmethod
    def conditional_score(self, x: torch.Tensor, z: torch.Tensor, t: torch.Tensor) -> torch.Tensor:
        pass


class GaussianConditionalProbabilityPath(ConditionalProbabilityPath):
    def __init__(self, p_data: Sampleable, alpha: Alpha, beta: Beta):
        class MockGaussian(Sampleable):
            def __init__(self, dim, std):
                self._dim = dim
                self.std = std
            @property
            def dim(self):
                return self._dim
            def sample(self, num_samples):
                return torch.randn(num_samples, self._dim) * self.std
        
        p_simple = MockGaussian(p_data.dim, 1.0)
        super().__init__(p_simple, p_data)
        self.alpha = alpha
        self.beta = beta

    def sample_conditioning_variable(self, num_samples: int) -> torch.Tensor:
        raise NotImplementedError
    
    def sample_conditional_path(self, z: torch.Tensor, t: torch.Tensor) -> torch.Tensor:
        raise NotImplementedError
        
    def conditional_vector_field(self, x: torch.Tensor, z: torch.Tensor, t: torch.Tensor) -> torch.Tensor:
        raise NotImplementedError

    def conditional_score(self, x: torch.Tensor, z: torch.Tensor, t: torch.Tensor) -> torch.Tensor:
        raise NotImplementedError


class Trainer(ABC):
    def __init__(self, model: torch.nn.Module):
        self.model = model
    
    @abstractmethod
    def get_train_loss(self, **kwargs) -> torch.Tensor:
        pass


class ConditionalFlowMatchingTrainer(Trainer):
    def __init__(self, path: ConditionalProbabilityPath, model: torch.nn.Module, **kwargs):
        super().__init__(model, **kwargs)
        self.path = path

    def get_train_loss(self, batch_size: int) -> torch.Tensor:
        raise NotImplementedError


class ConditionalScoreMatchingTrainer(Trainer):
    def __init__(self, path: ConditionalProbabilityPath, model: torch.nn.Module, **kwargs):
        super().__init__(model, **kwargs)
        self.path = path

    def get_train_loss(self, batch_size: int) -> torch.Tensor:
        raise NotImplementedError


class ScoreFromVectorField(torch.nn.Module):
    def __init__(self, vector_field: torch.nn.Module, alpha: Alpha, beta: Beta):
        super().__init__()
        self.vector_field = vector_field
        self.alpha = alpha
        self.beta = beta

    def forward(self, x: torch.Tensor, t: torch.Tensor) -> torch.Tensor:
        raise NotImplementedError


class LinearConditionalProbabilityPath(ConditionalProbabilityPath):
    def __init__(self, p_simple: Sampleable, p_data: Sampleable):
        super().__init__(p_simple, p_data)

    def sample_conditioning_variable(self, num_samples: int) -> torch.Tensor:
        raise NotImplementedError
    
    def sample_conditional_path(self, z: torch.Tensor, t: torch.Tensor) -> torch.Tensor:
        raise NotImplementedError
        
    def conditional_vector_field(self, x: torch.Tensor, z: torch.Tensor, t: torch.Tensor) -> torch.Tensor:
        raise NotImplementedError

    def conditional_score(self, x: torch.Tensor, z: torch.Tensor, t: torch.Tensor) -> torch.Tensor:
        raise NotImplementedError
