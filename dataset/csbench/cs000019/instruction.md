# Large File Support and Symbolic Link Benchmark Task

## Background

This benchmark extends the xv6 file system to remove two classic limitations. First, the stock xv6 inode layout only supports up to 268 data blocks per file because it exposes 12 direct pointers and one singly-indirect pointer. Second, xv6 lacks symbolic links, preventing user programs from creating path-based references to other files. You will enhance the kernel so that:

- Regular files may grow up to 65,803 blocks by introducing a doubly-indirect pointer while keeping the on-disk inode size fixed.
- A new `symlink` system call allows user programs to create and traverse symbolic links, including nested links with cycle detection.

## Goals

1. Modify the file system implementation in `kernel/fs.c` and related headers so each inode holds 11 direct pointers, one singly-indirect pointer, and one doubly-indirect pointer.
2. Ensure block allocation (`bmap`) and deallocation (`itrunc`) properly manage the new doubly-indirect level without leaking blocks.
3. Add symbolic link support by introducing file type `T_SYMLINK`, wiring the `symlink` system call, storing link targets, and teaching `open` to follow links unless `O_NOFOLLOW` is set.
4. Update user-space interfaces (`user/user.h`, `user/usys.pl`, and `Makefile`) so the new call is available and test programs build.
5. Preserve xv6 behavior for directories, device files, and existing syscalls while preventing infinite link resolution (e.g., cap the depth at 10).

## Implementation Notes

### Doubly-Indirect Blocks

- Keep the on-disk inode structure (`struct dinode`) size unchanged by repurposing one direct pointer slot for the doubly-indirect pointer.
- Define supporting constants in `kernel/fs.h` (e.g., `NDIRECT`, `NINDIRECT`, `NDOUBLYINDIRECT`, and the updated `MAXFILE`). Ensure the in-memory inode (`struct inode` in `kernel/file.h`) mirrors the on-disk layout.
- Extend `bmap` in `kernel/fs.c` to allocate intermediate blocks lazily when traversing the doubly-indirect tree. Each intermediate block stores `NINDIRECT` child addresses.
- Extend `itrunc` so truncating a file frees every singly- and doubly-indirect block and the underlying data blocks.

### Symbolic Links

- Add `T_SYMLINK` to `kernel/stat.h` and reserve a new open flag `O_NOFOLLOW` in `kernel/fcntl.h`.
- Implement `sys_symlink` in `kernel/sysfile.c` to create a symlink inode and persist the target path inside its data blocks.
- Update `sys_open` so opening a symlink follows the stored target path recursively unless `O_NOFOLLOW` is specified. Abort with an error once the resolution depth exceeds 10 or a referenced path is missing.
- Expose the user-space wrapper by adding the syscall number in `kernel/syscall.h`, exporting it in `kernel/syscall.c`, and regenerating the stubs via `user/usys.pl` and headers.
- Keep other operations (e.g., `link`, `unlink`) acting on the link itself rather than the target.

## Repository Layout

- `kernel/`: xv6 kernel sources, including file system code to update.
- `user/`: user-level programs and system call wrappers; contains the `symlinktest` utility.
- `Makefile`: builds xv6 for the fs lab configuration (`LAB=fs`).
- `grade-lab-fs`: automated grading script that drives QEMU-based tests.

## Development Environment

Builds rely on the RISC-V newlib toolchain and QEMU. The provided Dockerfile installs:

- `gcc-riscv64-unknown-elf` and `binutils-riscv64-unknown-elf` for cross-compiling xv6.
- `qemu-system-misc` to emulate RISC-V in headless mode.
- Standard build utilities (`build-essential`, `make`, `python3`, `git`, etc.).

After entering the container, run all commands from the repository root unless noted otherwise.

## Final Checklist

1. Rebuild xv6 from a clean state (`make clean && python3 grade-lab-fs`).
2. Confirm `bigfile`, `symlinktest`, and `usertests` succeed with the outputs listed above.
3. Verify no extraneous files or debug prints were added and all modified code stays within the required scope.
