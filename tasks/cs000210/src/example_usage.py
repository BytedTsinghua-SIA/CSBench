"""
使用示例
展示如何使用llm_utils模块中的各个功能
注意：此示例需要实际的模型和tokenizer才能运行
"""

# 示例1: Q1 - 文本生成
def example_generate_text():
    """示例：使用generate_text_from_prompt生成文本"""
    # 注意：需要先加载模型和tokenizer
    # from transformers import AutoTokenizer, AutoModelForCausalLM
    # tokenizer = AutoTokenizer.from_pretrained("google/gemma-2-2b-it")
    # model = AutoModelForCausalLM.from_pretrained("google/gemma-2-2b-it")
    
    from llm_utils import generate_text_from_prompt
    
    # 使用chat template
    # question = "Please tell me about machine learning."
    # chat = [{"role": "user", "content": question}]
    # prompt_with_template = tokenizer.apply_chat_template(chat, tokenize=False, add_generation_prompt=True)
    # response = generate_text_from_prompt(prompt_with_template, tokenizer, model)
    
    # 不使用chat template
    # response = generate_text_from_prompt(question, tokenizer, model)
    
    print("示例1: 文本生成功能已实现")


# 示例2: Q3 - Tokenization
def example_tokenize():
    """示例：使用tokenize_sentence进行tokenization"""
    from llm_utils import tokenize_sentence
    
    # 注意：需要先加载tokenizer
    # from transformers import AutoTokenizer
    # tokenizer = AutoTokenizer.from_pretrained("google/gemma-2-2b-it")
    
    # sentence = "I love taking a Machine Learning course by Professor Hung-yi Lee, What about you?"
    # token_ids, tokens = tokenize_sentence(sentence, tokenizer)
    
    # for t, t_id in zip(tokens, token_ids):
    #     print(f"Token: {t}, token index: {t_id}")
    
    print("示例2: Tokenization功能已实现")


# 示例3: Q4 - Top-p采样
def example_top_p_sampling():
    """示例：使用generate_with_top_p进行top-p采样"""
    from llm_utils import generate_with_top_p, compute_self_bleu
    
    # 注意：需要先加载模型和tokenizer
    # from transformers import AutoTokenizer, AutoModelForCausalLM
    # tokenizer = AutoTokenizer.from_pretrained("google/gemma-2-2b-it")
    # model = AutoModelForCausalLM.from_pretrained("google/gemma-2-2b-it")
    
    # prompt = "Generate a paraphrase of the sentence 'Professor Hung-yi Lee is one of the best teachers in the domain of machine learning'."
    # input_ids = tokenizer(prompt, return_tensors="pt")
    
    # generated_output = generate_with_top_p(
    #     model=model,
    #     tokenizer=tokenizer,
    #     input_ids=input_ids.input_ids,
    #     top_p=0.6,
    #     max_new_tokens=30
    # )
    
    # 计算self-BLEU
    # generated_sentences = ["sentence1", "sentence2", ...]
    # bleu_score = compute_self_bleu(generated_sentences)
    
    print("示例3: Top-p采样功能已实现")


# 示例4: Q6 - 提取模型输出
def example_extract_outputs():
    """示例：提取logits和attention scores"""
    from llm_utils import extract_model_outputs
    
    # 注意：需要先加载模型和tokenizer
    # from transformers import AutoTokenizer, AutoModelForCausalLM
    # tokenizer = AutoTokenizer.from_pretrained("google/gemma-2-2b-it")
    # model = AutoModelForCausalLM.from_pretrained("google/gemma-2-2b-it")
    
    # prompt = "Google "
    # input_ids = tokenizer(prompt, return_tensors="pt").to("cuda")
    
    # outputs = model(
    #     input_ids.input_ids,
    #     attention_mask=input_ids.attention_mask,
    #     output_attentions=True
    # )
    
    # logits, attention_scores = extract_model_outputs(outputs)
    
    print("示例4: 提取模型输出功能已实现")


# 示例5: Q7 - 激活分析
def example_activation_analysis():
    """示例：使用SAE进行激活分析"""
    from llm_utils import get_max_activation, plot_token_activations, plot_layer_activations
    
    # 注意：需要先加载模型、tokenizer和SAE
    # from transformers import AutoTokenizer, AutoModelForCausalLM
    # from sae_lens import SAE
    # tokenizer = AutoTokenizer.from_pretrained("google/gemma-2-2b-it")
    # model = AutoModelForCausalLM.from_pretrained("google/gemma-2-2b-it")
    # sae, cfg_dict, sparsity = SAE.from_pretrained(
    #     release="gemma-scope-2b-pt-res-canonical",
    #     sae_id="layer_20/width_16k/canonical",
    # )
    
    # 计算最大激活值
    # prompt_a = "Time travel offers me the opportunity to correct past errors..."
    # max_activation_a = get_max_activation(model, tokenizer, sae, prompt_a, feature_idx=10004)
    
    # 绘制token激活值
    # plot_token_activations(model, tokenizer, sae, prompt, feature_idx=10004, layer_idx=24)
    
    # 绘制层激活值
    # plot_layer_activations(model, tokenizer, sae, prompt, token_idx=1, feature_idx=10004)
    
    print("示例5: 激活分析功能已实现")


if __name__ == "__main__":
    print("=" * 60)
    print("LLM Utils 使用示例")
    print("=" * 60)
    print()
    
    example_generate_text()
    example_tokenize()
    example_top_p_sampling()
    example_extract_outputs()
    example_activation_analysis()
    
    print()
    print("=" * 60)
    print("所有功能示例已展示")
    print("注意：实际使用需要加载相应的模型和tokenizer")
    print("=" * 60)

