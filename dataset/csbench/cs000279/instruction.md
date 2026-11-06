# Assignment 6: Data Sagas

## Background
This assignment introduces low-level array behavior, heap-based priority queues, and a real-world apportionment algorithm. You will use the debugger to explore arrays, build a binary-heap priority queue with manual memory management, and apply it to Huntington-Hill apportionment.

## Tasks
1. Follow the instructions in `ExploreArrays.cpp`.
2. Implement the required `HeapPQueue` operations in `HeapPQueue.h` and `HeapPQueue.cpp`, including correct resizing and heap ordering, and add at least one `STUDENT_TEST` in `HeapPQueue.cpp`.
3. Implement `apportion` in `Apportionment.cpp` using `HeapPQueue`, handling error cases and matching the expected apportionment results (including the provided census data in `res/apportionment/2020.csv`).

## Scoring
- `HeapPQueue` operations are correct, efficient, and manage memory safely.
- `apportion` produces correct seat allocations and handles invalid inputs appropriately.
