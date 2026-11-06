## Task Instructions

https://pdos.csail.mit.edu/6.S081/2021/labs/lock.html

### Task Source

MIT 6.S081: Operating System Engineering Lab 8: Locks

### Task Overview

This lab involves implementing locks in the xv6 operating system to provide mutual exclusion for critical sections of code. Locks are essential for preventing race conditions when multiple processes access shared resources.

### Detailed Requirements

1. **Implement Lock Structure**: Define a lock structure that includes necessary fields such as a flag to indicate if the lock is held and a queue for processes waiting for the lock.
2. **Lock Acquisition and Release**: Implement functions to acquire and release locks. The acquire function should block the calling process if the lock is already held, while the release function should wake up one of the waiting processes.
3. **Testing**: Ensure that the implementation is tested thoroughly to verify that locks provide mutual exclusion and handle contention correctly, including edge cases such as deadlocks and priority inversion.