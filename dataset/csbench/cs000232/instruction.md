## Task Instructions

https://www.cs.umd.edu/class/spring2025/cmsc714/Projects/OpenMP/openmp-project.shtml

### Task Source

CMSC714 High Performance Computing (Spring 2025) - Project 1: OpenMP

### Task Overview

This project involves parallelizing a serial earthquake simulation program (quake.c) using OpenMP directives. The goal is to gain experience writing OpenMP programs, systematically identify performance bottlenecks, and achieve measurable speedup on a multi‑core compute node. The parallel version must produce identical results to the serial version while scaling efficiently across 1, 2, 4, 8, 16, and 32 threads.

### Detailed Requirements

1. **Profiling and Analysis**: Use `gprof` (compile with `-pg`) to identify the most time‑consuming parts of the serial program. Examine the loops in those subroutines to determine where OpenMP parallelism can be applied.

2. **OpenMP Parallelization**: Add appropriate OpenMP directives (e.g., `#pragma omp parallel`, `#pragma omp for`, `#pragma omp reduction`) to the candidate loops and functions in `quake_omp.c`. Ensure thread safety and correct handling of shared/private variables.

3. **Correctness Verification**: The parallel program must produce output identical to the serial version for any number of threads. Use `diff` to compare outputs when running on the provided input files (`quake.in` and `quake.in.short`). Debugging output should be sent to stderr, not stdout.

4. **Performance Measurement**: Run the parallel program on the full input file `quake.in` with 1, 2, 4, 8, 16, and 32 threads, recording execution times. The program should be compiled with `gcc -fopenmp -O2 -o quake_omp quake_omp.c -lm` (without `-pg` for final timing).

5. **Speedup Analysis**: Calculate speedup relative to the serial version (or the parallel version with 1 thread). The parallel implementation must show measurable speedup: at least two thread counts (among 1,2,4,8,16,32) should achieve speedup > 1.10 relative to the serial version, and execution with 4 threads must be faster than with 1 thread (speedup > 1.05). Ideally, speedup should approach linear scaling for the parallelizable portions.

6. **Report Submission**: Write a short report (1‑2 pages) that:
   - Lists the OpenMP directives used and explains why they were chosen.
   - Presents performance results (execution times and speedup) for all thread counts.
   - Discusses whether the results meet expectations and explains any observed limitations or anomalies.

7. **Submission Package**: Place the OpenMP‑enabled source code (`quake_omp.c`), the report, and the timing results in a directory named `LastName‑assign2`, compress it to `LastName‑assign2.tar.gz`, and upload to the course’s ELMS platform.

8. **Grading Compliance**: The implementation must satisfy the grading rubric:
   - Correct execution with 1 thread (10 points)
   - Correct execution with 32 threads (30 points)
   - Performance with 1 thread (10 points)
   - Speedup of the parallel version (30 points)
   - Quality of the writeup (20 points)

Note: If the program does not run correctly, no performance/speedup points are awarded.