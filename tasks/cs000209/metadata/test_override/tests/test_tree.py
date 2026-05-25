"""Tests for Journal (tree) class."""

import pytest
from tree import Journal
from nodes import Node


def test_journal_creation():
    """Test journal creation."""
    journal = Journal()
    assert len(journal) == 0
    assert len(journal.nodes) == 0


def test_journal_append():
    """Test appending nodes to journal."""
    journal = Journal()
    node1 = Node(code="x = 1")
    node2 = Node(code="y = 2")
    
    journal.append(node1)
    assert len(journal) == 1
    assert node1.step == 0
    
    journal.append(node2)
    assert len(journal) == 2
    assert node2.step == 1


def test_journal_draft_nodes():
    """Test draft nodes property."""
    journal = Journal()
    node1 = Node(code="x = 1")
    node2 = Node(code="y = 2", parent=node1)
    
    journal.append(node1)
    journal.append(node2)
    
    drafts = journal.draft_nodes
    assert len(drafts) == 1
    assert node1 in drafts
    assert node2 not in drafts


def test_journal_buggy_nodes():
    """Test buggy nodes property."""
    journal = Journal()
    node1 = Node(code="x = 1", is_buggy=False)
    node2 = Node(code="y = 2", is_buggy=True)
    
    journal.append(node1)
    journal.append(node2)
    
    buggy = journal.buggy_nodes
    assert len(buggy) == 1
    assert node2 in buggy
    assert node1 not in buggy


def test_journal_good_nodes():
    """Test good nodes property."""
    journal = Journal()
    node1 = Node(code="x = 1", is_buggy=False)
    node2 = Node(code="y = 2", is_buggy=True)
    
    journal.append(node1)
    journal.append(node2)
    
    good = journal.good_nodes
    assert len(good) == 1
    assert node1 in good
    assert node2 not in good


def test_journal_get_best_node():
    """Test getting best node."""
    journal = Journal()
    node1 = Node(code="x = 1", is_buggy=False, metric=0.5)
    node2 = Node(code="y = 2", is_buggy=False, metric=0.3)
    node3 = Node(code="z = 3", is_buggy=False, metric=0.7)
    
    journal.append(node1)
    journal.append(node2)
    journal.append(node3)
    
    best = journal.get_best_node(only_good=True)
    assert best == node2  # Lowest metric
    
    # Test with only_good=False
    node4 = Node(code="w = 4", is_buggy=True, metric=0.1)
    journal.append(node4)
    best_all = journal.get_best_node(only_good=False)
    assert best_all == node4


def test_journal_get_best_node_no_nodes():
    """Test getting best node when no nodes exist."""
    journal = Journal()
    best = journal.get_best_node(only_good=True)
    assert best is None


def test_journal_generate_summary():
    """Test summary generation."""
    journal = Journal()
    node1 = Node(
        code="x = 1",
        plan="Test plan",
        analysis="Good results",
        metric=0.5,
        is_buggy=False
    )
    journal.append(node1)
    
    summary = journal.generate_summary()
    assert "Test plan" in summary
    assert "Good results" in summary
    assert "0.5" in summary
    
    summary_with_code = journal.generate_summary(include_code=True)
    assert "x = 1" in summary_with_code

