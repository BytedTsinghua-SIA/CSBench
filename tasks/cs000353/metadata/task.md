# Problem Set 1: Algorithm Analysis and Peak-Finding

## Background

This problem set is from MIT 6.006 Introduction to Algorithms (Fall 2011), taught by Professors Erik Demaine and Srini Devadas. The assignment focuses on asymptotic analysis, recurrence relations, and the peak-finding problem introduced in Lecture 1.

A peak in a matrix is defined as a location where its four neighbors (north, south, east, and west) have values less than or equal to the value of the peak. The problem set provides Python code with four different algorithms for solving the peak-finding problem, and students must analyze their correctness and efficiency.

## Core Tasks

### Problem 1-1: Asymptotic Practice [15 points]

Sort functions in increasing order of asymptotic (big-O) complexity for three groups:

- **Group 1**: Functions involving polynomial, logarithmic, and exponential terms
- **Group 2**: Functions involving exponential, binomial coefficients, and polynomial terms
- **Group 3**: Functions involving exponential and polynomial combinations

### Problem 1-2: Recurrence Relation Resolution [15 points]

Determine the correct asymptotic runtime for algorithms with given recurrence relations:

- **(a)** A recurrence with two parameters that divides both dimensions
- **(b)** A recurrence with two parameters that divides only one dimension
- **(c)** A recurrence involving two mutually recursive functions

### Problem 1-3: Peak-Finding Correctness [16 points]

Determine which of the four provided peak-finding algorithms (algorithm1, algorithm2, algorithm3, algorithm4) are correct. For each algorithm, answer whether it correctly finds a peak in the matrix.

### Problem 1-4: Peak-Finding Efficiency [16 points]

Determine the worst-case runtime complexity of each of the four peak-finding algorithms on a problem of size n×n. Choose from:
- Θ(log n)
- Θ(n)
- Θ(n log n)
- Θ(n log² n)
- Θ(n²)
- Θ(2ⁿ)

### Problem 1-5: Peak-Finding Proof [19 points]

Modify the provided proof of correctness for algorithm1 to construct a proof of correctness for the most efficient correct algorithm among algorithm2, algorithm3, and algorithm4.

The proof must demonstrate:
1. If the peak problem is not empty, the algorithm will always return a location
2. If the algorithm returns a location, it will be a peak in the original problem

### Problem 1-6: Peak-Finding Counterexamples [19 points]

For each incorrect algorithm identified in Problem 1-3, provide a Python file containing a counterexample (i.e., a matrix for which the algorithm returns a location that is not a peak).

## Key Learning Objectives

- Master asymptotic complexity analysis and function ordering
- Understand and solve recurrence relations
- Analyze algorithm correctness through formal proofs
- Evaluate algorithm efficiency through complexity analysis
- Construct counterexamples to demonstrate incorrect algorithms

