# Counterexample for Algorithm 3
# This matrix causes Algorithm 3 to return a location that is not a peak
# Algorithm 3 divides both dimensions and tracks bestSeen
# This matrix exploits a flaw in how Algorithm 3 handles bestSeen

problemMatrix = [
    [1, 2, 3, 4],
    [2, 5, 6, 5],
    [3, 6, 7, 6],
    [4, 5, 6, 5]
]

# Note: This is a template. The actual counterexample depends on
# the specific bug in Algorithm 3's implementation.
# Algorithm 3 may incorrectly handle the bestSeen variable when
# recursing into subproblems, potentially returning a location
# that was the best in a subproblem but not a peak in the original.

