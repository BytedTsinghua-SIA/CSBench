"""
Helper functions for tests
"""

import sys
import os
from unittest.mock import MagicMock, patch


def setup_test_imports():
    """Setup imports for testing"""
    # Add src directory to path (tests is now inside src)
    src_path = os.path.dirname(os.path.dirname(__file__))  # Go up from tests to src
    parent_path = os.path.dirname(src_path)  # Go up from src to project root
    sys.path.insert(0, src_path)
    sys.path.insert(0, parent_path)

    # Create comprehensive mock modules with all necessary attributes
    mock_torch = MagicMock()
    mock_torch.device = MagicMock()
    mock_torch.bfloat16 = MagicMock()
    mock_torch.float16 = MagicMock()
    mock_torch.float32 = MagicMock()

    mock_tqdm = MagicMock()
    mock_tqdm_class = MagicMock()
    mock_tqdm_class.return_value = mock_tqdm

    mock_datasets = MagicMock()
    mock_dataset_class = MagicMock()
    mock_datasets.Dataset = mock_dataset_class

    mock_trl = MagicMock()
    mock_trl.SFTConfig = MagicMock()
    mock_trl.SFTTrainer = MagicMock()

    mock_transformers = MagicMock()
    mock_transformers.AutoModelForCausalLM = MagicMock()
    mock_transformers.AutoTokenizer = MagicMock()
    mock_transformers.BitsAndBytesConfig = MagicMock()
    mock_transformers.pipeline = MagicMock()

    mock_peft = MagicMock()
    mock_peft.LoraConfig = MagicMock()
    mock_peft.get_peft_model = MagicMock()
    mock_peft.PeftModel = MagicMock()

    # Mock external dependencies - IMPORTANT: Set in sys.modules BEFORE importing
    # Use patch.dict to ensure mocks are in place before any imports
    mock_modules = {
        "torch": mock_torch,
        "tqdm": mock_tqdm_class,
        "datasets": mock_datasets,
        "trl": mock_trl,
        "transformers": mock_transformers,
        "peft": mock_peft,
    }

    # Pre-populate sys.modules with mocks
    for name, mock_obj in mock_modules.items():
        if name not in sys.modules:
            sys.modules[name] = mock_obj

    # Set up package structure for relative imports
    with patch.dict("sys.modules", mock_modules, clear=False):
        # Create src package first
        import types
        import importlib.util

        src_package = types.ModuleType("src")
        sys.modules["src"] = src_package

        # Import base modules first (they don't have relative imports)
        import data_utils
        import config

        # Add to src package
        src_package.data_utils = data_utils
        src_package.config = config
        sys.modules["src.data_utils"] = data_utils
        sys.modules["src.config"] = config

        # Load modules with relative imports using importlib.util
        def load_module(name, path):
            spec = importlib.util.spec_from_file_location(f"src.{name}", path)
            module = importlib.util.module_from_spec(spec)
            # Set parent package
            module.__package__ = "src"
            sys.modules[f"src.{name}"] = module
            # Make sure all dependencies are mocked before loading
            spec.loader.exec_module(module)
            return module

        # Load modules in order (dependencies first)
        model_utils = load_module(
            "model_utils", os.path.join(src_path, "model_utils.py")
        )
        trainer = load_module("trainer", os.path.join(src_path, "trainer.py"))
        inference = load_module("inference", os.path.join(src_path, "inference.py"))

        # Also add to top-level for easier access
        sys.modules["model_utils"] = model_utils
        sys.modules["trainer"] = trainer
        sys.modules["inference"] = inference

        return {
            "data_utils": data_utils,
            "config": config,
            "model_utils": model_utils,
            "trainer": trainer,
            "inference": inference,
        }
