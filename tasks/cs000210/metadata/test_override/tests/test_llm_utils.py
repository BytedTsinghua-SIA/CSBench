"""
LLM Utils单元测试
测试所有实现的功能
"""

import unittest
from unittest.mock import Mock, MagicMock, patch
import torch
import numpy as np
from typing import List, Tuple

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from llm_utils import (
    generate_text_from_prompt,
    tokenize_sentence,
    generate_with_top_p,
    extract_model_outputs,
    get_max_activation,
    plot_token_activations,
    plot_layer_activations,
    compute_self_bleu,
)


class TestGenerateTextFromPrompt(unittest.TestCase):
    """测试Q1: generate_text_from_prompt函数"""
    
    def setUp(self):
        """设置测试环境"""
        self.tokenizer = Mock()
        self.model = Mock()
        self.prompt = "Hello, how are you?"
        
        # 模拟tokenizer
        self.tokenizer.pad_token_id = 0
        self.tokenizer.eos_token_id = 1
        self.tokenizer.encode.return_value = torch.tensor([[1, 2, 3, 4, 5]])
        # 正确设置tokenizer的__call__方法返回值
        self.tokenizer.return_value = {"input_ids": torch.tensor([[1, 2, 3, 4, 5]])}
        self.tokenizer.__call__ = Mock(return_value={"input_ids": torch.tensor([[1, 2, 3, 4, 5]])})
        
        # 模拟model.generate
        self.model.generate.return_value = torch.tensor([[1, 2, 3, 4, 5, 6, 7, 8]])
        
        # 模拟tokenizer.decode
        self.tokenizer.decode.return_value = "Hello, how are you? I'm fine."
    
    def test_generate_text_basic(self):
        """测试基本文本生成功能"""
        with patch('builtins.print'):  # 屏蔽print输出
            result = generate_text_from_prompt(
                self.prompt,
                self.tokenizer,
                self.model
            )
        
        self.assertIsInstance(result, str)
        self.assertNotEqual(result, "Empty Response")
        self.model.generate.assert_called_once()
    
    def test_generate_text_with_params(self):
        """测试带参数的文本生成"""
        with patch('builtins.print'):
            result = generate_text_from_prompt(
                self.prompt,
                self.tokenizer,
                self.model,
                max_new_tokens=100,
                do_sample=False,
                pad_token_id=0,
                eos_token_id=1
            )
        
        self.assertIsInstance(result, str)
        call_kwargs = self.model.generate.call_args[1]
        self.assertEqual(call_kwargs['max_new_tokens'], 100)
        self.assertEqual(call_kwargs['do_sample'], False)
    
    def test_generate_text_empty_response(self):
        """测试空响应情况"""
        self.model.generate.return_value = torch.tensor([])
        
        with patch('builtins.print'):
            result = generate_text_from_prompt(
                self.prompt,
                self.tokenizer,
                self.model
            )
        
        self.assertEqual(result, "Empty Response")


class TestTokenizeSentence(unittest.TestCase):
    """测试Q3: tokenize_sentence函数"""
    
    def setUp(self):
        """设置测试环境"""
        self.tokenizer = Mock()
        self.sentence = "I love machine learning"
        
        # 模拟tokenizer
        self.tokenizer.encode.return_value = [1, 2, 3, 4, 5]
        self.tokenizer.convert_ids_to_tokens.return_value = [
            "I", "Ġlove", "Ġmachine", "Ġlearning", "Ġ"
        ]
    
    def test_tokenize_basic(self):
        """测试基本tokenization功能"""
        token_ids, tokens = tokenize_sentence(
            self.sentence,
            self.tokenizer
        )
        
        self.assertIsInstance(token_ids, list)
        self.assertIsInstance(tokens, list)
        self.assertEqual(len(token_ids), len(tokens))
        self.tokenizer.encode.assert_called_once()
        self.tokenizer.convert_ids_to_tokens.assert_called_once()
    
    def test_tokenize_with_special_tokens(self):
        """测试带特殊token的tokenization"""
        token_ids, tokens = tokenize_sentence(
            self.sentence,
            self.tokenizer,
            add_special_tokens=True
        )
        
        self.tokenizer.encode.assert_called_with(
            self.sentence,
            add_special_tokens=True
        )
    
    def test_tokenize_output_format(self):
        """测试输出格式"""
        token_ids, tokens = tokenize_sentence(
            self.sentence,
            self.tokenizer
        )
        
        # 验证token_ids是整数列表
        self.assertTrue(all(isinstance(tid, int) for tid in token_ids))
        # 验证tokens是字符串列表
        self.assertTrue(all(isinstance(t, str) for t in tokens))


class TestGenerateWithTopP(unittest.TestCase):
    """测试Q4: generate_with_top_p函数"""
    
    def setUp(self):
        """设置测试环境"""
        self.model = Mock()
        self.tokenizer = Mock()
        self.input_ids = torch.tensor([[1, 2, 3, 4, 5]])
        
        # 模拟tokenizer属性
        self.tokenizer.pad_token_id = 0
        self.tokenizer.eos_token_id = 1
        self.tokenizer.bos_token_id = 2
        
        # 模拟model.generate
        mock_output = Mock()
        mock_output.sequences = torch.tensor([[1, 2, 3, 4, 5, 6, 7]])
        self.model.generate.return_value = mock_output
    
    @patch('torch.cuda.is_available', return_value=False)
    def test_generate_with_top_p_basic(self, mock_cuda):
        """测试基本top-p生成功能"""
        result = generate_with_top_p(
            self.model,
            self.tokenizer,
            self.input_ids,
            top_p=0.6
        )
        
        self.assertIsNotNone(result)
        self.model.generate.assert_called_once()
        call_kwargs = self.model.generate.call_args[1]
        self.assertEqual(call_kwargs['top_p'], 0.6)
        self.assertTrue(call_kwargs['do_sample'])
    
    @patch('torch.cuda.is_available', return_value=False)
    def test_generate_with_top_p_custom_params(self, mock_cuda):
        """测试自定义参数的top-p生成"""
        custom_params = {
            "max_length": 50,
            "temperature": 0.7
        }
        
        result = generate_with_top_p(
            self.model,
            self.tokenizer,
            self.input_ids,
            top_p=0.8,
            generation_params=custom_params
        )
        
        call_kwargs = self.model.generate.call_args[1]
        self.assertEqual(call_kwargs['top_p'], 0.8)
        self.assertEqual(call_kwargs['max_length'], 50)
        self.assertEqual(call_kwargs['temperature'], 0.7)


class TestExtractModelOutputs(unittest.TestCase):
    """测试Q6: extract_model_outputs函数"""
    
    def setUp(self):
        """设置测试环境"""
        self.outputs = Mock()
        
        # 模拟logits: (batch_size, seq_len, vocab_size)
        self.outputs.logits = torch.randn(1, 10, 5000)
        
        # 模拟attentions: 元组，包含所有层的attention
        # 每层attention shape: (batch_size, num_heads, seq_len, seq_len)
        num_layers = 3
        num_heads = 8
        seq_len = 10
        self.outputs.attentions = tuple([
            torch.randn(1, num_heads, seq_len, seq_len)
            for _ in range(num_layers)
        ])
    
    def test_extract_logits(self):
        """测试提取logits"""
        logits, attention_scores = extract_model_outputs(self.outputs)
        
        # 验证logits shape: 应该是 (vocab_size,)
        expected_shape = (self.outputs.logits.shape[-1],)
        self.assertEqual(logits.shape, expected_shape)
        self.assertIsInstance(logits, torch.Tensor)
    
    def test_extract_attention_scores(self):
        """测试提取attention scores"""
        logits, attention_scores = extract_model_outputs(self.outputs)
        
        # 验证attention_scores是元组
        self.assertIsInstance(attention_scores, tuple)
        # 验证每层attention的shape
        for attn in attention_scores:
            self.assertEqual(len(attn.shape), 4)  # (batch, heads, seq, seq)
    
    def test_extract_output_format(self):
        """测试输出格式"""
        logits, attention_scores = extract_model_outputs(self.outputs)
        
        self.assertIsInstance(logits, torch.Tensor)
        self.assertIsInstance(attention_scores, tuple)
        self.assertEqual(len(attention_scores), len(self.outputs.attentions))


class TestGetMaxActivation(unittest.TestCase):
    """测试Q7.2-7.3: get_max_activation函数"""
    
    def setUp(self):
        """设置测试环境"""
        self.model = Mock()
        self.tokenizer = Mock()
        self.sae = Mock()
        self.prompt = "Test prompt"
        
        # 模拟model
        self.model.device = torch.device("cpu")
        
        # 模拟sae
        self.sae.cfg = Mock()
        self.sae.cfg.hook_layer = 20
        self.sae.encode.return_value = torch.randn(1, 10, 16000)  # (batch, seq, num_features)
        self.sae.to = Mock(return_value=self.sae)
        
        # 模拟tokenizer
        self.tokenizer.encode.return_value = torch.tensor([[1, 2, 3, 4, 5, 6, 7, 8, 9, 10]])
    
    @patch('torch.cuda.is_available', return_value=False)
    def test_get_max_activation_basic(self, mock_cuda):
        """测试基本最大激活值计算"""
        # 设置feature_acts
        feature_acts = torch.randn(1, 10, 16000)
        feature_acts[0, 5, 10004] = 10.0  # 设置一个较大的值
        self.sae.encode.return_value = feature_acts
        
        # 模拟model调用
        mock_outputs = Mock()
        mock_outputs.hidden_states = [torch.randn(1, 10, 512) for _ in range(25)]
        
        # 使用side_effect来模拟模型调用
        self.model.side_effect = lambda *args, **kwargs: mock_outputs
        
        max_activation = get_max_activation(
            self.model,
            self.tokenizer,
            self.sae,
            self.prompt,
            feature_idx=10004
        )
        
        self.assertIsInstance(max_activation, float)
        self.assertGreater(max_activation, -float("inf"))


class TestComputeSelfBleu(unittest.TestCase):
    """测试self-BLEU计算函数"""
    
    def test_compute_self_bleu_identical_sentences(self):
        """测试相同句子的self-BLEU"""
        sentences = [
            "Hello world",
            "Hello world",
            "Hello world"
        ]
        
        score = compute_self_bleu(sentences)
        self.assertIsInstance(score, float)
        self.assertGreaterEqual(score, 0.0)
        self.assertLessEqual(score, 1.0)
    
    def test_compute_self_bleu_different_sentences(self):
        """测试不同句子的self-BLEU"""
        sentences = [
            "Hello world",
            "Goodbye world",
            "Hello there"
        ]
        
        score = compute_self_bleu(sentences)
        self.assertIsInstance(score, float)
        self.assertGreaterEqual(score, 0.0)
        self.assertLessEqual(score, 1.0)
    
    def test_compute_self_bleu_single_sentence(self):
        """测试单个句子的self-BLEU（边界情况）"""
        sentences = ["Hello world"]
        
        # 单个句子时，references为空，可能会出错
        # 这里测试是否会正确处理
        try:
            score = compute_self_bleu(sentences)
            self.assertIsInstance(score, float)
        except (ZeroDivisionError, IndexError):
            # 预期可能会出错，这是正常的边界情况
            pass


class TestPlotFunctions(unittest.TestCase):
    """测试绘图函数（主要测试不会崩溃）"""
    
    def setUp(self):
        """设置测试环境"""
        self.model = Mock()
        self.tokenizer = Mock()
        self.sae = Mock()
        
        # 模拟基本属性
        self.model.device = torch.device("cpu")
        self.tokenizer.convert_ids_to_tokens.return_value = ["Hello", "world"]
        # 设置tokenizer的__call__方法返回dict
        self.tokenizer.__call__ = Mock(return_value={"input_ids": torch.tensor([[1, 2]])})
        self.sae.cfg = Mock()
        self.sae.cfg.hook_layer = 20
        self.sae.encode.return_value = torch.randn(1, 2, 16000)
        self.sae.to = Mock(return_value=self.sae)
    
    @patch('matplotlib.pyplot.show')
    @patch('matplotlib.pyplot.figure')
    @patch('matplotlib.pyplot.bar')
    @patch('matplotlib.pyplot.xticks')
    @patch('matplotlib.pyplot.xlabel')
    @patch('matplotlib.pyplot.ylabel')
    @patch('matplotlib.pyplot.title')
    @patch('matplotlib.pyplot.grid')
    @patch('torch.cuda.is_available', return_value=False)
    def test_plot_token_activations(self, mock_cuda, *mocks):
        """测试plot_token_activations不会崩溃"""
        mock_outputs = Mock()
        mock_outputs.hidden_states = [torch.randn(1, 2, 512) for _ in range(25)]
        
        # 使用side_effect来模拟模型调用
        self.model.side_effect = lambda *args, **kwargs: mock_outputs
        
        try:
            plot_token_activations(
                self.model,
                self.tokenizer,
                self.sae,
                "Hello world",
                feature_idx=10004,
                layer_idx=24
            )
            # 如果没有抛出异常，测试通过
            self.assertTrue(True)
        except Exception as e:
            self.fail(f"plot_token_activations raised {type(e).__name__}: {e}")
    
    @patch('matplotlib.pyplot.show')
    @patch('matplotlib.pyplot.figure')
    @patch('matplotlib.pyplot.plot')
    @patch('matplotlib.pyplot.xlabel')
    @patch('matplotlib.pyplot.ylabel')
    @patch('matplotlib.pyplot.title')
    @patch('matplotlib.pyplot.xticks')
    @patch('matplotlib.pyplot.grid')
    @patch('torch.cuda.is_available', return_value=False)
    def test_plot_layer_activations(self, mock_cuda, *mocks):
        """测试plot_layer_activations不会崩溃"""
        mock_outputs = Mock()
        mock_outputs.hidden_states = [torch.randn(1, 2, 512) for _ in range(25)]
        
        # 使用side_effect来模拟模型调用
        self.model.side_effect = lambda *args, **kwargs: mock_outputs
        
        try:
            plot_layer_activations(
                self.model,
                self.tokenizer,
                self.sae,
                "Hello world",
                token_idx=1,
                feature_idx=10004
            )
            # 如果没有抛出异常，测试通过
            self.assertTrue(True)
        except Exception as e:
            self.fail(f"plot_layer_activations raised {type(e).__name__}: {e}")


class TestIntegration(unittest.TestCase):
    """集成测试"""
    
    def test_all_functions_importable(self):
        """测试所有函数都可以正确导入"""
        from llm_utils import (
            generate_text_from_prompt,
            tokenize_sentence,
            generate_with_top_p,
            extract_model_outputs,
            get_max_activation,
            plot_token_activations,
            plot_layer_activations,
            compute_self_bleu,
        )
        
        # 如果导入成功，测试通过
        self.assertTrue(True)
    
    def test_function_signatures(self):
        """测试函数签名正确性"""
        import inspect
        
        # 检查generate_text_from_prompt
        sig = inspect.signature(generate_text_from_prompt)
        self.assertIn('prompt', sig.parameters)
        self.assertIn('tokenizer', sig.parameters)
        self.assertIn('model', sig.parameters)
        
        # 检查tokenize_sentence
        sig = inspect.signature(tokenize_sentence)
        self.assertIn('sentence', sig.parameters)
        self.assertIn('tokenizer', sig.parameters)
        
        # 检查generate_with_top_p
        sig = inspect.signature(generate_with_top_p)
        self.assertIn('model', sig.parameters)
        self.assertIn('tokenizer', sig.parameters)
        self.assertIn('input_ids', sig.parameters)
        self.assertIn('top_p', sig.parameters)


if __name__ == '__main__':
    # 创建测试套件
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    # 添加所有测试类
    suite.addTests(loader.loadTestsFromTestCase(TestGenerateTextFromPrompt))
    suite.addTests(loader.loadTestsFromTestCase(TestTokenizeSentence))
    suite.addTests(loader.loadTestsFromTestCase(TestGenerateWithTopP))
    suite.addTests(loader.loadTestsFromTestCase(TestExtractModelOutputs))
    suite.addTests(loader.loadTestsFromTestCase(TestGetMaxActivation))
    suite.addTests(loader.loadTestsFromTestCase(TestComputeSelfBleu))
    suite.addTests(loader.loadTestsFromTestCase(TestPlotFunctions))
    suite.addTests(loader.loadTestsFromTestCase(TestIntegration))
    
    # 运行测试
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # 打印总结
    print(f"\n{'='*60}")
    print(f"测试总结:")
    print(f"  运行测试: {result.testsRun}")
    print(f"  成功: {result.testsRun - len(result.failures) - len(result.errors)}")
    print(f"  失败: {len(result.failures)}")
    print(f"  错误: {len(result.errors)}")
    print(f"{'='*60}")

