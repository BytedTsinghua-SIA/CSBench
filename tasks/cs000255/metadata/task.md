## Task Instructions

CS161 Spring 2020 HW6 Problem 3: Graph coloring to SAT conversion

### Task Source

UCLA CS161: Fundamentals of Artificial Intelligence - Homework 6

### Task Overview

This task involves implementing a graph coloring to SAT (Boolean Satisfiability) problem converter in Common Lisp. The goal is to encode a graph coloring problem as a SAT instance in CNF (Conjunctive Normal Form) format, which can then be solved by a SAT solver. The assignment focuses on understanding the reduction from graph coloring to SAT and implementing the encoding functions.

### Detailed Requirements

1. **Variable Encoding (`node2var`)**: Implement a function that maps a node-color pair to a unique SAT variable index. For a graph with n nodes and k possible colors, each node has k corresponding Boolean variables (one for each possible color).

2. **At Least One Color (`at-least-one-color`)**: Generate a clause ensuring that a node gets at least one color from a given set of colors {c, c+1, ..., k}. This produces a single clause with positive literals representing the disjunction of all possible color assignments.

3. **At Most One Color (`at-most-one-color`)**: Generate clauses ensuring that a node gets at most one color from a given set. This requires pairwise exclusion clauses - for each pair of distinct colors, create a clause stating that the node cannot have both colors simultaneously.

4. **Generate Node Clauses (`generate-node-clauses`)**: Combine the "at least one" and "at most one" constraints to ensure each node gets exactly one color from the set {1, 2, ..., k}.

5. **Generate Edge Clauses (`generate-edge-clauses`)**: For each edge connecting two nodes, generate clauses ensuring the connected nodes cannot have the same color. This is achieved by creating, for each color c, a clause that negates both nodes having color c.

6. **Top-level Conversion (`graph-coloring-to-sat`)**: The provided function reads a graph from a file (first line: number of nodes; subsequent lines: edges), generates all necessary constraints, and writes the resulting CNF formula to an output file in DIMACS format.
