"""
Model loading and configuration utilities module
"""

import os
import torch
from transformers import (
    AutoModelForCausalLM,
    AutoTokenizer,
    BitsAndBytesConfig,
    pipeline,
)
from peft import LoraConfig, get_peft_model, PeftModel
from .config import ModelConfig, LoRAConfig, InferenceConfig


def setup_device(cuda_device: str = "0"):
    """
    Setup CUDA device

    Args:
        cuda_device: CUDA device ID
    """
    # TODO: Implement this function
    return None


def create_bitsandbytes_config(config: ModelConfig) -> BitsAndBytesConfig:
    """
    Create BitsAndBytes configuration

    Args:
        config: Model configuration

    Returns:
        BitsAndBytesConfig object
    """
    compute_dtype_map = {
        "bfloat16": torch.bfloat16,
        "float16": torch.float16,
        "float32": torch.float32,
    }

    return BitsAndBytesConfig(
        load_in_4bit=config.load_in_4bit,
        bnb_4bit_use_double_quant=config.bnb_4bit_use_double_quant,
        bnb_4bit_quant_type=config.bnb_4bit_quant_type,
        bnb_4bit_compute_dtype=compute_dtype_map.get(
            config.bnb_4bit_compute_dtype, torch.bfloat16
        ),
    )


def load_model_and_tokenizer(model_config: ModelConfig, lora_config: LoRAConfig = None):
    """
    Load model and tokenizer

    Args:
        model_config: Model configuration
        lora_config: LoRA configuration (if None, LoRA will not be applied)

    Returns:
        (model, tokenizer) or (peft_model, tokenizer)
    """
    # Create quantization configuration
    bnb_config = create_bitsandbytes_config(model_config)

    # Load model
    model = AutoModelForCausalLM.from_pretrained(
        pretrained_model_name_or_path=model_config.model_name,
        quantization_config=bnb_config,
        low_cpu_mem_usage=model_config.low_cpu_mem_usage,
    )

    # Load tokenizer
    tokenizer = AutoTokenizer.from_pretrained(
        pretrained_model_name_or_path=model_config.model_name,
    )

    # Add pad token
    if tokenizer.pad_token is None:
        tokenizer.add_special_tokens({"pad_token": "[PAD]"})

    # Apply LoRA
    if lora_config is not None:
        peft_config = LoraConfig(
            r=lora_config.r,
            lora_alpha=lora_config.lora_alpha,
            lora_dropout=lora_config.lora_dropout,
            bias=lora_config.bias,
            task_type=lora_config.task_type,
            target_modules=lora_config.target_modules,
        )
        model = get_peft_model(model, peft_config)
        return model, tokenizer, peft_config

    return model, tokenizer, None


def create_generation_pipeline(
    model, tokenizer, inference_config: InferenceConfig, device: torch.device = None
):
    """
    Create text generation pipeline

    Args:
        model: Model object
        tokenizer: Tokenizer object
        inference_config: Inference configuration
        device: Device (if None, auto-detect)

    Returns:
        Pipeline object
    """
    generation_kwargs = {
        "max_new_tokens": inference_config.max_new_tokens,
        "pad_token_id": tokenizer.eos_token_id,
    }

    if inference_config.use_greedy:
        generation_kwargs.update(
            {
                "do_sample": False,
            }
        )
    else:
        generation_kwargs.update(
            {
                "do_sample": inference_config.do_sample,
                "temperature": inference_config.temperature,
                "top_p": inference_config.top_p,
            }
        )

    generator = pipeline(
        "text-generation",
        model=model,
        tokenizer=tokenizer,
        device=device,
        **generation_kwargs,
    )

    return generator


def load_adapter(model, adapter_path: str):
    """
    Load LoRA adapter

    Args:
        model: Base model
        adapter_path: Adapter path

    Returns:
        Model with adapter loaded
    """
    return PeftModel.from_pretrained(model, adapter_path)
