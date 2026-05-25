"""Tests for text processing utilities."""

import pytest
from text_processing import (
    wrap_code,
    is_valid_python_script,
    extract_code,
    extract_text_up_to_code,
    trim_long_string,
    extract_jsons
)


def test_wrap_code():
    """Test code wrapping function."""
    code = "print('hello')"
    result = wrap_code(code)
    assert "```python" in result
    assert code in result
    assert result.endswith("```")
    
    result_custom = wrap_code(code, lang="javascript")
    assert "```javascript" in result_custom


def test_is_valid_python_script():
    """Test Python script validation."""
    assert is_valid_python_script("print('hello')")
    assert is_valid_python_script("x = 1 + 2")
    assert not is_valid_python_script("print('hello'")  # Missing closing quote
    assert not is_valid_python_script("x = ")  # Incomplete


def test_extract_code():
    """Test code extraction from text."""
    text = "Here's some code:\n```python\nprint('hello')\n```"
    code = extract_code(text)
    assert "print('hello')" in code
    
    # Test without backticks
    text2 = "print('hello')"
    code2 = extract_code(text2)
    assert "print('hello')" in code2
    
    # Test multiple code blocks
    text3 = "```python\nx = 1\n```\n```python\ny = 2\n```"
    code3 = extract_code(text3)
    assert "x = 1" in code3
    assert "y = 2" in code3


def test_extract_text_up_to_code():
    """Test text extraction before code blocks."""
    text = "This is some text.\n```python\ncode here\n```"
    result = extract_text_up_to_code(text)
    assert "This is some text" in result
    assert "code here" not in result
    
    text_no_code = "Just text, no code"
    result2 = extract_text_up_to_code(text_no_code)
    assert result2 == ""


def test_trim_long_string():
    """Test string trimming function."""
    short_string = "short"
    assert trim_long_string(short_string) == short_string
    
    # Create a long string
    long_string = "a" * 10000
    result = trim_long_string(long_string, threshold=5100, k=2500)
    assert len(result) < len(long_string)
    assert "truncated" in result  # Check for "truncated" (actual format is "... [X characters truncated] ...")
    assert long_string[:2500] in result
    assert long_string[-2500:] in result


def test_extract_jsons():
    """Test JSON extraction from text."""
    text = 'Some text {"key": "value"} more text'
    jsons = extract_jsons(text)
    assert len(jsons) == 1
    assert jsons[0]["key"] == "value"
    
    text_multiple = '{"a": 1} and {"b": 2}'
    jsons2 = extract_jsons(text_multiple)
    assert len(jsons2) == 2

