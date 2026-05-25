"""
Test configuration file
"""
import unittest
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from config import (
    ModelConfig,
    LoRAConfig,
    TrainingConfig,
    InferenceConfig,
    DatasetConfig,
    Config
)


class TestModelConfig(unittest.TestCase):
    """Test ModelConfig"""

    def test_default_values(self):
        """Test default values"""
        config = ModelConfig()
        self.assertEqual(config.model_name, "unsloth/Llama-2-7b-bnb-4bit")
        self.assertEqual(config.max_seq_length, 2048)
        self.assertIsNone(config.dtype)
        self.assertTrue(config.load_in_4bit)
        self.assertEqual(config.chat_template, "llama-3.1")

    def test_custom_values(self):
        """Test custom values"""
        config = ModelConfig(
            model_name="custom_model",
            max_seq_length=4096,
            dtype="float16",
            load_in_4bit=False
        )
        self.assertEqual(config.model_name, "custom_model")
        self.assertEqual(config.max_seq_length, 4096)
        self.assertEqual(config.dtype, "float16")
        self.assertFalse(config.load_in_4bit)


class TestLoRAConfig(unittest.TestCase):
    """Test LoRAConfig"""

    def test_default_values(self):
        """Test default values"""
        config = LoRAConfig()
        self.assertEqual(config.r, 16)
        self.assertEqual(config.lora_alpha, 16)
        self.assertEqual(config.lora_dropout, 0.0)
        self.assertEqual(config.bias, "none")
        self.assertEqual(config.use_gradient_checkpointing, "unsloth")
        self.assertEqual(config.random_state, 3407)
        self.assertFalse(config.use_rslora)
        self.assertIsNone(config.loftq_config)

    def test_target_modules(self):
        """Test target_modules default values"""
        config = LoRAConfig()
        expected_modules = [
            "q_proj", "k_proj", "v_proj", "o_proj",
            "gate_proj", "up_proj", "down_proj"
        ]
        self.assertEqual(config.target_modules, expected_modules)

    def test_custom_target_modules(self):
        """Test custom target_modules"""
        custom_modules = ["q_proj", "v_proj"]
        config = LoRAConfig(target_modules=custom_modules)
        self.assertEqual(config.target_modules, custom_modules)


class TestTrainingConfig(unittest.TestCase):
    """Test TrainingConfig"""

    def test_default_values(self):
        """Test default values"""
        config = TrainingConfig()
        self.assertEqual(config.per_device_train_batch_size, 2)
        self.assertEqual(config.gradient_accumulation_steps, 4)
        self.assertEqual(config.warmup_steps, 10)
        self.assertEqual(config.num_train_epochs, 2)
        self.assertEqual(config.learning_rate, 2e-4)
        self.assertEqual(config.optim, "adamw_8bit")
        self.assertEqual(config.weight_decay, 0.01)
        self.assertEqual(config.lr_scheduler_type, "linear")
        self.assertEqual(config.seed, 3407)
        self.assertEqual(config.output_dir, "outputs")


class TestInferenceConfig(unittest.TestCase):
    """Test InferenceConfig"""

    def test_default_values(self):
        """Test default values"""
        config = InferenceConfig()
        self.assertTrue(config.do_sample)
        self.assertEqual(config.max_new_tokens, 100)
        self.assertTrue(config.use_cache)
        self.assertEqual(config.temperature, 1.5)
        self.assertEqual(config.top_p, 0.9)
        self.assertEqual(config.top_k, 30)


class TestDatasetConfig(unittest.TestCase):
    """Test DatasetConfig"""

    def test_default_values(self):
        """Test default values"""
        config = DatasetConfig()
        self.assertEqual(config.max_training_samples, 100)
        self.assertEqual(config.dataset_used, "sorted_dataset_simple")
        self.assertEqual(config.dataset_range_start, 0)
        self.assertEqual(config.dataset_range_end, 100)


class TestConfig(unittest.TestCase):
    """Test main configuration class"""

    def test_default_initialization(self):
        """Test default initialization"""
        config = Config()
        self.assertIsInstance(config.model, ModelConfig)
        self.assertIsInstance(config.lora, LoRAConfig)
        self.assertIsInstance(config.training, TrainingConfig)
        self.assertIsInstance(config.inference, InferenceConfig)
        self.assertIsInstance(config.dataset, DatasetConfig)


if __name__ == "__main__":
    unittest.main()

