"""
Usage examples: demonstrate how to use each module
"""

from config import Config, ModelConfig, LoRAConfig, TrainingConfig
from model_utils import initialize_model, enable_inference_mode
from dataset_utils import (
    load_dataset_from_disk,
    sort_dataset_simple,
    create_formatting_prompts_func,
)
from training_utils import create_trainer, train_model
from inference_utils import generate_response, InferenceConfig


def example_basic_usage():
    """Basic usage example"""
    print("=" * 50)
    print("Basic Usage Example")
    print("=" * 50)

    # 1. Create configuration
    config = Config()

    # 2. Initialize model
    print("\nInitializing model...")
    model, tokenizer = initialize_model(config.model, config.lora)
    print("Model initialization complete")

    # 3. Load dataset (requires actual dataset path)
    # dataset = load_dataset_from_disk(config.dataset.dataset_path)
    # print(f"Dataset loaded, total {len(dataset)} samples")

    print("\nExample completed!")


def example_custom_config():
    """Custom configuration example"""
    print("=" * 50)
    print("Custom Configuration Example")
    print("=" * 50)

    # Create custom configuration
    model_config = ModelConfig(max_seq_length=4096, load_in_4bit=True)

    lora_config = LoRAConfig(r=32, lora_alpha=32)  # Higher rank

    training_config = TrainingConfig(
        per_device_train_batch_size=4, num_train_epochs=3, learning_rate=1e-4
    )

    inference_config = InferenceConfig(temperature=0.7, max_new_tokens=200, top_p=0.95)

    config = Config(
        model=model_config,
        lora=lora_config,
        training=training_config,
        inference=inference_config,
    )

    print("Custom configuration created")
    print(f"LoRA rank: {config.lora.r}")
    print(f"Training epochs: {config.training.num_train_epochs}")
    print(f"Inference temperature: {config.inference.temperature}")


def example_inference():
    """Inference example"""
    print("=" * 50)
    print("Inference Example")
    print("=" * 50)

    # Note: This requires loading a trained model first
    # model, tokenizer = load_model("lora_model", ModelConfig())
    # enable_inference_mode(model)

    # Create inference configuration
    inference_config = InferenceConfig(temperature=1.0, max_new_tokens=100)

    # Prepare messages
    messages = [{"role": "user", "content": "Hello, how are you?"}]

    # Generate response (requires actual model)
    # response = generate_response(
    #     model, tokenizer, messages, inference_config
    # )
    # print(f"Model response: {response}")

    print("Inference example completed (requires actual model)")


if __name__ == "__main__":
    print("Homework 5 Feature Usage Examples\n")

    # Run examples
    example_basic_usage()
    print("\n")
    example_custom_config()
    print("\n")
    example_inference()
