import subprocess
from pathlib import Path
import pytest

# Helper function to run cargo test
def run_cargo_test(test_name, is_doc=False):
    # Determine the project root directory (CS000337_before/src)
    # This file is at CS000337_before/src/tests/test_phases.py
    cwd = Path(__file__).resolve().parent.parent
    
    arg = "--doc" if is_doc else "--test"
    cmd = f"cargo test {arg} {test_name}"
    
    print(f"Running command: {cmd} in {cwd}")
    
    result = subprocess.run(
        cmd,
        cwd=str(cwd),
        shell=True,
        check=False,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
    )
    
    assert result.returncode == 0, (
        f"Cargo test failed for {test_name}.\n"
        f"Command: {cmd}\n"
        f"Exit code: {result.returncode}\n"
        f"--- output ---\n{result.stdout}\n--------------\n"
    )

def test_phase1_cache():
    """Test Phase 1: Cache"""
    run_cargo_test("cache")

def test_phase1_tcp():
    """Test Phase 1: TCP"""
    run_cargo_test("tcp")

def test_phase1_thread_pool():
    """Test Phase 1: Thread Pool"""
    run_cargo_test("thread_pool")

def test_phase2_linked_list():
    """Test Phase 2: Doubly Linked List"""
    run_cargo_test("linked_list")

def test_phase3_list_set():
    """Test Phase 3: List Set (includes fine_grained and optimistic_fine_grained)"""
    run_cargo_test("list_set")

def test_phase4_arc_test():
    """Test Phase 4: Core Arc (Unit Tests)"""
    run_cargo_test("arc")

def test_phase4_arc_doc():
    """Test Phase 4: Core Arc (Doc Tests)"""
    run_cargo_test("arc", is_doc=True)

def test_phase5_hazard_pointer():
    """Test Phase 5: Hazard Pointers"""
    run_cargo_test("hazard_pointer")

def test_phase6_growable_array():
    """Test Phase 6: Growable Array (Hash Table Part 1)"""
    run_cargo_test("growable_array")

def test_phase6_split_ordered_list():
    """Test Phase 6: Split Ordered List (Hash Table Part 2)"""
    run_cargo_test("split_ordered_list")

def test_phase7_boc():
    """Test Phase 7: Behaviour-Oriented Concurrency"""
    run_cargo_test("boc")
