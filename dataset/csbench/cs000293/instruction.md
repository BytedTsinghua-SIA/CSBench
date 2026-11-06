# MIT 18.330 Problem Set 2 (Spring 2020)

**Course:** MIT 18.330 - Introduction to Numerical Analysis  
**Submission Deadline:** 11:59pm on Monday, February 17

---

## Overview

This problem set focuses on **root-finding algorithms** and **numerical methods** using Julia. The exercises cover fixed-point iteration, Newton's method, polynomial root-finding, and the Aberth method.

---

## Exercise 1: Fixed-Point Iteration

Find the roots of the function:

$$f(\alpha, x) = x^3 - \alpha x + \sqrt{2}$$

using fixed-point iterations.

### Tasks:
1. **Define and visualize** the Julia function for $f$; create an interactive visualization as $\alpha$ changes (fix plot limits).
2. **Analyze root count**: Determine the approximate value of $\alpha$ where the number of real roots changes. How many real roots exist?
3. **Locate roots**: When $\alpha = 2.5$, approximately where are the roots? Fix $\alpha$ to this value for subsequent tasks.
4. **Plot** the function $g(x) = x + f(\alpha, x)$ and $y = x$. Determine which root can be calculated by iterating $g$. Fix an initial condition and demonstrate convergence.
5. **Rate of convergence**: What is the rate of convergence to that root?
6. **Initial condition analysis**: What happens with initial condition $x = 1.1$? Why?
7. **Cobweb diagram**: Draw a cobweb diagram to illustrate this behavior.
8. **Alternative iterations**: Find fixed-point iterations $g$ that converge to the other two roots using:
   - Algebraic rearrangement of $f(\alpha, x) = 0$
   - Generalized function $g(c, x) := x + cf(x)$ with interactive plot as $c$ varies
9. **(Extra credit)** Find the critical value $\alpha_c$ where the number of roots changes (bifurcation point). What is the relationship between roots at $\alpha_c$?

---

## Exercise 2: Newton's Method

Find the roots of $f(\alpha, x)$ from Exercise 1 using Newton's method.

### Tasks:
1. **Define** the Julia function $f'(\alpha, x)$.
2. **Implement Newton's method** as a function that returns the sequence of iterates.
3. **Demonstrate convergence** to the two roots found in Exercise 1 with appropriate initial conditions.
4. **Visualize convergence**: Show how the result changes as the initial condition changes on the interval $[-10, 10]$, indicating which root the iteration converges to.
5. **Fractal basin of attraction**: Use Newton's method in the complex plane (with $z \in \mathbb{C}$) and color the initial point based on which root it converges to. Choose appropriate color for non-convergence cases.
6. **Julia set** (Extra credit): Make a movie of how the Julia set changes as $\alpha$ varies from 0 to 10.

---

## Exercise 3: Wilkinson's Polynomial

Consider Wilkinson's polynomial:

$$W(x) = \prod_{i=1}^{20}(x - i) = (x-1)(x-2)\cdots(x-20)$$

### Tasks:
1. **Expand** Wilkinson's polynomial using `Polynomials.jl`.
2. **Find roots** using `roots` function from `Polynomials.jl`.
3. **Plot roots**: Plot the roots in the complex plane (real part vs imaginary part). What do you observe?
4. **Implement Newton's method** for polynomials and test on Wilkinson's polynomial.
5. **Compare** the two sets of roots.
6. **Root sensitivity**: The polynomial $p(x) = x^n$ has a root of multiplicity $n$ at the origin. What is the sensitivity of the roots to changes in coefficients?

---

## Exercise 4: Aberth Method

The Aberth method calculates **all roots of a polynomial simultaneously**.

Given estimates $(z_k)$ for all roots of a polynomial, the new estimate is:

$$z_k = z_k - w_k$$

where:

$$w_k = \frac{\frac{p(z_k)}{p'(z_k)}}{1 - \frac{p(z_k)}{p'(z_k)} \cdot \sum_{j \neq k} \frac{1}{z_k - z_j}}$$

### Cauchy's Bounds

For polynomial $p(x) = a_0 + a_1x + \cdots + a_nx^n$:

**Upper bound:**
$$U = 1 + \max\left(\left|\frac{a_{n-1}}{a_n}\right|, \left|\frac{a_{n-2}}{a_n}\right|, \ldots, \left|\frac{a_0}{a_n}\right|\right)$$

**Lower bound:**
$$L = \frac{1}{1 + \max\left\{\left|\frac{a_n}{a_0}\right|, \left|\frac{a_{n-1}}{a_0}\right|, \ldots, \left|\frac{a_1}{a_0}\right|\right\}}$$

### Tasks:
1. **Implement `poly_bounds`**: Function that takes a Polynomial and returns $L$ and $U$.
2. **Implement `initialize_points`**: Generate suitable starting points by:
   - Sampling $\rho$ from uniform distribution over $[L, U]$
   - Sampling $\theta$ from uniform distribution over $[0, 2\pi]$
   - Calculating $z = \rho e^{i\theta}$
   - *Hint*: Write a `uniform(a, b)` function using `rand()`.
3. **Implement Aberth method**: Takes polynomial $p$ and initial points from `initialize_points`. Terminate after a certain number of iterations or when tolerance is met. Test on polynomials from previous exercises.
4. **Interactive visualization**: Visualize progress over time on random polynomials of degree 10 or 20.
5. **Order of convergence**: Find numerically the order of convergence of the method.
6. **Multiple roots**: Test on polynomials with multiple roots, such as $(x^2 + 1)^3$. What happens?

---

## Implementation Requirements

- **Language:** Julia
- **Visualization:** Interactive plots with adjustable parameters
- **Documentation:** Clear code comments and explanations
- **Testing:** Test all functions with appropriate test cases

---

## Deliverables

1. Julia code for all exercises
2. Interactive visualizations
3. Cobweb diagrams
4. Fractal basin of attraction plots
5. Analysis and explanations for each task
