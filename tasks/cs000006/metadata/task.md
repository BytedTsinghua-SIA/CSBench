# Cache Lab Benchmark Task

## Background

This assignment adapts the cache simulator and matrix transpose components of the CS:APP Cache Lab. You will complete the provided skeletons  to model the behavior of a set-associative cache and to craft cache-friendly matrix transposes. By doing so, you will gain hands-on practice with:

- Translating a memory trace into cache hits, misses, and evictions under configurable cache parameters.
- Applying Least Recently Used (LRU) replacement policies within a simulated cache hierarchy.
- Designing matrix transposition kernels that minimize cache misses on realistic cache organizations.
- Building, running, and validating systems code with make-based toolchains.

## Goals

1. Finish the cache simulator so it accepts standard command-line flags, ingests trace files, and reports hit, miss, and eviction counts exactly as described in the Cache Lab handout.
2. Implement an optimized `transpose_submit` that meets the official performance targets for 32×32, 64×64, and 61×67 matrix sizes while passing `is_transpose` validation.


## Required Deliverables

### Cache Simulator (`csim.c`)

- Parse command-line options `-s`, `-E`, `-b`, `-t`, and `-v`.
- Read memory traces from `traces/` (hex addresses with load/store operations).
- Maintain per-set LRU state to determine which line to evict on a miss.
- Summarize results via the supplied `printSummary` helper.

### Matrix Transpose (`trans.c`)

- Keep `transpose_submit` as the entry point evaluated by the autograder.
- Optimize for the three target matrix shapes using block decomposition and register tiling.
- Ensure the helper `is_transpose` continues to confirm correctness for arbitrary matrices.


## Development Environment

The official container is based on Ubuntu 22.04 with `build-essential`, `python3`, `make`, and `valgrind`. All dependencies must be installed via the Dockerfile so that the agent never needs to run `apt` or `pip` during evaluation.


## Usage Notes

- Keep the implementation focused: do not modify unrelated files or over-engineer beyond the provided skeletons.
- Follow the existing function signatures and output formats; graders rely on them.
- Feel free to add small helper functions when necessary, but avoid altering supplied headers or support files unless explicitly required.
