"""
Main program: integrates all functionality
"""

import json
import os

# Support both relative and absolute imports
try:
    from .config import Config
    from .model_utils import (
        initialize_model,
        setup_chat_template,
        enable_inference_mode,
        save_model,
        load_model,
    )
    from .dataset_utils import (
        load_dataset_from_disk,
        sort_dataset_simple,
        sort_dataset_advanced,
        prepare_training_dataset,
        create_formatting_prompts_func,
    )
    from .training_utils import create_trainer, train_model, curriculum_training
    from .inference_utils import run_inference_on_test_set
except ImportError:
    # Fallback to absolute imports for testing
    from config import Config
    from model_utils import (
        initialize_model,
        setup_chat_template,
        enable_inference_mode,
        save_model,
        load_model,
    )
    from dataset_utils import (
        load_dataset_from_disk,
        sort_dataset_simple,
        sort_dataset_advanced,
        prepare_training_dataset,
        create_formatting_prompts_func,
    )
    from training_utils import create_trainer, train_model, curriculum_training
    from inference_utils import run_inference_on_test_set


def main(config: Config = None, use_curriculum: bool = False):
    """
    Main function: executes the complete fine-tuning pipeline

    Args:
        config: Configuration object, uses default config if None
        use_curriculum: Whether to use curriculum training
    """
    if config is None:
        config = Config()

    print("=" * 50)
    print("Starting Fine-tuning Pipeline")
    print("=" * 50)

    # 1. Initialize model
    print("\n[1/6] Initializing model and LoRA adapter...")
    model, tokenizer = initialize_model(config.model, config.lora)
    print("Model initialization complete")

    # 2. Load and prepare dataset
    print("\n[2/6] Loading and preparing dataset...")
    dataset = load_dataset_from_disk(config.dataset.dataset_path)
    print(f"Dataset loaded, total {len(dataset)} samples")

    # Sort dataset
    sorted_dataset_simple = sort_dataset_simple(dataset)
    sorted_dataset_advanced = sort_dataset_advanced(dataset)
    print("Dataset sorting complete")

    # 3. Prepare training dataset
    print("\n[3/6] Preparing training dataset...")
    formatting_func = create_formatting_prompts_func(tokenizer)

    if config.dataset.dataset_used == "sorted_dataset_simple":
        selected_dataset = sorted_dataset_simple
    else:
        selected_dataset = sorted_dataset_advanced

    train_dataset = prepare_training_dataset(
        selected_dataset,
        config.dataset.dataset_used,
        config.dataset.dataset_range_start,
        config.dataset.dataset_range_end,
        formatting_func,
    )
    print(f"Training dataset prepared, total {len(train_dataset)} samples")

    # 4. Train model
    print("\n[4/6] Starting model training...")
    if use_curriculum:
        print("Using curriculum training mode...")
        # Calculate number of samples used in each stage (total not exceeding 100)
        simple_count = config.dataset.max_training_samples // 2
        advanced_count = config.dataset.max_training_samples - simple_count

        stats_list = curriculum_training(
            model,
            tokenizer,
            sorted_dataset_simple,
            sorted_dataset_advanced,
            config.training,
            config.model.max_seq_length,
            formatting_func,
            simple_range=(0, simple_count),
            advanced_range=(0, advanced_count),
        )
        print("Curriculum training completed")
        for stage, stats in stats_list:
            print(f"  {stage} stage training statistics: {stats}")
    else:
        trainer = create_trainer(
            model,
            tokenizer,
            train_dataset,
            config.training,
            config.model.max_seq_length,
        )
        trainer_stats = train_model(trainer)
        print("Training completed")
        print(f"Training statistics: {trainer_stats}")

    # 5. Save model
    print("\n[5/6] Saving model...")
    save_path = "lora_model"
    save_model(model, tokenizer, save_path)
    print(f"Model saved to {save_path}")

    # Save training configuration
    training_config_dict = {
        "per_device_train_batch_size": config.training.per_device_train_batch_size,
        "gradient_accumulation_steps": config.training.gradient_accumulation_steps,
        "warmup_steps": config.training.warmup_steps,
        "num_train_epochs": config.training.num_train_epochs,
        "learning_rate": config.training.learning_rate,
        "optim": config.training.optim,
        "weight_decay": config.training.weight_decay,
        "lr_scheduler_type": config.training.lr_scheduler_type,
        "seed": config.training.seed,
    }
    with open("training_config.json", "w", encoding="utf-8") as f:
        json.dump(training_config_dict, f, indent=4)
    print("Training configuration saved")

    # 6. Inference
    print("\n[6/6] Running inference...")
    if os.path.exists(config.dataset.test_set_path):
        enable_inference_mode(model)
        inference_results = run_inference_on_test_set(
            model, tokenizer, config.dataset.test_set_path, config.inference
        )
        print("Inference completed")
    else:
        print(
            f"Test set file does not exist: {config.dataset.test_set_path}, skipping inference"
        )

    print("\n" + "=" * 50)
    print("Fine-tuning pipeline completed!")
    print("=" * 50)


if __name__ == "__main__":
    # Run with default configuration
    main()
