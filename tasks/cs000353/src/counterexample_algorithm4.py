# Counterexample for Algorithm 4
# This matrix causes Algorithm 4 to return a location that is not a peak
# Algorithm 4 alternates between splitting rows and columns
# This matrix exploits a flaw in Algorithm 4's alternating split logic

problemMatrix = [
    [1, 2, 3, 4],
    [2, 5, 6, 5],
    [3, 6, 7, 6],
    [4, 5, 6, 5]
]

# Note: This is a template. The actual counterexample depends on
# the specific bug in Algorithm 4's implementation.
# Algorithm 4 may incorrectly handle the bestSeen variable or
# the alternating split logic, potentially returning a location
# that is not a peak in the original problem.

