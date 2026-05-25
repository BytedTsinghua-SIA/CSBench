## Background (Assignment 5: RSS News Feed Aggregation)

This assignment focuses on building a multithreaded RSS news feed aggregator. You will transition from a sequential implementation to a highly concurrent one, managing threads, mutexes, and semaphores to speed up data ingestion.

Outcomes:
- Experience with C++ threads, mutexes, and semaphores.
- Handling race conditions and deadlocks.
- Networking and parsing in a concurrent environment.
- Building an inverted index for search.

---

## Inputs and Constraints

- **Input**: An XML file containing a list of RSS feeds (e.g., `medium-feed.xml`).
- **Output**: An interactive console for searching the built index.
- **Constraints**:
    - **No Memory Leaks**: All allocated memory must be freed before exit.
    - **Thread Safety**: Zero race conditions or deadlocks.
    - **Strict Thread Limits**: Adhere to global and per-server thread limits.

---

## Required Features

### 1) Sequential Aggregation (Milestone 1)
- **Feed Parsing**: Download and parse the feed list.
- **Article Parsing**: Download and parse each article in the feeds.
- **Indexing**: Build an inverted index mapping words to articles.
- **De-duplication**:
    - **URL Uniqueness**: Never download the same URL twice.
    - **Smart Intersection**: If multiple articles have the **same title** and **same server** but different URLs:
        - Download all of them.
        - Intersect their token sets (keep only words present in ALL versions).
        - Store the result under the lexicographically smallest URL.

### 2) Multithreaded Aggregation (Milestone 2)
Transform the sequential aggregator into a concurrent one with the following strict limits:

- **Feed Threads**:
    - Each RSS feed is processed in its own child thread.
    - **Limit**: Max **5** concurrent feed threads.
- **Article Threads**:
    - Each article is downloaded in its own grandchild thread.
    - **Global Limit**: Max **18** concurrent article download threads total.
    - **Per-Server Limit**: Max **8** concurrent connections to any single server (e.g., `www.economist.com`).
- **Synchronization**:
    - Use **mutexes** to protect shared data structures (e.g., the `RSSIndex`, the set of visited URLs).
    - Use **semaphores** to enforce the thread counts (global 18, feed 5, per-server 8).
    - Ensure the `RSSIndex` is fully built before the query loop starts.

### 3) Search Interface
- After indexing completes, enter a REPL (Read-Eval-Print Loop).
- User enters a search term.
- Program displays matching articles, sorted by relevance (frequency of the term).

---

## Program Interface (CLI)

The program is executed with a feed list XML file.

```bash
./aggregate --url <feed-list-xml> [--verbose|--quiet] [--report-limits]
```

**Example Session:**

```text
myth4> ./aggregate --url medium-feed.xml
MAX feed threads: <n>
MAX article threads: <n>
MAX per-server connections [<server>]: <n>
Enter a search term [or just hit <enter> to quit]: Manhattan
That term appears in 122 articles.  Here are the top 15 of them:
   1.) "Eight dead in truck attack on Manhattan bike path; suspect arrested" [appears 28 times].
       "http://feeds.reuters.com/~r/Reuters/domesticNews/~3/Bcf3RK5GM-s/e.....D02QU"
   ...
```

---

## Suggested Implementation Notes

- **Class Structure**:
    - `NewsAggregator`: Main class to orchestrate threads. Needs `processAllFeeds` and `buildIndex`.
    - `RSSFeedList`, `RSSFeed`, `HTMLDocument`: Provided classes for parsing.
    - `RSSIndex`: The inverted index (Not thread-safe! You must protect it).
- **Concurrency Strategy**:
    - Use `std::thread` for spawning threads.
    - Maintain a `std::map<std::string, std::unique_ptr<semaphore>>` for per-server limits.
    - Use `mutex` for critical sections (adding to index, checking visited URLs).
- **De-duplication Logic**:
    - Use `std::set_intersection` and `std::sort` for the smart intersection requirement.
    - For multiple variants on the same server with the same title: store only the intersection under the lexicographically smallest URL; do not index other URLs.
    - For a single variant: index tokens as-is.
    - Test with `static-alphabet-feed.xml` and local fixtures to verify intersection logic.

---

## Deliverables

- **Source Code**:
    - `news-aggregator.cc` / `news-aggregator.h`: Core logic and threading.
    - `rss-index.cc` / `rss-index.h`: Index implementation (likely modified for intersection logic).
    - `aggregate.cc`: Main entry point (should not need changes).
- **Functionality**:
    - Correctly built index.
    - No crashes or race conditions.
    - Adherence to thread limits (verify with logging if needed).

---

## Additional Requirements and Validation

- **Concurrency Constraints (Measured)**
  - The aggregator should be able to report observed peak concurrency when `--report-limits` is specified:
    - `MAX feed threads` must not exceed `5`.
    - `MAX article threads` must not exceed `18`.
    - `MAX per-server connections [<server>]` must not exceed `8` for any server.
  - These metrics are printed before entering the query REPL when `--report-limits` is present.

- **Index Construction Completeness**
  - Ensure all threads have joined and the `RSSIndex` is fully built before starting the REPL.

- **Smart Intersection Semantics**
  - For multiple variants sharing the same `server` and `title`:
    - Download all variants, compute the intersection of their token sets.
    - Store the final intersection under the lexicographically smallest URL only.
  - For a single variant: index tokens as-is.

- **Sorting and Output**
  - Search results sorted by frequency (descending), then by `Article` (URL) for ties.
  - Display at most 15 matches.

- **Resilience and Offline Mode**
  - The aggregator should not crash on network or parsing failures; errors are logged and processing continues where reasonable.
  - Must support local feed files (e.g., `small-feed.xml`, local fixtures) without network access.

- **CLI Behavior**
  - Support `--verbose`, `--quiet`, `--url <feed-list-xml>`.
  - Support `--report-limits` to print concurrency metrics.
  - Unknown flags should print usage and exit with a non-zero status.

- **Resource Management**
  - No memory leaks (use RAII where appropriate).
  - Proper cleanup of libxml resources (`xmlInitParser`, `xmlCleanupParser`, `xmlFreeDoc`, etc.)。

---

## How to Run

1) **Build**:
   ```bash
   make
   ```

2) **Run Sequential/Small Test**:
   ```bash
   ./aggregate --url small-feed.xml
   ```

3) **Run Full Test**:
   ```bash
   ./aggregate --url medium-feed.xml
   ```

4) **Sanity Check**:
   ```bash
   ./sanitycheck
   ```
