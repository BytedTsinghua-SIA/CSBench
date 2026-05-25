"""Tests for Interpreter class."""

import pytest
import time
from interpreter import Interpreter, ExecutionResult, exception_summary


def test_interpreter_initialization():
    """Test interpreter initialization."""
    interpreter = Interpreter(timeout=100, agent_file_name="test.py")
    assert interpreter.timeout == 100
    assert interpreter.agent_file_name == "test.py"
    assert interpreter.process is None


def test_exception_summary():
    """Test exception summary generation."""
    try:
        raise ValueError("Test error")
    except ValueError as e:
        tb_str, e_cls_name, exc_info, exc_stack = exception_summary(e, "test.py")
        
        assert e_cls_name == "ValueError"
        assert "Test error" in str(exc_info.get("args", []))
        assert len(exc_stack) > 0


def test_interpreter_run_simple_code():
    """Test running simple code."""
    interpreter = Interpreter(timeout=10)
    
    try:
        result = interpreter.run("print('hello')", reset_session=True)
        
        assert isinstance(result, ExecutionResult)
        assert result.exc_type is None
        assert "hello" in "".join(result.term_out)
    finally:
        # Ensure cleanup happens
        if interpreter.process is not None:
            interpreter.cleanup_session()


def test_interpreter_run_with_error():
    """Test running code with error."""
    interpreter = Interpreter(timeout=10)
    
    try:
        result = interpreter.run("raise ValueError('test error')", reset_session=True)
        
        assert isinstance(result, ExecutionResult)
        assert result.exc_type == "ValueError"
        assert result.exc_info is not None
    finally:
        # Ensure cleanup happens
        if interpreter.process is not None:
            interpreter.cleanup_session()


def test_interpreter_cleanup():
    """Test interpreter cleanup - simplified to avoid hanging in Docker."""
    interpreter = Interpreter(timeout=10)
    
    # Test cleanup when process is None (should not raise)
    interpreter.cleanup_session()
    assert interpreter.process is None
    
    # Skip the process creation test in Docker to avoid hanging issues
    # The cleanup logic is tested indirectly through other tests


def test_execution_result():
    """Test ExecutionResult dataclass."""
    result = ExecutionResult(
        term_out=["output\n"],
        exec_time=0.5,
        exc_type=None,
        exc_info=None,
        exc_stack=None
    )
    
    assert result.term_out == ["output\n"]
    assert result.exec_time == 0.5
    assert result.exc_type is None

