# Assignment 3: All Things Multiprocessing

This assignment covers multiprocessing, pipes, and process control via four problems. Implement the following: 1) a C pipeline utility, 2) a C++ subprocess library, 3) a `trace` system-call tracer, and 4) a `farm` multi-process prime factorization manager.

Recommended environment: Linux on ARM64 (aarch64). Samples and test harnesses are provided in the repo.

Container tip (ARM64): if building inside Docker on non-ARM hosts, use `docker build --platform=linux/arm64` or set `DOCKER_DEFAULT_PLATFORM=linux/arm64`.

---

## 1) Pipeline in C

Implement a `pipeline` function that spawns two child processes and connects the stdout of the first to the stdin of the second.

- Function signature: `void pipeline(char *argv1[], char *argv2[], pid_t pids[]);`
- Assume `argv1` and `argv2` are valid, NULL-terminated argument vectors; `pids` points to an array of length 2.
- Connect processes via a pipe and use `dup2`, `close`, and `execvp` appropriately.
- Do not wait for children: return immediately without calling `waitpid`.
- Record child PIDs in `pids[0]` and `pids[1]`.
- Ensure parallelism: `pipeline({"sleep","10",NULL}, {"sleep","10",NULL}, pids)` should take ~10s, not ~20s.

Files and tests:
- Implement in `pipeline.c`.
- Use `pipeline-test.c` (and extend it) to exercise your implementation.

Build and run:
- `make pipeline-test`
- `./pipeline-test`

Note: This problem is standalone and doesn’t contribute to later problems.

---

## 2) Subprocess in C++

Implement a flexible subprocess routine and supporting record in C++.

- Interface excerpt (see `subprocess.h` for full documentation):

```cpp
struct subprocess_t {
  pid_t pid;
  int supplyfd;   // parent → child stdin (or kNotInUse)
  int ingestfd;   // child → parent stdout (or kNotInUse)
};

subprocess_t subprocess(char *argv[],
                        bool supplyChildInput,
                        bool ingestChildOutput) throw (SubprocessException);
```

- Behavior:
  - `supplyChildInput == true`: set up pipe so parent can write to child’s stdin.
  - `ingestChildOutput == true`: set up pipe so parent can read child’s stdout.
- On any system call failure (parent or child), throw `SubprocessException` with an actionable message (see `subprocess-exception.h`).

Files and tests:
- Implement in `subprocess.cc`.
- Use `subprocess-test.cc` and add tests to cover all flag combinations: `(true,true)`, `(true,false)`, `(false,true)`, `(false,false)`.

Build and run:
- `make subprocess-test`
- `./subprocess-test`

Note: This C++ implementation links into later problems (trace, farm).

---

## 3) trace in C++ (ARM64)

Implement `trace`, a systems tool that profiles a target (“tracee”) and prints information about its system calls.

Modes:
- Simple (`--simple`): print only the system call code and raw return value.
- Full (default): print the system call name, arguments, return value, and for failures, the errno constant and `strerror` message.

Examples (see `simple-test5.cc`):
- Simple: prints only the numeric syscall code and raw return, e.g., `syscall(221) = 0` on ARM64 (syscall numbers differ by architecture).
- Full: `write(1, "12345\n", 6) = 6` and, on error, `-1 EBADF (Bad file descriptor)`.

ptrace essentials (ARM64/aarch64):
- `ptrace(PTRACE_TRACEME)`: called by the tracee before `raise(SIGSTOP)` and `execvp`.
- `ptrace(PTRACE_SETOPTIONS, pid, 0, PTRACE_O_TRACESYSGOOD)`: distinguish syscall-related `SIGTRAP`s.
- `ptrace(PTRACE_SYSCALL, pid, 0, 0)`: continue and stop at syscall entry/return; pair with `waitpid`.
- Read registers via `ptrace(PTRACE_GETREGSET, pid, NT_PRSTATUS, &iov)` where `iov_base` points to the ARM64 register struct (e.g., `struct user_pt_regs`).
  - Syscall number at entry: in register `x8`.
  - Arguments: in `x0`–`x5`.
  - Return value at syscall return: in `x0`.
- `ptrace(PTRACE_PEEKDATA, pid, addr, NULL)`: read memory to reconstruct string arguments.

Additional requirements and simplifications:
- Print all return values as integers, except `brk` and `mmap`, which return pointers.
- Support libraries: `trace-error-constants.*`, `trace-system-calls.*`, `trace-options.*`.
- First run may build a cache (`.trace_signatures.txt`); rebuild via `--rebuild`.

Build and run:
- `make trace`
- Simple: `./trace --simple ./simple-test5`
- Full: `./trace ./simple-test5`

---

## 4) farm in C++

Implement `farm`, which spawns one worker per CPU core, each running a self-halting `factor.py`, and distributes an unbounded stream of positive integers (one per line) to idle workers. Workers print prime factorizations; ordering is not enforced.

Overview:
- Each worker runs `factor.py --self-halting` and self-halts after completing one computation (resumed via `SIGCONT`).
- The parent writes inputs via pipes and tracks worker availability via `SIGCHLD`.
- Read integers from `stdin` (one per line); stop on EOF.
- Before exiting, wait for all workers to self-halt and terminate cleanly.

Suggested structures and globals:
```cpp
struct worker {
  worker() {}
  worker(char *argv[]) : sp(subprocess(argv, true, false)), available(false) {}
  subprocess_t sp;
  bool available;
};

static const size_t kNumCPUs = sysconf(_SC_NPROCESSORS_ONLN);
static std::vector<worker> workers(kNumCPUs);
static size_t numWorkersAvailable = 0;
```

Roadmap:
- `spawnAllWorkers`: start one self-halting `factor.py` per core; record `subprocess_t`s.
- `markWorkersAsAvailable` (SIGCHLD): `waitpid` the self-halted child and mark available.
- `getAvailableWorker`: block (e.g., via `sigsuspend`) until some worker is available.
- `broadcastNumbersToWorkers`: read lines, parse via `stoll`, dispatch to an available worker, resume via `SIGCONT`.
- `waitForAllWorkers`: wait until all workers are available.
- `closeAllWorkers`: uninstall `SIGCHLD` handler (`SIG_DFL`), send EOFs, and wait for termination.

Optional: pin workers to cores via `cpu_set_t`, `CPU_ZERO`, `CPU_SET`, and `sched_setaffinity`.

Build and run:
- `make farm`
- Example: `printf "123456789\n123456789\n123456789\n123456789\n" | ./farm`

Notes:
- Ensure exception safety and proper resource cleanup; avoid zombie processes.
- Sample solutions (`trace_soln`, `farm_soln`) are available via the `slink` symlink.

---

Use the provided headers and support libraries throughout (`subprocess.*`, `trace-*.h/.cc`, `string-utils.h`). Add and extend tests (`pipeline-test.c`, `subprocess-test.cc`, `simple-test*.cc`) to validate your implementation.
