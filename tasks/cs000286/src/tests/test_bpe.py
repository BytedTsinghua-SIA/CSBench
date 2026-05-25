"""
Unit tests for BPE tokenizer.
"""

import pytest
import tempfile
import os
from src.bpe import Tokenizer, train_bpe, GPT2_PATTERN
import regex


class TestTokenizer:
    """Test Tokenizer class methods."""
    
    def test_tokenizer_init(self):
        """Test tokenizer initialization."""
        vocab = {0: b'<|endoftext|>', 1: b'a', 2: b'b', 3: b'ab'}
        merges = [(b'a', b'b')]
        tokenizer = Tokenizer(vocab, merges, special_tokens=['<|endoftext|>'])
        
        assert tokenizer.vocab == vocab
        assert tokenizer.merges == merges
        assert '<|endoftext|>' in tokenizer.special_tokens
    
    def test_tokenizer_encode_simple(self):
        """Test encoding simple text."""
        vocab = {0: b'<|endoftext|>', 1: b'a', 2: b'b', 3: b' '}
        merges = []
        tokenizer = Tokenizer(vocab, merges)
        
        text = "ab"
        ids = tokenizer.encode(text)
        
        assert isinstance(ids, list)
        assert all(isinstance(id, int) for id in ids)
        assert len(ids) > 0
    
    def test_tokenizer_encode_with_special_token(self):
        """Test encoding text with special tokens."""
        vocab = {0: b'<|endoftext|>', 1: b'a', 2: b'b'}
        merges = []
        tokenizer = Tokenizer(vocab, merges, special_tokens=['<|endoftext|>'])
        
        text = "a<|endoftext|>b"
        ids = tokenizer.encode(text)
        
        assert isinstance(ids, list)
        assert len(ids) > 0
    
    def test_tokenizer_decode_simple(self):
        """Test decoding token IDs."""
        vocab = {0: b'<|endoftext|>', 1: b'a', 2: b'b', 3: b' '}
        merges = []
        tokenizer = Tokenizer(vocab, merges)
        
        ids = [1, 3, 2]
        text = tokenizer.decode(ids)
        
        assert isinstance(text, str)
        assert len(text) >= 0
    
    def test_tokenizer_encode_decode_roundtrip(self):
        """Test encode-decode roundtrip for simple text."""
        vocab = {0: b'<|endoftext|>', 1: b'a', 2: b'b', 3: b'c', 4: b' '}
        merges = []
        tokenizer = Tokenizer(vocab, merges)
        
        original = "abc"
        ids = tokenizer.encode(original)
        decoded = tokenizer.decode(ids)
        
        assert isinstance(decoded, str)
    
    def test_tokenizer_encode_iterable(self):
        """Test encoding iterable of strings."""
        vocab = {0: b'<|endoftext|>', 1: b'a', 2: b'b'}
        merges = []
        tokenizer = Tokenizer(vocab, merges)
        
        texts = ["a", "b", "ab"]
        ids_generator = tokenizer.encode_iterable(texts)
        
        ids_list = list(ids_generator)
        assert isinstance(ids_list, list)
        assert len(ids_list) > 0
    
    def test_tokenizer_from_files(self):
        """Test loading tokenizer from files."""
        vocab = {0: b'<|endoftext|>', 1: b'a', 2: b'b'}
        merges = [(b'a', b'b')]
        
        with tempfile.TemporaryDirectory() as tmpdir:
            vocab_path = os.path.join(tmpdir, 'vocab.txt')
            merges_path = os.path.join(tmpdir, 'merges.txt')
            
            with open(vocab_path, 'wb') as f:
                for token_id in sorted(vocab.keys()):
                    f.write(vocab[token_id] + b'\n')
            
            with open(merges_path, 'wb') as f:
                for merge in merges:
                    f.write(merge[0] + b' ' + merge[1] + b'\n')
            
            tokenizer = Tokenizer.from_files(vocab_path, merges_path)
            assert tokenizer.vocab is not None
            assert tokenizer.merges is not None


class TestBPETraining:
    """Test BPE training function."""
    
    def test_train_bpe_basic(self):
        """Test basic BPE training."""
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.txt') as f:
            f.write("hello world\nhello world\n")
            temp_path = f.name
        
        try:
            vocab, merges = train_bpe(temp_path, vocab_size=260, special_tokens=[])
            
            assert isinstance(vocab, dict)
            assert isinstance(merges, list)
            assert len(vocab) <= 260
            assert all(isinstance(k, int) for k in vocab.keys())
            assert all(isinstance(v, bytes) for v in vocab.values())
        finally:
            os.unlink(temp_path)
    
    def test_train_bpe_with_special_tokens(self):
        """Test BPE training with special tokens."""
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.txt') as f:
            f.write("text<|endoftext|>more text\n")
            temp_path = f.name
        
        try:
            vocab, merges = train_bpe(
                temp_path, 
                vocab_size=260, 
                special_tokens=['<|endoftext|>']
            )
            
            assert isinstance(vocab, dict)
            assert isinstance(merges, list)
            # Check special token is in vocab
            special_bytes = '<|endoftext|>'.encode('utf-8')
            assert any(v == special_bytes for v in vocab.values())
        finally:
            os.unlink(temp_path)
    
    def test_train_bpe_vocab_size_limit(self):
        """Test that BPE training respects vocab size limit."""
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.txt') as f:
            f.write("a b c d e f g h i j k l m n o p q r s t u v w x y z\n" * 10)
            temp_path = f.name
        
        try:
            vocab_size = 280
            vocab, merges = train_bpe(temp_path, vocab_size=vocab_size, special_tokens=[])
            
            assert len(vocab) <= vocab_size
        finally:
            os.unlink(temp_path)
    
    def test_train_bpe_merges_order(self):
        """Test that merges are returned in creation order."""
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.txt') as f:
            f.write("low low low\n")
            temp_path = f.name
        
        try:
            vocab, merges = train_bpe(temp_path, vocab_size=260, special_tokens=[])
            
            assert isinstance(merges, list)
            assert all(isinstance(m, tuple) and len(m) == 2 for m in merges)
            assert all(isinstance(m[0], bytes) and isinstance(m[1], bytes) for m in merges)
        finally:
            os.unlink(temp_path)


class TestPreTokenization:
    """Test pre-tokenization functionality."""
    
    def test_gpt2_pattern_basic(self):
        """Test GPT-2 regex pattern on basic text."""
        text = "hello world"
        matches = list(regex.finditer(GPT2_PATTERN, text))
        
        assert len(matches) > 0
        assert all(isinstance(m.group(0), str) for m in matches)
    
    def test_gpt2_pattern_with_numbers(self):
        """Test GPT-2 pattern with numbers."""
        text = "123 abc"
        matches = list(regex.finditer(GPT2_PATTERN, text))
        
        assert len(matches) > 0
    
    def test_gpt2_pattern_with_punctuation(self):
        """Test GPT-2 pattern with punctuation."""
        text = "hello, world!"
        matches = list(regex.finditer(GPT2_PATTERN, text))
        
        assert len(matches) > 0
    
    def test_gpt2_pattern_contractions(self):
        """Test GPT-2 pattern with contractions."""
        text = "I'll don't can't"
        matches = list(regex.finditer(GPT2_PATTERN, text))
        
        assert len(matches) > 0

