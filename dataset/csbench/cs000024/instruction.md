# xv6 Page Table Lab Benchmark

This benchmark is based on the xv6 page table laboratory. 

## Shared userspace system call page
* When a process is allocated in `kernel/proc.c`, allocate a page for `struct usyscall` and initialize it with the process's PID.
* Map that page at `USYSCALL` (defined in `kernel/memlayout.h`) inside `proc_pagetable()` with read-only user permissions.
* Ensure the page is unmapped and freed in `freeproc()` / `proc_freepagetable()`.

## Page table printer
* Define `vmprint(pagetable_t)` in `kernel/vm.c` to recursively print valid entries in the format used by the xv6 lab handout.
* Expose the prototype via `kernel/defs.h` and invoke `vmprint(p->pagetable)` for the first user process (PID 1) in `kernel/exec.c` just before returning `argc`.

## Page access tracking system call
* Add the `pgaccess` system call in `kernel/sysproc.c` to scan up to a limited number of pages, report accessed pages through a user bitmask, and clear the accessed bit (`PTE_A`) on inspected entries.
* Define `PTE_A` in `kernel/riscv.h` and register the syscall in `kernel/syscall.c` / `kernel/syscall.h` as needed.

## User support
* Provide a user helper `ugetpid()` in `user/ulib.c` that reads from the `USYSCALL` mapping.
* Make sure headers (`kernel/proc.h`, `user/user.h`) declare the new structures and functions under `#ifdef LAB_PGTBL` guards, matching the existing layout.

## Submit the lab

**This completes the lab.** Make sure you pass all of the make grade tests. If this lab had questions, don't forget to write up your answers to the questions in answers-*lab-name*.txt. Commit your changes (including adding answers-*lab-name*.txt) and type make handin in the lab directory to hand in your lab.

### Time spent

Create a new file, `time.txt`, and put in it a single integer, the number of hours you spent on the lab. Don't forget to `git add` and `git commit` the file.

