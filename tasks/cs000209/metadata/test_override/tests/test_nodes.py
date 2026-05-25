"""Tests for Node class."""

import pytest
from nodes import Node
from interpreter import ExecutionResult


def test_node_creation():
    """Test basic node creation."""
    node = Node(code="print('hello')", plan="Test plan")
    assert node.code == "print('hello')"
    assert node.plan == "Test plan"
    assert node.id is not None
    assert node.parent is None
    assert len(node.children) == 0


def test_node_parent_child():
    """Test parent-child relationships."""
    parent = Node(code="x = 1")
    child = Node(code="y = 2", parent=parent)
    
    assert child.parent == parent
    assert child in parent.children
    assert child.stage_name == "improve"  # Parent is not buggy


def test_node_stage_name():
    """Test stage name property."""
    root = Node(code="x = 1")
    assert root.stage_name == "draft"
    
    # Child of non-buggy parent
    child1 = Node(code="y = 2", parent=root)
    assert child1.stage_name == "improve"
    
    # Child of buggy parent
    root.is_buggy = True
    child2 = Node(code="z = 3", parent=root)
    assert child2.stage_name == "debug"


def test_node_absorb_exec_result():
    """Test absorbing execution results."""
    node = Node(code="print('hello')")
    exec_result = ExecutionResult(
        term_out=["hello\n"],
        exec_time=0.1,
        exc_type=None,
        exc_info=None,
        exc_stack=None
    )
    
    node.absorb_exec_result(exec_result)
    assert node.exec_time == 0.1
    assert node.exc_type is None
    assert node._term_out == ["hello\n"]


def test_node_is_leaf():
    """Test leaf node detection."""
    parent = Node(code="x = 1")
    assert parent.is_leaf
    
    child = Node(code="y = 2", parent=parent)
    assert not parent.is_leaf
    assert child.is_leaf


def test_node_debug_depth():
    """Test debug depth calculation."""
    root = Node(code="x = 1")
    root.is_buggy = True
    
    child1 = Node(code="y = 2", parent=root)
    assert child1.debug_depth == 1
    
    child1.is_buggy = True
    child2 = Node(code="z = 3", parent=child1)
    assert child2.debug_depth == 2

