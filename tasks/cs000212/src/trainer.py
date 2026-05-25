"""
Training module
"""
import random
from typing import Tuple, Optional, List, Dict, Any
from datasets import Dataset
from trl import SFTConfig, SFTTrainer
from transformers import PreTrainedTokenizer
from peft import LoraConfig

from .config import TrainingConfig, LoRAConfig, DataConfig
from .data_utils import load_jsonlines, nshot_chats


def format_gsm8k_data(
    tokenizer: PreTrainedTokenizer,
    train_file: str,
    data_config: DataConfig,
    fixed_examples: Optional[List[Dict[str, Any]]] = None
) -> Tuple[Dataset, int]:
    """
    Format GSM8K data for fine-tuning
    
    Args:
        tokenizer: Tokenizer object
        train_file: Training data file path
        data_config: Data configuration
        fixed_examples: Fixed few-shot examples
        
    Returns:
        (Formatted dataset, maximum token length)
    """
    # TODO: Implement this function
    return Dataset.from_list([]), 0


def create_trainer(
    model,
    tokenizer: PreTrainedTokenizer,
    train_dataset: Dataset,
    training_config: TrainingConfig,
    lora_config: LoRAConfig,
    max_seq_length: int
) -> SFTTrainer:
    """
    Create SFT trainer
    
    Args:
        model: Model object
        tokenizer: Tokenizer object
        train_dataset: Training dataset
        training_config: Training configuration
        lora_config: LoRA configuration
        max_seq_length: Maximum sequence length
        
    Returns:
        SFTTrainer object
    """
    # Create training arguments
    training_arguments = SFTConfig(
        seed=training_config.seed,
        data_seed=training_config.data_seed,
        output_dir=training_config.output_dir,
        per_device_train_batch_size=training_config.per_device_train_batch_size,
        gradient_accumulation_steps=training_config.gradient_accumulation_steps,
        optim=training_config.optim,
        num_train_epochs=training_config.num_train_epochs,
        logging_strategy=training_config.logging_strategy,
        logging_steps=training_config.logging_steps,
        save_strategy=training_config.save_strategy,
        save_steps=training_config.save_steps,
        lr_scheduler_type=training_config.lr_scheduler_type,
        learning_rate=training_config.learning_rate,
        weight_decay=training_config.weight_decay,
        bf16=training_config.bf16,
        group_by_length=training_config.group_by_length,
        max_seq_length=max_seq_length,
        dataset_text_field=training_config.dataset_text_field,
        report_to=training_config.report_to,
    )
    
    # Create LoRA configuration
    peft_config = LoraConfig(
        r=lora_config.r,
        lora_alpha=lora_config.lora_alpha,
        lora_dropout=lora_config.lora_dropout,
        bias=lora_config.bias,
        task_type=lora_config.task_type,
        target_modules=lora_config.target_modules
    )
    
    # Create trainer
    trainer = SFTTrainer(
        model=model,
        train_dataset=train_dataset,
        peft_config=peft_config,
        processing_class=tokenizer,
        args=training_arguments,
    )
    
    return trainer

