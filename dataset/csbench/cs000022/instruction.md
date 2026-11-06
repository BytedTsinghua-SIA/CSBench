# Memory-Mapped File Support Benchmark

## Background

This benchmark targets the xv6-riscv teaching operating system. The stock kernel lacks support for the `mmap` and `munmap` system calls that user programs expect for memory-mapped files. The goal is to extend xv6 so that user processes can request file-backed virtual memory regions whose contents are populated on demand and optionally written back to disk.

## Objectives

1. Add a virtual memory area (VMA) abstraction so each process tracks its active `mmap` regions, including start address, length, protection bits, sharing mode, and backing file.
2. Implement the `mmap` system call so it:
   - Chooses an unused, page-aligned address range when user code passes `addr = 0`.
   - Records the mapping in the calling process's VMA list and duplicates the referenced `struct file`.
   - Defers physical page allocation until the process faults on the range.
3. Handle page faults inside `usertrap` by allocating a page, reading the corresponding file contents into it, zero-filling any short read, and inserting the page with permissions derived from the VMA's `prot` flags.
4. Implement `munmap` so it unmaps full or partial regions (restricted to trimming the start, end, or entire mapping), optionally writes dirty MAP_SHARED pages back to the file, updates or removes the VMA, and decrements the file reference count when a mapping disappears.
5. Ensure `exit` cleans up any remaining VMAs and `fork` clones the parent's mappings while bumping file reference counts so children fault in their own pages.
6. Export user-visible stubs by wiring syscall numbers, dispatchers, and user-space wrappers so `user/mmaptest.c` builds and runs.

## Key Source Files

- `kernel/vma.c` and `kernel/vma.h`: global VMA pool management, `mmap`, `munmap`, and page-fault handling helpers.
- `kernel/trap.c`: user trap handler that detects page faults and invokes VMA allocation on demand.
- `kernel/proc.c`: process lifecycle updates for cloning and cleaning up VMAs.
- `kernel/sysfile.c`, `kernel/syscall.c`, and `kernel/syscall.h`: syscall plumbing for `mmap`/`munmap`.
- `user/`: user programs, including `mmaptest`, which exercises the implemented functionality.

