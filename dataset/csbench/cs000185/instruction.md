## Background (curated from the project specification)

To monitor real-time network usage and detect potential DDoS attacks on a high-traffic website, we need a data structure that approximates frequency counts efficiently with low memory overhead. The Count–Min Sketch (CM Sketch) is a probabilistic structure that maintains a compact 2D array of counters indexed by `d` independently seeded hash functions. Each update increments one cell per row; a query returns the minimum across those rows. CM Sketch is mergeable: summing two compatible sketches (same `w` and `d`) is equivalent to building a single sketch over the concatenation of their input streams.

Core parameters:

- `width (w)` – Number of columns per row; each hash maps an item to `[0, w-1]`. Larger `w` ⇒ smaller additive error.
- `depth (d)` – Number of rows / independent hash functions. Larger `d` ⇒ lower probability of overestimation.
- `hash family / seeds` – Derive `d` pairwise-independent hash functions (e.g., by mixing distinct seeds into a base hash per row).

### Example walkthrough (w=4, d=3)

Consider the stream: `["24.156.99.202", "172.217.22.14", "64.104.78.227", "24.156.99.202"]`.

Initialize the counter matrix (3 rows × 4 columns):

```
0 0 0 0
0 0 0 0
0 0 0 0
```

Insert `"24.156.99.202"`. Suppose the modulo-4 positions for the three hashes are `2, 0, 3`:

```
0 0 1 0
1 0 0 0
0 0 0 1
```

Insert `"172.217.22.14"`. Positions: `1, 0, 2` (row 1 collides at column 0):

```
0 1 1 0
2 0 0 0
0 0 1 1
```

Insert `"64.104.78.227"`. Positions: `3, 1, 2` (row 2 collides at column 2):

```
0 1 1 1
2 1 0 0
0 0 2 1
```

Insert `"24.156.99.202"` again (same positions `2, 0, 3`):

```
0 1 2 1
3 1 0 0
0 0 2 2
```

Estimate the frequency of `"24.156.99.202"` by looking up the same positions:

Row 0, col 2 → 2
Row 1, col 0 → 3
Row 2, col 3 → 2

Estimate:

```
Estimate("24.156.99.202") = min(2, 3, 2) = 2
```

Why take the minimum? Each row’s count can be inflated by collisions with other items, but the minimum across independent rows gives the tightest upper bound on the true frequency.

---

## Task #1 (Implement Count–Min Sketch)

Implement a basic Count–Min Sketch supporting insertion, frequency estimation, and merging. In `count_min_sketch.h`, the following functions are declared and must be implemented in `count_min_sketch.cpp`:

- `CountMinSketch(width, depth)`: constructor, creates a sketch with `width` columns (buckets) and `depth` rows (hash functions).
- `CountMinSketch(&&other)`: move constructor, transfers ownership of resources from another instance.
- `operator=(&&other)`: move assignment, moves resources from another instance into this one.
- `Insert(item)`: inserts the specified item; expected to be thread-safe.
- `Count(&item)`: returns the estimated frequency of the item (minimum across rows).
- `Clear()`: resets the counter matrix for fresh streams while preserving parameters and seeds.
- `Merge(&other)`: creates a new sketch by element-wise summing two compatible sketches (same `w` and `d`).
- `TopK(k, &candidates)`: practical usage—given known candidates that have been inserted, return the `k` candidates with the highest estimated counts.

Feel free to design helper functions to organize hashing, concurrency, and storage.

### Advice

- Hash design: derive independent seeds per row; mix seeds into a base hash to approximate pairwise independence.
- Concurrency and performance: `Insert` is the hot path; prefer per-row fine-grained locks or atomic counters to avoid global lock contention.
- Merge constraints: allow merging only when `w` and `d` match; otherwise return an error or throw.
- TopK semantics: rank only over the provided `candidates`, avoiding a full-table scan.
- Clearing and lifetime: `Clear()` zeroes counts but keeps seeds and dimensions; move semantics prevent double-free and unnecessary copies.

---

## Resources

To understand Count–Min Sketch and why it works:

- A visual walkthrough illustrating the internal mechanics of Count–Min Sketch.
- A comprehensive overview video covering Count–Min Sketch and practical applications (with Bloom Filter and HyperLogLog included in the full video).
- A concise paper analyzing the time and space bounds of the structure.

---

## Quality and Safety Checks

- Memory correctness: build in Debug mode to run with LLVM sanitizers integrated in the toolchain. Run your tests normally; if there are issues, the sanitizer will emit a detailed report (addresses, stacks, and error types). Treat these as correctness failures and fix before submission.
- Style and static checks: follow the Google C++ Style Guide. Automated Clang-based checks run on the source and must pass. Submissions that do not satisfy these checks receive no credit.

## Important Information

- Hash function requirement: use the seeded hash utilities provided in BusTub at `src/include/common/util/hash_util.h` to derive per-row hash functions. Do not implement your own hashing or rely on external libraries; otherwise, you may fail the provided test suite.
- Concurrency and performance: only `Insert(item)` is required to be thread-safe. The final test compares your parallel insertion throughput against a strictly sequential version; your implementation must achieve a relative speedup greater than 1.2×. Avoid guarding the entire data structure with a single global lock. Prefer fine-grained synchronization (e.g., per-row/per-bucket) or lock-free updates using atomics (e.g., `fetch_add`, `compare_exchange`) to reduce contention.
