# Task: Build a Parallel Task Execution Library

## Background
You are implementing a C++ task execution library that runs bulk task launches efficiently on a multi-core CPU. The library evolves from simple parallel launches to a thread-pool based scheduler and then to asynchronous task graphs with dependencies.

## Core Tasks
1. Implement the Part A task systems in `asst2/part_a/tasksys.cpp` and `asst2/part_a/tasksys.h`:
   - Parallel spawn per run
   - Thread pool with spinning workers
   - Thread pool with sleeping workers
2. Implement the Part B task-graph scheduler in `asst2/part_b/tasksys.cpp` and `asst2/part_b/tasksys.h`, including `runAsyncWithDeps()` and `sync()` for dependency-aware execution.

## Scoring
- Correctness of task execution for sync and async paths (all tests pass).
- Dependency handling in Part B (tasks run only after prerequisites).
- Efficiency of scheduling (thread pool usage and low overhead).
