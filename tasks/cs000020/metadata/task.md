## Task Instructions

https://pdos.csail.mit.edu/6.S081/2021/labs/cow.html

### Task Source

MIT 6.S081: Operating System Engineering Lab 5: Copy-on-Write Fork

### Task Overview

This lab involves implementing copy-on-write (COW) fork in the xv6 operating system. When a process calls fork(), instead of immediately copying all pages, the kernel should mark them as read-only and only copy them when they are written to.

### Detailed Requirements

1. **Modify the Fork System Call**: Update the `fork()` system call to set up the child process's page table entries as read-only and mark them as COW.
2. **Handle Page Faults**: Implement a page fault handler that detects write attempts to COW pages, allocates a new page, copies the contents, and updates the page table entry to make it writable.
3. **Testing**: Ensure that the implementation is tested thoroughly to verify that COW behavior is functioning correctly, including edge cases such as multiple processes writing to the same page.