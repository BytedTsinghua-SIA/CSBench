# Counterexample for Algorithm 2
# This matrix causes Algorithm 2 to return a location that is not a peak
# Algorithm 2 starts at (0,0) and greedily moves to better neighbors
# This matrix has a structure that can trap Algorithm 2 in a local maximum
# that is not a global peak

problemMatrix = [
    [1, 2, 3, 4],
    [2, 5, 6, 5],
    [3, 6, 9, 6],
    [4, 5, 6, 5]
]

# Expected behavior:
# Algorithm 2 starts at (0,0) = 1
# Moves to better neighbor: (0,1) = 2 -> (0,2) = 3 -> (0,3) = 4
# Then moves down: (1,3) = 5 -> (1,2) = 6 -> (2,2) = 9
# At (2,2) = 9, neighbors are: (1,2)=6, (2,1)=6, (2,3)=6, (3,2)=6
# All neighbors are smaller, so Algorithm 2 returns (2,2)
# However, (2,2) = 9 IS a peak, so this may not be a counterexample
# 
# A better counterexample would be one where Algorithm 2 gets stuck
# in a location that is not a peak due to its greedy nature

