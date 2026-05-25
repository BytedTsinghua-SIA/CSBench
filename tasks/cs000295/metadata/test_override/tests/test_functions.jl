# Test functions for Python unit tests
# This file contains only the functions needed for testing, without plotting dependencies

using Test
using BenchmarkTools
using Polynomials
using PolynomialRoots

# ============================================================================
# Exercise 1: Summation Two Ways
# ============================================================================

"""
Calculate relative error between approximate and true values.
"""
function rela_error(x, x̂)
    return abs((x̂ - x) / x)
end

"""
Naive summation algorithm using a loop.
"""
function sum1(x)
    s = 0.0
    for i in 1:length(x)
        s += x[i]
    end
    return s
end

"""
Recursive summation algorithm that splits vector into two halves.
Base case: returns single element when length is 1.
Uses views to avoid excessive memory allocations.
"""
function sum2(x)
    n = length(x)
    if n == 1
        return x[1]
    end
    nnew = div(n, 2)
    return sum2(view(x, 1:nnew)) + sum2(view(x, nnew+1:n))
end

"""
Hybrid summation algorithm that uses recursion but switches to sum1
when vector is sufficiently short (length <= 2^10) to balance accuracy and performance.
"""
function sum3(x)
    n = length(x)
    if n <= 2^10
        return sum1(x)
    else
        nnew = div(n, 2)
        return sum3(view(x, 1:nnew)) + sum3(view(x, nnew+1:n))
    end
end

# ============================================================================
# Exercise 2: Conditioning of a Problem and Stability of an Algorithm
# ============================================================================

"""
Calculate the relative condition number κ_φ(x) for φ(x) = √(1+x) - 1.
κ_φ(x) = |x·φ'(x) / φ(x)| = (√(1+x) + 1) / (2√(1+x))
"""
function condition_number_phi(x)
    sqrt_1px = sqrt(1 + x)
    return (sqrt_1px + 1) / (2 * sqrt_1px)
end

"""
Naive algorithm: φ(x) = √(1+x) - 1
This is numerically unstable near x = 0 due to catastrophic cancellation.
"""
function naive_phi(x)
    return sqrt(x + 1) - 1
end

"""
Stable algorithm: φ(x) = x / (√(1+x) + 1)
This avoids catastrophic cancellation by algebraic manipulation.
"""
function stable_phi(x)
    return x / (sqrt(1 + x) + 1)
end

# ============================================================================
# Exercise 3: Conditioning of Polynomial Roots
# ============================================================================

"""
Calculate the condition number for finding a root r when the leading coefficient a_n is varied.
κ = |a_n · r^(n-1) / p'(r)|
"""
function condition_number_root(p::Polynomial, r)
    n = length(p) - 1
    a_n = p[end]  # leading coefficient
    p_prime = derivative(p)
    return abs(a_n * r^(n-1) / p_prime(r))
end

"""
Construct the Wilkinson polynomial: p(x) = (x-1)(x-2)...(x-20)
Uses BigInt for coefficient calculation to avoid overflow.
"""
function wilkinson_polynomial()
    p = one(Polynomial{BigInt})
    for i in 1:20
        p *= Polynomial([-BigInt(i), BigInt(1)])
    end
    # Convert to Float64 for root finding
    p_float = Polynomial([Float64(coeff) for coeff in p.coeffs])
    return p_float, p
end

# ============================================================================
# Exercise 4: Lagrange Interpolation
# ============================================================================

"""
Calculate the Lagrange cardinal function ℓ_k(x) that satisfies ℓ_k(t_i) = [i = k].
Operation count: O(n) for each evaluation, where n is the number of nodes.
"""
function lagrange_cardinal(t, x, k)
    n = length(t)
    result = 1.0
    for i in 1:n
        if i == k
            continue
        end
        result *= (x - t[i]) / (t[k] - t[i])
    end
    return result
end

"""
Calculate the Lagrange interpolant at point x using nodes t and data y.
Operation count: O(n^2) for each evaluation, where n is the number of nodes.
"""
function lagrange_interpolant(t, y, x)
    n = length(t)
    result = 0.0
    for k in 1:n
        result += y[k] * lagrange_cardinal(t, x, k)
    end
    return result
end

"""
Calculate Chebyshev points: t_i = cos(θ_i), where θ_i are equally-spaced angles between 0 and π.
"""
function chebyshev_points(N)
    θ = range(0, π, length=N+1)
    return cos.(θ)
end
