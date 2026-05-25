"""
Unit tests for config module
"""

import unittest
import sys
import os
from unittest.mock import patch, MagicMock

# Setup test imports
import sys
import os

# Tests are now inside src/tests
tests_path = os.path.dirname(__file__)
sys.path.insert(0, tests_path)
from test_helpers import setup_test_imports

modules = setup_test_imports()

# Import config classes
ModelConfig = modules["config"].ModelConfig
LoRAConfig = modules["config"].LoRAConfig
TrainingConfig = modules["config"].TrainingConfig
InferenceConfig = modules["config"].InferenceConfig
DataConfig = modules["config"].DataConfig
Config = modules["config"].Config


class TestModelConfig(unittest.TestCase):
    """Test ModelConfig class"""

    def test_default_values(self):
        """Test default configuration values"""
        config = ModelConfig()
        self.assertEqual(config.model_name, "meta-llama/Llama-3.2-1B-Instruct")
        self.assertTrue(config.load_in_4bit)
        self.assertTrue(config.bnb_4bit_use_double_quant)
        self.assertEqual(config.bnb_4bit_quant_type, "nf4")
        self.assertEqual(config.bnb_4bit_compute_dtype, "bfloat16")
        self.assertTrue(config.low_cpu_mem_usage)

    def test_custom_values(self):
        """Test custom configuration values"""
        config = ModelConfig(
            model_name="custom-model", load_in_4bit=False, bnb_4bit_quant_type="fp4"
        )
        self.assertEqual(config.model_name, "custom-model")
        self.assertFalse(config.load_in_4bit)
        self.assertEqual(config.bnb_4bit_quant_type, "fp4")


class TestLoRAConfig(unittest.TestCase):
    """Test LoRAConfig class"""

    def test_default_values(self):
        """Test default LoRA configuration values"""
        config = LoRAConfig()
        self.assertEqual(config.r, 8)
        self.assertEqual(config.lora_alpha, 16)
        self.assertEqual(config.lora_dropout, 0.05)
        self.assertEqual(config.bias, "none")
        self.assertEqual(config.task_type, "CAUSAL_LM")
        self.assertIsNotNone(config.target_modules)
        self.assertEqual(len(config.target_modules), 7)
        self.assertIn("up_proj", config.target_modules)
        self.assertIn("down_proj", config.target_modules)

    def test_custom_target_modules(self):
        """Test custom target modules"""
        custom_modules = ["q_proj", "v_proj"]
        config = LoRAConfig(target_modules=custom_modules)
        self.assertEqual(config.target_modules, custom_modules)


class TestTrainingConfig(unittest.TestCase):
    """Test TrainingConfig class"""

    def test_default_values(self):
        """Test default training configuration values"""
        config = TrainingConfig()
        self.assertEqual(config.seed, 1126)
        self.assertEqual(config.data_seed, 1126)
        self.assertEqual(config.output_dir, "sft")
        self.assertEqual(config.per_device_train_batch_size, 1)
        self.assertEqual(config.gradient_accumulation_steps, 4)
        self.assertEqual(config.optim, "paged_adamw_32bit")
        self.assertEqual(config.num_train_epochs, 1)
        self.assertEqual(config.learning_rate, 2e-4)
        self.assertEqual(config.weight_decay, 0.01)
        self.assertTrue(config.bf16)
        self.assertTrue(config.group_by_length)


class TestInferenceConfig(unittest.TestCase):
    """Test InferenceConfig class"""

    def test_default_values(self):
        """Test default inference configuration values"""
        config = InferenceConfig()
        self.assertEqual(config.max_new_tokens, 256)
        self.assertTrue(config.do_sample)
        self.assertEqual(config.temperature, 0.6)
        self.assertEqual(config.top_p, 0.9)
        self.assertFalse(config.use_greedy)

    def test_greedy_decoding(self):
        """Test greedy decoding configuration"""
        config = InferenceConfig(use_greedy=True)
        self.assertTrue(config.use_greedy)


class TestDataConfig(unittest.TestCase):
    """Test DataConfig class"""

    def test_default_values(self):
        """Test default data configuration values"""
        config = DataConfig()
        self.assertEqual(config.train_n_shot, 1)
        self.assertEqual(config.test_n_shot, 1)
        self.assertFalse(config.use_fixed_few_shot)
        self.assertEqual(config.fixed_few_shot_size, 4)

    def test_fixed_few_shot(self):
        """Test fixed few-shot configuration"""
        config = DataConfig(use_fixed_few_shot=True, fixed_few_shot_size=5)
        self.assertTrue(config.use_fixed_few_shot)
        self.assertEqual(config.fixed_few_shot_size, 5)


class TestConfig(unittest.TestCase):
    """Test Config class"""

    def test_default_initialization(self):
        """Test default configuration initialization"""
        config = Config()
        self.assertIsNotNone(config.model)
        self.assertIsNotNone(config.lora)
        self.assertIsNotNone(config.training)
        self.assertIsNotNone(config.inference)
        self.assertIsNotNone(config.data)
        self.assertEqual(config.cuda_device, "0")
        self.assertEqual(config.student_id, "")
        self.assertIsInstance(config.model, ModelConfig)
        self.assertIsInstance(config.lora, LoRAConfig)
        self.assertIsInstance(config.training, TrainingConfig)
        self.assertIsInstance(config.inference, InferenceConfig)
        self.assertIsInstance(config.data, DataConfig)

    def test_custom_initialization(self):
        """Test custom configuration initialization"""
        custom_model = ModelConfig(model_name="custom")
        custom_lora = LoRAConfig(r=16)
        config = Config(model=custom_model, lora=custom_lora, student_id="12345")

        self.assertEqual(config.model.model_name, "custom")
        self.assertEqual(config.lora.r, 16)
        self.assertEqual(config.student_id, "12345")
        # Other configs should still be initialized with defaults
        self.assertIsNotNone(config.training)
        self.assertIsNotNone(config.inference)
        self.assertIsNotNone(config.data)


if __name__ == "__main__":
    unittest.main()
