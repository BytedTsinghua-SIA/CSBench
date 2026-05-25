import subprocess
from pathlib import Path
import re
import sys
import os
import numpy as np

# Add parent directory to path to import problem2
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from problem2 import generate_data

def test_data_generation_structure():
    """Verify the structure of the generated matrix and vectors."""
    A, b, xTrue = generate_data()
    n = int(2e3)
    m = int(1e4)
    
    assert A.shape == (m, n)
    assert b.shape == (m,)
    assert xTrue.shape == (n,)
    assert np.all(xTrue == 1.0)
    
    # Check consistency b = Ax
    assert np.allclose(A @ xTrue, b)

def test_ill_conditioned_structure():
    """Verify the ill-conditioned structure of the matrix."""
    A, b, xTrue = generate_data()
    m, n = A.shape
    n2 = n // 2
    
    # The matrix is constructed as [A_base, A_base + noise]
    # So the first n/2 columns should be close to the second n/2 columns
    A1 = A[:, :n2]
    A2 = A[:, n2:]
    
    diff = A1 - A2
    # The noise magnitude was 1e-4
    # Check that differences are small but non-zero
    assert np.all(np.abs(diff) < 1.0)
    assert np.any(np.abs(diff) > 0)

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

def test_problem2_success():
    cwd = Path(__file__).resolve().parent.parent
    script_path = cwd / "problem2.py"
    
    assert script_path.exists(), f"Missing file: {script_path}"

    result = subprocess.run(
        ["python3", str(script_path)],
        capture_output=True,
        text=True,
        timeout=6  # Slightly more than the 5s constraint to catch timeout failures gracefully
    )

    output = result.stdout
    print(output) # Print output for debugging visibility
    
    assert result.returncode == 0, f"Script failed with exit code {result.returncode}\nStderr: {result.stderr}"
    assert "Problem 2: SUCCESS" in output, (
        "Expected 'Problem 2: SUCCESS' in output.\n"
        f"Output:\n{output}"
    )
