# 18.330 Problem Set 4

## Background

This problem set explores fundamental concepts in numerical analysis, focusing on numerical errors, algorithm stability, and interpolation methods. The exercises demonstrate how seemingly simple computational tasks can have significant numerical accuracy and performance implications, and how different algorithmic approaches can lead to vastly different results.

## Core Tasks

### Exercise 1: Summation Two Ways

Compare two different approaches to summing a vector of numbers and analyze their numerical accuracy and computational performance.

**Tasks:**
1. Implement a naive summation algorithm `sum1` that sums vector elements using a loop.
2. Implement a recursive summation algorithm `sum2` that splits the vector into two halves and recursively sums each half. The base case returns the single element when the vector length is 1. Use views to avoid excessive memory allocations.
3. Calculate relative errors of `sum1` and `sum2` compared to the true value (using `sum(big.(x))`) for vector lengths from $2^5$ to $2^{20}$. Plot relative error vs. length.
4. Benchmark both functions using `@belapsed` and plot run times as a function of length.
5. Implement a hybrid function `sum3` that uses recursion but switches to `sum1` when the vector is sufficiently short (e.g., length $\leq 2^{10}$) to balance accuracy and performance.
6. Calculate relative errors and run times for `sum3` and the built-in Julia `sum` function, and add them to the previous plots.

**Learning Objectives:**
- Understand how different summation algorithms affect numerical accuracy
- Recognize the trade-off between accuracy and performance
- Learn the importance of algorithm design for numerical stability

### Exercise 2: Conditioning of a Problem and Stability of an Algorithm

Analyze the numerical stability of computing $\phi(x) = \sqrt{1 + x} - 1$ near $x = 0$.

**Tasks:**
1. Calculate the relative condition number $\kappa_\phi(x)$ for the problem.
2. Determine whether the problem is well-conditioned near $x = 0$.
3. Analyze the obvious algorithm by breaking it into steps and calculating the condition number of each step. Identify the problematic step.
4. Find an alternative algorithm using algebraic manipulation that is numerically stable.
5. Implement both the naive and stable algorithms. Calculate relative errors compared to `ϕ(big(x))` for decreasing values of $x$ approaching 0. Plot the errors on the same axes.

**Learning Objectives:**
- Understand the difference between problem conditioning and algorithm stability
- Learn to identify numerical instability in algorithms
- Practice deriving stable alternative formulations

### Exercise 3: Conditioning of Polynomial Roots

Investigate the conditioning of polynomial root finding, using the famous Wilkinson polynomial as a case study.

**Tasks:**
1. Show that the condition number of finding a root $r$ when the leading coefficient $a_n$ is varied is $\kappa = \left| \frac{a_n r^{n-1}}{p'(r)} \right|$.
2. Construct the Wilkinson polynomial $p(x) = (x - 1)(x - 2) \cdots (x - 20)$ and calculate its coefficients using `Int128` or `BigInt`.
3. Calculate the condition number of each root. Identify which roots are well-conditioned and which are ill-conditioned.
4. Use the `roots` function to calculate the roots. Perturb a single coefficient by `randn()*2.0^(-23)` and plot the roots. Repeat 50 times to visualize the instability. Compare with the condition numbers from step 3.

**Learning Objectives:**
- Understand how polynomial root finding can be ill-conditioned
- Learn to calculate condition numbers for root finding problems
- Visualize the effect of small perturbations on polynomial roots

### Exercise 4: Lagrange Interpolation

Implement and analyze Lagrange interpolation, including the Runge phenomenon and Chebyshev points.

**Tasks:**
1. Write a function to calculate the Lagrange cardinal functions $\ell_k(x)$ that satisfy $\ell_k(t_i) = [i = k]$. The function should take a vector `t`, a value `x`, and an index `k`. Determine the operation count.
2. Write a function to calculate the Lagrange interpolant at nodes $t_i$ with data $y_i$ at point $x$ using the cardinal functions. Determine the operation count.
3. Find the Lagrange interpolant to $\exp(x)$ sampled at $N + 1$ equally spaced points in $[-1, 1]$. Plot the interpolant for $N = 10$ along with $\exp(x)$ and the interpolation points.
4. Calculate the maximum error between the interpolant and $\exp(x)$ by sampling at 100 points. Analyze how the error varies with the degree of the interpolant.
5. Consider $f(x) = \frac{1}{1 + 25x^2}$ on $[-1, 1]$. Investigate what happens as the number of equally-spaced points increases. Create an interactive visualization. This demonstrates the **Runge phenomenon**.
6. Instead, interpolate at **Chebyshev points** $t_i = \cos(\theta_i)$, where $\theta_i$ are equally-spaced angles between $0$ and $\pi$. Create another interactive visualization. Analyze the rate of convergence numerically. This demonstrates **spectral convergence**.

**Learning Objectives:**
- Implement Lagrange interpolation from scratch
- Understand the Runge phenomenon and its causes
- Learn about Chebyshev points and their advantages
- Analyze convergence rates for different interpolation schemes

## Technical Requirements

- Use Julia programming language
- Required packages: `Test`, `Plots`, `BenchmarkTools`, `Polynomials`, `PolynomialRoots`
- Use `big` precision for true value calculations
- Use views in recursive implementations to avoid excessive memory allocations
- Create appropriate visualizations for error analysis and convergence studies
