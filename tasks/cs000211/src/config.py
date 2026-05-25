"""
Configuration file: stores all hyperparameters and configuration options
"""

from dataclasses import dataclass
from typing import Optional, List


@dataclass
class ModelConfig:
    """Model configuration"""

    model_name: str = "unsloth/Llama-2-7b-bnb-4bit"
    max_seq_length: int = 2048
    dtype: Optional[str] = None  # None for auto detection
    load_in_4bit: bool = True
    chat_template: str = "llama-3.1"


@dataclass
class LoRAConfig:
    """LoRA adapter configuration"""

    r: int = 16  # LoRA rank
    lora_alpha: int = 16  # LoRA alpha
    target_modules: List[str] = None
    lora_dropout: float = 0.0
    bias: str = "none"
    use_gradient_checkpointing: str = "unsloth"
    random_state: int = 3407
    use_rslora: bool = False
    loftq_config: Optional[dict] = None

    def __post_init__(self):
        if self.target_modules is None:
            self.target_modules = [
                "q_proj",
                "k_proj",
                "v_proj",
                "o_proj",
                "gate_proj",
                "up_proj",
                "down_proj",
            ]


@dataclass
class TrainingConfig:
    """Training configuration"""

    per_device_train_batch_size: int = 2
    gradient_accumulation_steps: int = 4
    warmup_steps: int = 10
    num_train_epochs: int = 2
    learning_rate: float = 2e-4
    optim: str = "adamw_8bit"
    weight_decay: float = 0.01
    lr_scheduler_type: str = "linear"
    seed: int = 3407  # Do not modify to ensure reproducibility
    output_dir: str = "outputs"
    logging_steps: int = 1
    dataset_num_proc: int = 2
    packing: bool = False


@dataclass
class InferenceConfig:
    """Inference configuration"""

    do_sample: bool = True
    max_new_tokens: int = 100
    use_cache: bool = True
    temperature: float = 1.5
    top_p: float = 0.9
    top_k: int = 30


@dataclass
class DatasetConfig:
    """Dataset configuration"""

    dataset_path: str = "/content/ML_Spring2025_HW5/fastchat_alpaca_52k"
    test_set_path: str = "/content/ML_Spring2025_HW5/test_set_evol_instruct_150.json"
    max_training_samples: int = 100  # Maximum 100 samples for training
    dataset_used: str = (
        "sorted_dataset_simple"  # "sorted_dataset_simple" or "sorted_dataset_advanced"
    )
    dataset_range_start: int = 0
    dataset_range_end: int = 100


@dataclass
class Config:
    """Main configuration class"""

    model: ModelConfig = None
    lora: LoRAConfig = None
    training: TrainingConfig = None
    inference: InferenceConfig = None
    dataset: DatasetConfig = None

    def __post_init__(self):
        if self.model is None:
            self.model = ModelConfig()
        if self.lora is None:
            self.lora = LoRAConfig()
        if self.training is None:
            self.training = TrainingConfig()
        if self.inference is None:
            self.inference = InferenceConfig()
        if self.dataset is None:
            self.dataset = DatasetConfig()
