# Homework Memory Benchmark Task


## Objectives
- Extend the Pintos kernel with an `sbrk` system call and provide a user-mode wrapper.
- Track the per-process heap state so that user programs can request and release heap pages.
- Implement a simple `malloc`/`realloc`/`free` allocator in `mm_alloc` using `sbrk` for backing memory.
- Ensure all new heap allocations are zero-initialised and that shrinking the heap unmaps whole pages that become unused.

## Required Files
- `pintos/src/lib/syscall-nr.h`: add the syscall number for `SYS_SBRK`.
- `pintos/src/lib/user/syscall.c`: implement the user wrapper that invokes the `SYS_SBRK` syscall.
- `pintos/src/userprog/syscall.c`: handle the `SYS_SBRK` case inside the kernel, map and free pages with `palloc`/`pagedir` helpers, zero newly allocated ranges, and update the process break.
- `pintos/src/userprog/process.c`: compute the initial break from the loaded segments and initialise the heap metadata stored on the current thread.
- `pintos/src/threads/thread.h`: extend `struct thread` with fields that record the heap base and the current break.
- `mm_alloc/mm_alloc.c`: implement the allocator by managing a doubly linked list of blocks that calls `sbrk` when more memory is required.
