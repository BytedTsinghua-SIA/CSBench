"""Tests for Agent class."""

import pytest
from unittest.mock import Mock, MagicMock, patch
from agent import Agent
from tree import Journal
from nodes import Node
from config import Config
from interpreter import ExecutionResult


@pytest.fixture
def mock_llm_model():
    """Create a mock LLM model."""
    model = Mock()
    model.create_chat_completion.return_value = {
        "choices": [{
            "message": {
                "content": "Here's a plan:\n\n```python\nprint('hello')\n```"
            }
        }]
    }
    return model


@pytest.fixture
def sample_config():
    """Create a sample configuration."""
    return Config({
        "task_goal": "Test task",
        "data_dir": "/test/data",
        "agent": {
            "steps": 5,
            "search": {
                "debug_prob": 0.5,
                "num_drafts": 1
            }
        }
    })


@pytest.fixture
def sample_journal():
    """Create a sample journal."""
    return Journal()


def test_agent_initialization(sample_config, sample_journal, mock_llm_model):
    """Test agent initialization."""
    agent = Agent(sample_config, sample_journal, mock_llm_model)
    assert agent.cfg == sample_config
    assert agent.journal == sample_journal
    assert agent.llm_model == mock_llm_model
    assert agent.data_preview is None


def test_search_policy_draft(sample_config, sample_journal, mock_llm_model):
    """Test search policy returns None for drafting."""
    agent = Agent(sample_config, sample_journal, mock_llm_model)
    
    # When no drafts exist, should return None
    result = agent.search_policy()
    assert result is None


def test_search_policy_debug(sample_config, sample_journal, mock_llm_model):
    """Test search policy for debugging."""
    agent = Agent(sample_config, sample_journal, mock_llm_model)
    
    # Add a buggy node
    buggy_node = Node(code="buggy code", is_buggy=True)
    sample_journal.append(buggy_node)
    
    # Mock random to always choose debug
    with patch('random.random', return_value=0.1):  # Less than debug_prob
        result = agent.search_policy()
        assert result == buggy_node


def test_plan_and_code_query(sample_config, sample_journal, mock_llm_model):
    """Test plan and code query extraction."""
    agent = Agent(sample_config, sample_journal, mock_llm_model)
    
    plan, code = agent.plan_and_code_query(
        system_message="You are a helpful assistant",
        user_message="Write some code"
    )
    
    assert isinstance(plan, str)
    assert isinstance(code, str)
    assert "print" in code.lower() or len(code) > 0


@patch('agent.data_preview_generate')
def test_draft(mock_preview, sample_config, sample_journal, mock_llm_model):
    """Test draft generation."""
    mock_preview.return_value = "Data preview"
    agent = Agent(sample_config, sample_journal, mock_llm_model)
    agent.data_preview = "Data preview"
    
    node = agent._draft()
    
    assert isinstance(node, Node)
    assert node.code is not None
    assert node.plan is not None
    assert node.parent is None


def test_improve(sample_config, sample_journal, mock_llm_model):
    """Test solution improvement."""
    agent = Agent(sample_config, sample_journal, mock_llm_model)
    agent.data_preview = "Data preview"
    
    parent_node = Node(code="x = 1", is_buggy=False, metric=0.5)
    sample_journal.append(parent_node)
    
    node = agent._improve(parent_node)
    
    assert isinstance(node, Node)
    assert node.parent == parent_node
    assert node.stage_name == "improve"


def test_debug(sample_config, sample_journal, mock_llm_model):
    """Test debugging."""
    agent = Agent(sample_config, sample_journal, mock_llm_model)
    agent.data_preview = "Data preview"
    
    parent_node = Node(
        code="buggy code",
        is_buggy=True,
        exc_type="ValueError",
        _term_out=["Error message"]
    )
    
    node = agent._debug(parent_node)
    
    assert isinstance(node, Node)
    assert node.parent == parent_node
    assert node.stage_name == "debug"


def test_parse_exec_result(sample_config, sample_journal, mock_llm_model):
    """Test parsing execution results."""
    # Mock LLM response with MSE
    mock_llm_model.create_chat_completion.return_value = {
        "choices": [{
            "message": {
                "content": "The code executed successfully. MSE: 0.25. The model performed well."
            }
        }]
    }
    
    agent = Agent(sample_config, sample_journal, mock_llm_model)
    
    node = Node(code="print('test')")
    exec_result = ExecutionResult(
        term_out=["test\n"],
        exec_time=0.1,
        exc_type=None,
        exc_info=None,
        exc_stack=None
    )
    
    agent.parse_exec_result(node, exec_result)
    
    assert node.exec_time == 0.1
    assert node.analysis is not None
    # Should extract metric from response
    assert node.metric is not None or node.metric == 0.25


def test_parse_exec_result_with_exception(sample_config, sample_journal, mock_llm_model):
    """Test parsing execution results with exception."""
    agent = Agent(sample_config, sample_journal, mock_llm_model)
    
    node = Node(code="buggy code")
    exec_result = ExecutionResult(
        term_out=["Traceback...\n"],
        exec_time=0.1,
        exc_type="ValueError",
        exc_info={"args": ["test error"]},
        exc_stack=[("file.py", 1, "func", "code")]
    )
    
    agent.parse_exec_result(node, exec_result)
    
    assert node.exc_type == "ValueError"
    assert node.is_buggy is True  # Should be buggy due to exception

