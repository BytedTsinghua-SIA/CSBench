## Project 3: Joins and Query Optimization

### Overview
In this project you will implement several join algorithms and a limited
version of the Selinger optimizer in RookieDB. In Part 1 you will extend the
query execution engine with disk-aware join and sort operators. In Part 2 you
will implement plan space search to choose a lower-cost join order.

This assignment follows the volcano iterator model: operators are layered, and
each operator pulls tuples from its input operator(s) on demand rather than
materializing full intermediate results.

#### Suggested Reading
- Part 1:
  - `common/iterator`
  - Join operators (`query/join` and `query/JoinOperator.java`)
  - `query/disk`
- Part 2:
  - Scan and special operators (`query/`)
  - `query/QueryPlan.java`

### Understanding the Skeleton Code
- `common/iterator`: contains the `BacktrackingIterator` interface, which
  supports `markPrev`/`markNext` and `reset` for iterator backtracking.
  `ArrayBacktrackingIterator` provides a concrete implementation you will use
  when implementing joins.
- `query/QueryOperator.java`: base class of all query operators. Operators form
  a volcano-style iterator pipeline; each operator is `Iterable<Record>` and
  pulls tuples from its input(s) on demand.
- `query/join/JoinOperator.java`: base class for join operators. It provides
  helper methods for working with the current transaction and temporary tables.
  For Part 1, you should not interact with `Table` or `TransactionContext`
  directly (other than passing them into provided helper methods).
- Scan operators:
  - `SequentialScanOperator`: scans all records of a table.
  - `IndexScanOperator`: scans records matching a predicate on an indexed
    column.
- Special operators:
  - `SelectOperator`: filters records from a source operator.
  - `ProjectOperator`: projects columns (and optionally aggregates, out of
    scope for this project).
  - `SortOperator`: yields records from the source operator in sorted order
    (you will implement external sort in Part 1).
- `query/disk`: contains disk-backed helpers used by Grace Hash Join and
  external merge sort.
  - `Partition`: represents a hash partition, buffering reads/writes so that at
    most one page is needed in memory at a time.
  - `Run`: represents a sorted run used by external mergesort.
- `query/QueryPlan.java`: represents a user query. Users build queries by
  calling methods like `join()`/`select()` and then call `execute()` to obtain
  an iterator over results. In Part 2, you will replace the naive execution
  strategy with an optimizer-driven one.

### QueryPlan Predicates
- `QueryPlan.SelectPredicate`: stores single-table selection predicates (table,
  column, operator, constant value).
- `QueryPlan.JoinPredicate`: stores equijoin conditions (left table/column,
  right table/column). All joins in this project are equijoins.

### Important Implementation Details
- Streaming: unless explicitly permitted in the skeleton comments, operators
  should stream their inputs rather than materializing them in memory.
- Buffer constraints: join and sort implementations must not exceed the number
  of buffers the algorithm allows. Holding more pages than permitted may result
  in no credit.
- Terminology: in this project, a page is the unit of transfer between memory
  and disk, and a block is a set of one or more pages.
- Iterator usage: for all iterators you implement, you may assume `hasNext()`
  is always called before `next()`.
- Input validity: public tests will not include invalid inputs (null objects,
  negative buffer sizes, too-small buffers, invalid queries, etc.).
- No concurrent mutations: you do not need to handle underlying relations being
  mutated during the execution of your operators.

### Interface for Querying
Queries are built via `QueryPlan` and executed in the volcano model. After
`execute()` is called, you can inspect the final plan:

```java
Iterator<Record> result = query.execute();
QueryOperator finalOperator = query.getFinalOperator();
System.out.println(finalOperator.toString());
```

Example output:

```
-> SNLJ on S.sid=E.sid (cost=6)
        -> Seq Scan on S (cost=3)
        -> Seq Scan on E (cost=3)
```

### Tasks

#### Part 1: Join Algorithms

##### Task 1: Nested Loop Joins

Implement Block Nested Loop Join in `query/join/BNLJOperator.java`.
`SNLJOperator` is provided as an example of how join pseudocode translates to
code, but it does not manage pages explicitly and should not be copied.

`PNLJOperator` is implemented as
a special case of BNLJ with `B = 3`, so it will not work correctly until BNLJ
is correct.

You will implement `fetchNextRecord()` (and may implement the suggested helper
methods `fetchNextLeftBlock` and `fetchNextRightPage`). Your logic should cover
the major control-flow cases:
- Right page iterator still has records.
- Right page exhausted but left block still has records.
- Both exhausted, but there are more right pages.
- Right pages exhausted for this left block, but there are more left blocks.

After completing this task you should pass all tests in
`TestNestedLoopJoin`.

##### Task 2: Hash Joins

Implement Grace Hash Join in `query/join/GHJOperator.java`. A Simple Hash Join
implementation is provided in `SHJOperator.java`; read it to understand the
partitioning and probing structure.

You will implement:
- `partition`
- `buildAndProbe`
- `run`

You will also fill in `getBreakSHJInputs` and `getBreakGHJInputs` to provide
test inputs that demonstrate when SHJ fails but GHJ succeeds, and when GHJ
must fail (as required by the public tests).

After completing this task you should pass all tests in
`TestGraceHashJoin`.

There are no hidden tests for Grace Hash Join; grading for GHJ is based solely
on the released public tests.

##### Task 3: External Sort

Implement external merge sort in `query/SortOperator.java`. Sorting is a
prerequisite for Sort Merge Join.

You will implement:
- `sortRun(run)`: in-memory sort for pass 0.
- `mergeSortedRuns(runs)`: merge multiple sorted runs into one sorted run.
- `mergePass(runs)`: perform one merge pass over the list of runs.
- `sort()`: run external mergesort end-to-end and return the final sorted run.

Each method may be tested independently, so implement each one exactly as
specified. You may add helper methods as needed.

After completing this task you should pass all tests in
`TestSortOperator`.

##### Task 4: Sort Merge Join

Implement Sort Merge Join in `query/join/SortMergeOperator.java` by completing
`fetchNextRecord()` in the `SortMergeIterator` inner class.

For simplicity, do not implement the “merge final pass while joining”
optimization. Use `SortOperator` to sort both inputs first.

Do not add a new public method to `SortOperator` and call it from
`SortMergeOperator`; the two implementations may be tested independently.

After completing this task you should pass all tests in
`TestSortMergeJoin`.

##### Part 1 Submission Checklist
If everything is complete, you should be passing all tests in:
- `database.query.TestNestedLoopJoin`
- `database.query.TestGraceHashJoin`
- `database.query.TestSortOperator`
- `database.query.TestSortMergeJoin`

#### Part 2: Query Optimization

##### Task 5: Single Table Access Selection (Pass 1)

Implement `QueryPlan#minCostSingleAccess` in `query/QueryPlan.java`.

For a single table, choose the lowest estimated cost access method between:
- A sequential scan (`SequentialScanOperator`) and
- An index scan (`IndexScanOperator`) when there is an index on a column with
  an eligible selection predicate.

After choosing the access operator, push down all eligible single-table
selection predicates using the provided helper (`addEligibleSelections`). The
result should be a scan operator followed by zero or more `SelectOperator`s.

After completing this task you should pass all tests in
`TestSingleAccess`.

##### Task 6: Join Selection (Pass i > 1)

Implement `QueryPlan#minCostJoins` in `query/QueryPlan.java`.

This method performs pass i of the dynamic programming search for left-deep
join trees. Given a mapping from sets of i-1 tables to their best plans, return
the best plan for each valid set of i tables, excluding Cartesian products.
Use the join predicates provided via `QueryPlan#join` to determine which joins
are legal.

Plan space constraints for this project:
- Search only left-deep trees.
- Avoid Cartesian products where possible; for grading, treat Cartesian products
  as disallowed.

Do not add additional selection predicates in this method; remaining predicates
at this stage correspond to join conditions in this simplified database.

After completing this task you should pass
`TestOptimizationJoins#testMinCostJoins`.

##### Task 7: Optimal Plan Selection

Implement `QueryPlan#execute` in `query/QueryPlan.java`.

This method is the optimizer driver: use `minCostSingleAccess` and
`minCostJoins` to search for the best overall plan for all tables in
`tableNames`, then add any remaining query operators (projection, group by,
etc.) using the provided private helper methods.

After completing this task you should pass all the tests in the
`database.query.*` package.

##### Part 2 Submission Checklist
If everything is complete, you should be passing all tests in:
- `database.query.TestNestedLoopJoin`
- `database.query.TestGraceHashJoin`
- `database.query.TestSortOperator`
- `database.query.TestSingleAccess`
- `database.query.TestOptimizationJoins`
- `database.query.TestBasicQuery`

#### Modification Constraints
- You may not modify the signature of provided methods or classes.
- For Part 2, only modify `query/QueryPlan.java`.
