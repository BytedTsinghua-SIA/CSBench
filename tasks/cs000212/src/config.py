"""
Configuration file
"""

import torch
from dataclasses import dataclass
from typing import Optional


@dataclass
class ModelConfig:
    """Model configuration"""

    model_name: str = ""  # TODO: Set default value
    load_in_4bit: bool = False  # TODO: Set default value
    bnb_4bit_use_double_quant: bool = False  # TODO: Set default value
    bnb_4bit_quant_type: str = ""  # TODO: Set default value
    bnb_4bit_compute_dtype: str = ""  # TODO: Set default value
    low_cpu_mem_usage: bool = False  # TODO: Set default value


@dataclass
class LoRAConfig:
    """LoRA configuration"""

    r: int = 0  # TODO: Set default value
    lora_alpha: int = 0  # TODO: Set default value
    lora_dropout: float = 0.0  # TODO: Set default value
    bias: str = ""  # TODO: Set default value
    task_type: str = ""  # TODO: Set default value
    target_modules: Optional[list] = None

    def __post_init__(self):
        # TODO: Implement initialization
        if self.target_modules is None:
            self.target_modules = []


@dataclass
class TrainingConfig:
    """Training configuration"""

    seed: int = 0  # TODO: Set default value
    data_seed: int = 0  # TODO: Set default value
    output_dir: str = ""  # TODO: Set default value
    per_device_train_batch_size: int = 0  # TODO: Set default value
    gradient_accumulation_steps: int = 0  # TODO: Set default value
    optim: str = ""  # TODO: Set default value
    num_train_epochs: int = 0  # TODO: Set default value
    logging_strategy: str = ""  # TODO: Set default value
    logging_steps: float = 0.0  # TODO: Set default value
    save_strategy: str = ""  # TODO: Set default value
    save_steps: float = 0.0  # TODO: Set default value
    lr_scheduler_type: str = ""  # TODO: Set default value
    learning_rate: float = 0.0  # TODO: Set default value
    weight_decay: float = 0.0  # TODO: Set default value
    bf16: bool = False  # TODO: Set default value
    group_by_length: bool = False  # TODO: Set default value
    dataset_text_field: str = ""  # TODO: Set default value
    report_to: str = ""  # TODO: Set default value


@dataclass
class InferenceConfig:
    """Inference configuration"""

    max_new_tokens: int = 0  # TODO: Set default value
    do_sample: bool = False  # TODO: Set default value
    temperature: float = 0.0  # TODO: Set default value
    top_p: float = 0.0  # TODO: Set default value
    use_greedy: bool = False  # TODO: Set default value


@dataclass
class DataConfig:
    """Data configuration"""

    train_n_shot: int = 0  # TODO: Set default value
    test_n_shot: int = 0  # TODO: Set default value
    use_fixed_few_shot: bool = True  # TODO: Set default value (changed to make tests fail)
    fixed_few_shot_size: int = 0  # TODO: Set default value


@dataclass
class Config:
    """Main configuration"""

    model: ModelConfig = None
    lora: LoRAConfig = None
    training: TrainingConfig = None
    inference: InferenceConfig = None
    data: DataConfig = None
    cuda_device: str = "0"
    student_id: str = ""

    def __post_init__(self):
        # TODO: Implement initialization
        pass
