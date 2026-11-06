# System Call Tracing and Sysinfo Benchmark Task

## Background

This benchmark extends the xv6-riscv kernel with two debugging-oriented facilities. The first is a trace system call that prints kernel trace lines for selected system calls invoked by a process and its future children. The second is a sysinfo system call that reports basic system statistics (free memory and active process count) back to user space. Together they mirror the requirements from the "System call tracing" and "Sysinfo" assignments in the MIT 6.S081 labs.

## Goals

1. Implement process-local syscall tracing that can be toggled via `trace(mask)` where each bit corresponds to a syscall number from `kernel/syscall.h`.
2. Provide a `sysinfo(struct sysinfo *)` syscall that fills a user-provided struct with the number of free bytes and the number of processes that are not `UNUSED`.
3. Ensure both features propagate correctly through fork/exec flows, interact only with the calling process (and its descendants), and survive concurrent workloads.

## Implementation Scope

 All other repository contents emulate an xv6 lab submission harness and should remain untouched.

### Kernel Updates

- `kernel/proc.h`: extend `struct proc` with a tracing mask field persisted across context switches and forked children.
- `kernel/proc.c`: copy the tracing mask in `fork()` and provide an `nproc()` helper that counts processes whose state differs from `UNUSED`.
- `kernel/syscall.c`: register the new syscalls, maintain a syscall name table, and emit `printf` trace lines before returning to user space when the mask bit is set. Format lines as `{pid}: syscall {name} -> {return}`.
- `kernel/syscall.h`: assign syscall numbers for `trace` and `sysinfo`.
- `kernel/sysproc.c`: implement `sys_trace()` to store the mask and `sys_sysinfo()` to populate a local `struct sysinfo`, fetch arguments with `argint`/`argaddr`, and return data with `copyout`.
- `kernel/kalloc.c`: add `kfreenum()`/`freemem()` helpers that count free pages under the allocator lock.
- `kernel/defs.h`: declare the new helper prototypes.
- `kernel/sysinfo.h`: define the `struct sysinfo` layout shared with user programs.

### User-Space Updates

- `user/user.h`: declare `trace(int)` and forward-declare `struct sysinfo` plus `sysinfo(struct sysinfo *)`.
- `user/usys.pl`: generate syscall stubs for the new entries.
- `user/trace.c`: supplied utility that expects the `trace` syscall to exist.
- `user/sysinfotest.c`: supplied test program that exercises the `sysinfo` syscall.
- `Makefile`: add `$U/_trace` and `$U/_sysinfotest` to `UPROGS` so both utilities build into the xv6 file system image.


