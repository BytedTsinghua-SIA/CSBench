# RISC-V Trap Handling and Alarm Benchmark

## Goal
Implement the xv6 "traps" lab features so that the repository builds and passes the official grading script. The lab exercises three areas:

1. Produce well-reasoned answers for the introductory RISC-V questions in `answers-traps.txt`.
2. Add a stack backtrace helper that prints call-site return addresses whenever `sys_sleep` returns and whenever the kernel panics.
3. Extend the process scheduler with periodic user-level alarms driven by a new `sigalarm`/`sigreturn` system call pair.


## Required Deliverables
- `answers-traps.txt`: answer every question from the assignment description. The grading script only checks that the file exists and contains at least ten non-whitespace characters; however, include the full reasoning so a human can review it.
- `kernel/printf.c`: supply a `backtrace()` implementation that walks kernel stack frame pointers, prints the saved return address for each frame, and terminates gracefully once it leaves the current kernel stack page. Ensure `panic()` invokes `backtrace()` before halting.
- `kernel/sysproc.c`: call `backtrace()` at the end of `sys_sleep` after releasing `tickslock` and rework the system call layer to support alarms.
- `kernel/proc.h`, `kernel/proc.c`, `kernel/trap.c`, `kernel/syscall.*`, `user/` sources: maintain or add the fields, prototypes, and glue required to track alarm metadata, save/restore trapframes, and expose the syscalls to user space. The scaffold already contains most of the necessary structure; fill in any missing logic without rewriting unrelated code.
- `user/alarmtest.c`: keep the reference program intact; it drives the automated checks. Do not alter its expected output sequence.
- `time.txt`: record a single integer representing the hours spent on the lab.

## Functional Expectations
- `backtrace()` must print a header line `backtrace:` followed by one line per return address formatted as `%p`. The sample `bttest` execution should resemble:
  ```
  backtrace:
  0x0000000080002cda
  0x0000000080002bb6
  0x0000000080002898
  ```
- The alarm subsystem must trigger a handler every *n* timer ticks of CPU time, suspend the user context while the handler runs, and resume execution at the interrupted instruction once the handler calls `sigreturn()`. Nested alarms are forbidden—ignore timer interrupts while a handler is active.
- `alarmtest` must print `test0 passed`, `test1 passed`, and `test2 passed` with intermittent `alarm!` messages exactly as in the assignment statement. `usertests` must finish with `ALL TESTS PASSED`.

## Submit the lab

**This completes the lab.** Make sure you pass all of the make grade tests. If this lab had questions, don't forget to write up your answers to the questions in answers-*lab-name*.txt. Commit your changes (including adding answers-*lab-name*.txt) and type make handin in the lab directory to hand in your lab.

### Time spent

Create a new file, `time.txt`, and put in it a single integer, the number of hours you spent on the lab. Don't forget to `git add` and `git commit` the file.

