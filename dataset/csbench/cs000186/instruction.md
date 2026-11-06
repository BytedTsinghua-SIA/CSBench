## Project 1: Buffer Pool Manager

In this project, you will implement the storage manager’s **buffer pool manager** for BusTub, a disk-oriented DBMS. A disk-oriented design keeps the primary database on persistent storage (HDD/SSD) and uses memory as a cache.

BusTub moves data in fixed-size units:

- **Page**: 8192 bytes (8 KB) of logical database data.
- **Frame**: an 8 KB region of memory that can hold one page at a time.

The buffer pool manager provides a uniform interface to other DBMS components: when they request a page by `page_id_t`, they should not need to know whether the page is already in memory or must be fetched from disk.

### Concurrency model

Your implementation must be **thread-safe**:

- Multiple threads will access internal buffer pool structures concurrently.
- You must protect critical sections with **latches** (mutexes).
- The DBMS must never keep two in-memory copies of the same page at once (to avoid write-write races).

The buffer pool manager tracks:

- A **page table** mapping `page_id_t -> frame_id_t`.
- A **pin count** per frame (number of active users of the page). Pinned pages must not be evicted.
- A **dirty flag** per frame to decide whether to flush on eviction.

---

## What You Need to Implement

This project has three components:

1. **Adaptive Replacement Cache (ARC) Replacer**
2. **Disk Scheduler**
3. **Buffer Pool Manager** (plus **page guards** for safe access)

### Global Implementation Requirements

For each of the following components, stub classes are already provided with the APIs you must implement. **You must follow these constraints**:

- You must **not modify the signatures** for the pre-defined functions in these classes. If you change them, the grading tests will not compile or run, and you will not receive credit.
- If a class already contains data members, you **must not remove them**. For example, the `BufferPoolManager` class contains `DiskScheduler` and `ArcReplacer` members that are required for correct functionality.
- You **may add** additional data members and helper functions to these classes to correctly implement the required functionality.
- You may use any built-in **C++17 containers** unless specified otherwise. These containers are **not thread-safe**, so you must protect them with appropriate latches.
- You **may not** use additional third-party libraries (e.g., Boost).

Most of your code changes will be in:

- `src/include/buffer/arc_replacer.h`, `src/buffer/arc_replacer.cpp`
- `src/include/storage/disk/disk_scheduler.h`, `src/storage/disk/disk_scheduler.cpp`
- `src/include/storage/page/page_guard.h`, `src/storage/page/page_guard.cpp`
- `src/include/buffer/buffer_pool_manager.h`, `src/buffer/buffer_pool_manager.cpp`

Other files should only be changed if explicitly required (e.g., adding tests), and you should never change test files or public APIs in a way that breaks the provided tests.


## Task #1 (ARC Replacement Policy)

Implement `ArcReplacer`:

- Header: `src/include/buffer/arc_replacer.h`
- Implementation: `src/buffer/arc_replacer.cpp`

ARC is an adaptive policy that tracks both recency and frequency using four lists:

- **MRU**: pages accessed exactly once recently
- **MFU**: pages accessed more than once recently
- **MRU ghost**: recently evicted pages formerly in MRU
- **MFU ghost**: recently evicted pages formerly in MFU

ARC also maintains an adaptive **MRU target size** that shifts based on observed ghost hits.

### Required API

Implement these methods **exactly as declared** in the header:

- `Size() -> size_t`
  - Returns the number of **evictable** frames currently tracked by the ARC.
- `SetEvictable(frame_id_t frame_id, bool set_evictable)`
  - Marks a frame as evictable or non-evictable and updates the ARC’s current evictable size. Typically called when a page’s pin count transitions to or from zero.
- `RecordAccess(frame_id_t frame_id, page_id_t page_id)`
  - Records that `page_id` stored in `frame_id` was accessed. Updates MRU/MFU and ghost lists according to the ARC algorithm.
- `Evict() -> std::optional<frame_id_t>`
  - Chooses a victim frame to evict following the ARC policy. Returns `std::nullopt` if no evictable frame exists.
- `Remove(frame_id_t frame_id)`
  - Removes a frame and its page from the replacer if it exists and is currently evictable. Used when a page is deleted from the buffer pool.

### RecordAccess behavior (high level)

On each access of `(frame_id, page_id)`, one of these happens:

1. **Hit in MRU/MFU**: move page to front of **MFU**.
2. **Hit in MRU ghost**: increase MRU target size (bounded by capacity), then move to front of **MFU**.
3. **Hit in MFU ghost**: decrease MRU target size (bounded by 0), then move to front of **MFU**.
4. **Miss everywhere**: insert into front of **MRU**, potentially trimming ghost lists to maintain size invariants.

### Eviction behavior (high level)

When evicting:

- If `MRU.size() < mru_target_size_`, prefer evicting from **MFU**; otherwise prefer **MRU**.
- If the preferred list has no evictable frames, try the other list.
- If neither has an evictable frame, return `std::nullopt`.

### Performance note

`RecordAccess` is on a hot path. The tests include a performance check; avoid linear scans by maintaining efficient lookups (e.g., hash maps to list iterators).

---

## Task #2 (Disk Scheduler)

Implement `DiskScheduler`:

- Header: `src/include/storage/disk/disk_scheduler.h`
- Implementation: `src/storage/disk/disk_scheduler.cpp`

The disk scheduler queues `DiskRequest`s and processes them on a **background worker thread**.

### Required API

- `Schedule(std::vector<DiskRequest> &requests)`
  - Schedules a **vector of disk requests** to be executed by the disk manager. Each `DiskRequest` describes a read or write operation, including the page ID, buffer pointer, and a `std::promise<bool>` callback that must be set to `true` when the request finishes.
- `StartWorkerThread()`
  - Entry point for the background worker thread created in the constructor. It repeatedly receives queued `DiskRequest`s from the shared channel/queue, dispatches them to `DiskManager::ReadPage` / `DiskManager::WritePage`, and signals completion via the request’s `std::promise`. This method should not return until the scheduler is being shut down in the destructor.

Each `DiskRequest` includes a `std::promise` callback that must be fulfilled when the request completes (see `disk_scheduler_test.cpp` for usage patterns).

The scheduler should dispatch to the disk manager:

- `DiskManager::ReadPage()`
- `DiskManager::WritePage()`

You may use the provided thread-safe `Channel` (`src/include/common/channel.h`) or your own safe queue.

---

## Task #3 (Buffer Pool Manager + Page Guards)

Implement the buffer pool manager and the RAII page guards.

### Page guards

Implement move semantics and RAII behavior in:

- Header: `src/include/storage/page/page_guard.h`
- Implementation: `src/storage/page/page_guard.cpp`

Required methods:

- `ReadPageGuard::ReadPageGuard()`
  - Default constructor; initializes an empty guard that does not own any page.
- `ReadPageGuard::ReadPageGuard(ReadPageGuard &&that)`
  - Move constructor; transfers ownership of the underlying page and any associated pin/latch state from `that`, leaving `that` empty.
- `ReadPageGuard::operator=(ReadPageGuard &&that) -> ReadPageGuard &`
  - Move assignment; releases any currently held page (if any), then takes ownership from `that` and leaves `that` empty.
- `ReadPageGuard::Flush()`
  - Flushes the underlying page to disk if needed (typically via the buffer pool manager) while keeping the guard valid.
- `ReadPageGuard::Drop()`
  - Explicitly releases ownership of the guarded page (unpinning/unlatching as appropriate). After `Drop`, the guard should behave as empty.
- `WritePageGuard::WritePageGuard()`
  - Default constructor; initializes an empty write guard.
- `WritePageGuard::WritePageGuard(WritePageGuard &&that)`
  - Move constructor; transfers ownership of the write-access page from `that` and invalidates `that`.
- `WritePageGuard::operator=(WritePageGuard &&that) -> WritePageGuard &`
  - Move assignment; drops any currently held page, then acquires ownership from `that`.
- `WritePageGuard::Flush()`
  - Flushes the underlying (potentially dirty) page to disk while retaining write access.
- `WritePageGuard::Drop()`
  - Releases write ownership of the page, ensuring that the page is properly unpinned/unlatched. After `Drop`, the guard holds no page.

These guards provide safe read/write access and must correctly release resources when dropped or moved.

### BufferPoolManager

Implement in:

- Header: `src/include/buffer/buffer_pool_manager.h`
- Implementation: `src/buffer/buffer_pool_manager.cpp`

Required methods:

- `NewPage() -> page_id_t`
  - Allocates a new page in the database, chooses a frame (evicting if necessary), and pins the new page in the buffer pool. Returns the new `page_id_t`.
- `DeletePage(page_id_t page_id) -> bool`
  - Deletes the specified page from the buffer pool and disk (if possible). Fails if the page is pinned or otherwise not safe to remove.
- `CheckedWritePage(page_id_t page_id) -> std::optional<WritePageGuard>`
  - Pins the page for write access and returns a `WritePageGuard` if the page can be loaded/found. Returns `std::nullopt` if the page cannot be brought into the buffer pool.
- `CheckedReadPage(page_id_t page_id) -> std::optional<ReadPageGuard>`
  - Pins the page for read access and returns a `ReadPageGuard` if successful, or `std::nullopt` on failure.
- `FlushPageUnsafe(page_id_t page_id) -> bool`
  - Flushes a single page’s contents from its frame to disk **without** acquiring the global buffer pool latch (caller must already hold appropriate synchronization).
- `FlushPage(page_id_t page_id) -> bool`
  - Flushes the specified page to disk **with** proper internal synchronization.
- `FlushAllPagesUnsafe()`
  - Flushes all pages in the buffer pool to disk without acquiring the outer latch (assumes caller holds it).
- `FlushAllPages()`
  - Flushes all pages in the buffer pool to disk while managing synchronization internally.
- `GetPinCount(page_id_t page_id)`
  - Returns the current pin count of the frame holding the given page, which reflects how many threads are actively using it.

Implementation guidance from the spec:

- Holding the buffer pool latch for the full duration of each public method is acceptable, except when you must release early to avoid deadlocks.
- Ensure correctness first, but avoid pathological slowness (future projects build on this).

## Formatting, Linting, and Sanitizers

Your code must follow the Google C++ Style Guide. Submissions that fail these checks receive **zero credit**.

```bash
make format
make check-clang-tidy-p1
```

Memory checks:

- Use ASAN/LSAN in Debug builds to find memory errors.
- Note: macOS supports ASAN but not LSAN.
