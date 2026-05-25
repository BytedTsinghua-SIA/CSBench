## Task Instructions

This assignment involves implementing search algorithms and a classic AI problem in Common Lisp.

### Task Source

CMU 15-381/681: Artificial Intelligence - Homework 2

### Task Overview

Implement and test tree search algorithms (BFS, DFS, DFID) and solve the Missionary-Cannibal problem using depth-first search in Common Lisp.

### Detailed Requirements

1. **Tree Search Algorithms**: Implement three search algorithms that traverse a tree structure where leaves are atoms and non-leaves are lists of child nodes:
   - **BFS (Breadth-First Search)**: Traverse level-by-level, left-to-right
   - **DFS (Depth-First Search)**: Traverse depth-first, right-to-left
   - **DFID (Depth-First Iterative Deepening)**: Perform depth-limited DFS with increasing depth limits

2. **Missionary-Cannibal Problem**: Implement a solution to the classic puzzle where:
   - 3 missionaries and 3 cannibals must cross a river
   - A boat can carry at most 2 people
   - Missionaries must never be outnumbered by cannibals on either bank
   - Implement: final-state, next-state, succ-fn, on-path, mult-dfs, mc-dfs

3. **Testing**: The implementation must pass all test cases in test.lsp which verify:
   - BFS returns `(C A D B)` for tree `((A (B)) C (D))`
   - DFS returns `(D C B A)` for tree `((A (B)) C (D))`
   - DFID returns `(C A C D A B C D)` for tree `((A (B)) C (D))` with depth 3
   - MC-DFS correctly solves the missionary-cannibal problem from initial state (3 3 T)
