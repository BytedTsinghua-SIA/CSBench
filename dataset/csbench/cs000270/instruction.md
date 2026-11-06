## Background

Least squares problems are fundamental in machine learning and scientific computing. While basic solvers are readily available, handling large-scale or ill-conditioned problems efficiently requires a deeper understanding of numerical linear algebra.

This assignment challenges you to solve two specific least squares problems efficiently. We have constructed these problems with known ground truth (the all-ones vector) to allow for precise error checking.

## Problem Description

Your goal is to implement solvers for two distinct least squares scenarios.

For both problems, you must find an estimate $\hat{x}$ such that the infinity norm error relative to the true solution $x_{true}$ is small:
$$ \|\hat{x} - x_{true}\|_\infty \le 10^{-10} $$

### Problem 1: Nearly Square Matrix

In this problem, you are dealing with a matrix $A$ of size $m \times n$ where $n = 5000$ and $m = n + 1$. The matrix is generated from a standard normal distribution.

**Constraints:**
- Accuracy: $\|\hat{x} - x_{true}\|_\infty \le 10^{-10}$
- Time limit: Under 10 seconds

### Problem 2: Tall, Ill-Conditioned Matrix

In this problem, you are dealing with a matrix $A$ of size $m \times n$ where $n = 2000$ and $m = 10000$. The matrix is constructed by stacking two $m \times (n/2)$ matrices, where the second half is a slightly perturbed version of the first half. This structure introduces numerical challenges.

**Constraints:**
- Accuracy: $\|\hat{x} - x_{true}\|_\infty \le 10^{-10}$
- Time limit: Under 5 seconds

---

## Special reminders for this repository

- Do not use external libraries other than `numpy` and `scipy` unless absolutely necessary and standard in scientific Python environments.
- Ensure your solution is robust and reproducible (the random seed is fixed in the setup).
