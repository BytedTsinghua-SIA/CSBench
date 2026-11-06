import subprocess
from pathlib import Path
import re
import sys
import os
import numpy as np

# Add parent directory to path to import problem1
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from problem1 import generate_data

def test_data_generation_structure():
    """Verify the structure of the generated matrix and vectors."""
    A, b, xTrue = generate_data()
    n = int(5e3)
    m = n + 1
    
    assert A.shape == (m, n)
    assert b.shape == (m,)
    assert xTrue.shape == (n,)
    assert np.all(xTrue == 1.0)
    
    # Check consistency b = Ax
    assert np.allclose(A @ xTrue, b)

def test_random_seed_fixity():
    """Verify that the random seed produces deterministic results."""
    seed = 42
    A1, b1, x1 = generate_data(seed=seed)
    A2, b2, x2 = generate_data(seed=seed)
    
    assert np.array_equal(A1, A2)
    assert np.array_equal(b1, b2)
    assert np.array_equal(x1, x2)
    
    # Verify different seed produces different results
    A3, _, _ = generate_data(seed=seed+1)
    assert not np.array_equal(A1, A3)

def test_problem1_success():
    cwd = Path(__file__).resolve().parent.parent
    script_path = cwd / "problem1.py"
    
    assert script_path.exists(), f"Missing file: {script_path}"

    result = subprocess.run(
        ["python3", str(script_path)],
        capture_output=True,
        text=True,
        timeout=11  # Slightly more than the 10s constraint to catch timeout failures gracefully
    )

    output = result.stdout
    print(output) # Print output for debugging visibility
    
    assert result.returncode == 0, f"Script failed with exit code {result.returncode}\nStderr: {result.stderr}"
    assert "Problem 1: SUCCESS" in output, (
        "Expected 'Problem 1: SUCCESS' in output.\n"
        f"Output:\n{output}"
    )
