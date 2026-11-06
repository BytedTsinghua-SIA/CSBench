## Task Instructions

https://inst.eecs.berkeley.edu/~cs188/sp24/projects/proj1/

### Task Source

UC Berkeley CS188: Introduction to AI - Project 1: Search

### Task Overview

This project involves implementing various search algorithms for a Pacman agent to navigate through maze worlds, both to reach specific locations and to collect food efficiently. Students build general search algorithms and apply them to Pacman scenarios, learning about uninformed search (DFS, BFS, UCS) and informed search (A* with heuristics).

### Detailed Requirements

1. **Q1: Depth First Search (DFS)** - Implement graph-based DFS algorithm that finds paths through the maze. Must avoid revisiting states and return a list of legal actions.

2. **Q2: Breadth First Search (BFS)** - Implement graph-based BFS algorithm that finds shortest paths in terms of number of actions. Should find optimal solutions for unweighted graphs.

3. **Q3: Uniform Cost Search (UCS)** - Implement UCS algorithm that finds paths with minimum total cost. Handles varying cost functions (e.g., StayEastSearchAgent, StayWestSearchAgent).

4. **Q4: A* Search** - Implement A* graph search with heuristic functions. Uses heuristic evaluation to guide search more efficiently than UCS.

5. **Q5: Corners Problem** - Formulate a new search problem to find the shortest path that visits all four corners of a maze. Requires appropriate state representation that encodes visited corners.

6. **Q6: Corners Heuristic** - Design a non-trivial, consistent heuristic for the CornersProblem. Must be admissible (lower bound on true cost) and consistent (monotonic). Evaluated on node expansion count.

7. **Q7: Food Search Heuristic** - Implement a consistent heuristic for the FoodSearchProblem (eating all dots). Must return 0 at goal states and never be negative. Score depends on nodes expanded.

8. **Q8: Suboptimal Search** - Implement ClosestDotSearchAgent that greedily eats the closest dot using repeated searches. Requires implementing AnyFoodSearchProblem with appropriate goal test.

### Files to Edit

- `search.py` - Contains search algorithms (DFS, BFS, UCS, A*)
- `searchAgents.py` - Contains search-based agents and problem definitions

### Grading Criteria

- Q1-Q5: 3 points each for correctness
- Q6: Up to 3 points based on node expansion (≤2000 nodes for full credit)
- Q7: Up to 4 points based on node expansion (≤9000 nodes for full credit, ≤7000 for extra credit)
- Q8: 3 points for correctness

**Total: 25 points**

### Key Concepts

- Graph search with visited state tracking
- Fringe management: Stack (LIFO), Queue (FIFO), PriorityQueue
- Heuristics: admissibility vs consistency
- State representation design
- Problem formulation for search
