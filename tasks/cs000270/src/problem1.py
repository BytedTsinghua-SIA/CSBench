import numpy as np
import scipy.linalg as sla
from timeit import default_timer as timer

def generate_data(seed=12345):
    rng = np.random.default_rng(seed)
    n   = int(5e3)
    m   = n+1
    A       = rng.standard_normal( (m,n) )
    xTrue   = np.ones(n)
    b       = A@xTrue
    return A, b, xTrue

def solve_problem_1():
    # Problem 1 Setup
    A, b, xTrue = generate_data()
    n = A.shape[1]

    print("Problem 1: Solving...")
    start = timer()

    # ==========================================
    # FILL IN YOUR METHOD HERE
    # Find x such that ||x - xTrue||_inf <= 10^-10
    # Expected time: < 10 seconds
    # ==========================================
    
    x = np.zeros(n) # Placeholder: Replace with your solver

    # ==========================================

    end = timer()
    
    elapsed = end - start
    print(f'Elapsed time is {elapsed:.5f} seconds')
    
    err = np.linalg.norm(x - xTrue, np.inf)
    print(f'   and l_inf error is {err:.2e}')
    
    if err <= 1e-10 and elapsed < 10.0:
        print("Problem 1: SUCCESS")
    else:
        print("Problem 1: FAILURE (Accuracy or Time constraint not met)")

if __name__ == "__main__":
    solve_problem_1()
