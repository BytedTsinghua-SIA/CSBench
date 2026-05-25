# Threading and Synchronization Benchmark Task

This benchmark recreates the "thread" lab from the MIT 6.S081 operating systems course. The repository that the agent receives is a snapshot of the xv6-labs codebase with the uthread, parallel hash table (ph), and barrier assignments left unfinished. The goal is to implement the missing functionality so that the xv6 grading scripts report a clean pass for the corresponding tests.

The benchmark exercises three different problem domains:

1. **User-level thread switching on xv6** (`user/uthread.c`, `user/uthread_switch.S`)
   * Implement `thread_create`, `thread_schedule`, and the assembly routine `thread_switch` so that threads run on their own stacks and cooperatively yield to each other.
   * The `uthread` test should print interleaved output from three threads that count to 100 and exit. Passing is verified by `make grade`'s `uthread` case.

2. **Parallel hash table on Linux/macOS** (`notxv6/ph.c`)
   * Fix data races in `put`/`get` by introducing appropriate locking so that no keys are lost when multiple threads call the routines concurrently (`ph_safe`).
   * Refine the design (e.g., lock per bucket) to allow concurrent inserts that touch different buckets to run in parallel (`ph_fast`).
   * You will interact with POSIX threads (`pthread_*`) and measure throughput with `./ph <nthreads>`.

3. **Barrier synchronization on Linux/macOS** (`notxv6/barrier.c`)
   * Implement a reusable barrier using pthread mutexes and condition variables so that no worker proceeds past the barrier until every worker reaches it.
   * Handle successive barrier rounds correctly.

### Expected workflow for solvers
1. Study the provided xv6 and not-xv6 source files to understand the missing pieces.
2. Implement the necessary context-switching and synchronization primitives.
3. Build and test locally with `make grade`, which runs:
   * `uthread` test on xv6 via `make qemu`
   * `ph_safe` and `ph_fast` on the host toolchain
   * `barrier` regression tests
4. Ensure `make grade` exits successfully without regressions.
5. Record the time spent in `time.txt` as an integer number of hours.
6. Commit all changes (including any required answer files) and run `make handin` when submitting upstream.

### Automated evaluation
The evaluation harness performs the following steps:
1. Apply the agent's patch on top of the starter repository.
2. Restore any files listed in `.file` to their original state.
3. Copy the resulting workspace into `/testbed` for an isolated build.
4. Execute `bash test.sh`, which is expected to run the full `make grade` pipeline.

Your solution passes if `bash test.sh` exits with status code zero.