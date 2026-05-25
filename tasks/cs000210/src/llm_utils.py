"""
LLM Transformers工具函数
实现notebook中要求的所有功能
"""

import torch
import numpy as np
from typing import List, Tuple, Optional, Dict, Any
import matplotlib.pyplot as plt


def generate_text_from_prompt(
    prompt: str,
    tokenizer,
    model,
    max_new_tokens: int = 200,
    do_sample: bool = False,
    pad_token_id: Optional[int] = None,
    eos_token_id: Optional[int] = None,
) -> str:
    """
    从prompt生成文本输出 (Q1.1 ~ Q1.4)

    Args:
        prompt: 输入到模型的prompt
        tokenizer: 用于编码/解码的tokenizer
        model: 用于生成输出的模型
        max_new_tokens: 最大生成token数
        do_sample: 是否使用采样（设置为False以获得确定性响应）
        pad_token_id: padding token id
        eos_token_id: end of sequence token id

    Returns:
        模型的响应文本
    """
    pass


def tokenize_sentence(
    sentence: str, tokenizer, add_special_tokens: bool = False
) -> Tuple[List[int], List[str]]:
    """
    对句子进行tokenization (Q3.1 ~ Q3.4)

    Args:
        sentence: 要tokenize的句子
        tokenizer: tokenizer对象
        add_special_tokens: 是否添加特殊token

    Returns:
        (token_ids, tokens): token ID列表和对应的token字符串列表
    """
    pass


def generate_with_top_p(
    model,
    tokenizer,
    input_ids: torch.Tensor,
    top_p: float = 0.6,
    max_new_tokens: int = 30,
    generation_params: Optional[Dict[str, Any]] = None,
) -> torch.Tensor:
    """
    使用top-p (nucleus)采样生成文本 (Q4.3 ~ Q4.6)

    Args:
        model: 生成模型
        tokenizer: tokenizer对象
        input_ids: 输入token IDs
        top_p: nucleus采样的p值
        max_new_tokens: 最大生成token数
        generation_params: 其他生成参数

    Returns:
        生成的token序列
    """
    pass


def extract_model_outputs(outputs) -> Tuple[torch.Tensor, Tuple]:
    """
    从模型输出中提取logits和attention scores (Q6.1 ~ Q6.4)

    Args:
        outputs: 模型的输出对象

    Returns:
        (logits, attention_scores): logits张量和attention scores元组
    """
    pass


def get_max_activation(
    model, tokenizer, sae, prompt: str, feature_idx: int = 10004
) -> float:
    """
    计算特定feature在SAE中的最大激活值 (Q7.2 ~ Q7.3)

    Args:
        model: Transformer模型
        tokenizer: tokenizer对象
        sae: Sparse Autoencoder
        prompt: 输入文本prompt
        feature_idx: SAE中的feature索引

    Returns:
        指定feature索引的最大激活值
    """
    pass


def plot_token_activations(
    model,
    tokenizer,
    sae,
    prompt: str,
    feature_idx: int = 10004,
    layer_idx: Optional[int] = None,
) -> None:
    """
    绘制特定层中每个token的激活值 (Q7.4 ~ Q7.6)

    Args:
        model: Transformer模型
        tokenizer: tokenizer对象
        sae: Sparse Autoencoder模型
        prompt: 输入文本字符串
        feature_idx: 要分析的feature索引
        layer_idx: 要分析的层索引（None则使用sae.cfg.hook_layer）
    """
    pass


def plot_layer_activations(
    model, tokenizer, sae, prompt: str, token_idx: int = 0, feature_idx: int = 10004
) -> None:
    """
    绘制特定token在所有层中的激活值 (Q7.7 ~ Q7.9)

    Args:
        model: Transformer模型
        tokenizer: tokenizer对象
        sae: Sparse Autoencoder模型
        prompt: 输入文本字符串
        token_idx: 要分析的token索引
        feature_idx: 要分析的feature索引
    """
    pass


def compute_self_bleu(generated_sentences: List[str]) -> float:
    """
    计算生成句子的self-BLEU分数

    Args:
        generated_sentences: 生成的句子列表

    Returns:
        self-BLEU分数
    """
    pass
