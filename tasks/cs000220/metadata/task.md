## Project 4: Concurrency

### Overview
In this project you will implement multigranularity locking and two-phase
locking in RookieDB. In Part 1 you will build a lock manager that supports
multiple lock types and queues conflicting requests. In Part 2 you will add
multigranularity support, a declarative locking interface, and integrate
locking with transaction execution.

#### Suggested Reading
- Part 1:
  - `concurrency/LockType.java`
  - `concurrency/LockManager.java`
- Part 2:
  - `concurrency/LockContext.java`
  - `concurrency/LockUtil.java`
  - `memory/Page.java`
  - `table/PageDirectory.java`
  - `table/Table.java`
  - `Database.TransactionContextImpl` in `Database.java`
  - `cli/CommandLineInterface.java` and `Server.java`

### Understanding the Skeleton Code
- `concurrency/LockType.java`: defines all lock types (NL, S, X, IS, IX, SIX)
  and provides helpers to reason about compatibility, hierarchy, and
  substitutability of lock types.
- `concurrency/LockManager.java`: manages locks for individual resources.
  Tracks locks held by each transaction and locks/queues for each resource,
  and is responsible for acquiring, releasing, promoting, and queueing
  requests while blocking/unblocking transactions.
- `concurrency/LockContext.java`: represents a single resource in the
  multigranularity hierarchy (database, table, page). Enforces multigranularity
  constraints on top of `LockManager` and provides operations like acquire,
  release, promote, and escalate at the context level.
- `concurrency/LockUtil.java`: provides declarative helper
  `ensureSufficientLockHeld` which acquires and promotes locks (including
  ancestor intent locks) so that the current transaction can safely read or
  write a resource.
- `concurrency/ResourceName.java`: identifies lockable resources and encodes
  the hierarchy (ancestors and descendants) used by `LockContext`.
- `common/transaction/Transaction.java`: represents a database transaction and
  exposes methods to block/unblock when waiting for locks.
- `memory/Page.java`: defines `Page.PageBuffer`, through which all reads and
  writes to pages go. You will add locking to `get` and `put` here.
- `table/PageDirectory.java`: manages mapping from logical records to physical
  pages and provides helpers for finding or allocating pages with free space.
- `table/Table.java`: implements high-level table operations such as scanning,
  inserting, updating, and deleting records. You will integrate locking into
  several of these operations.
- `Database.TransactionContextImpl`: wraps a transaction’s view of the
  database and is responsible for releasing all locks at the end of a
  transaction during cleanup.
- `cli/CommandLineInterface.java` and `Server.java`: provide an interactive CLI
  and server mode for manually running transactions and observing locks.

### Tasks

#### Part 1: Queuing

##### Task 1: LockType

Before implementing the queuing logic, you will complete the lock type
reasoning helpers in `LockType`.

For the purposes of this project, a transaction with:

- `S(A)` can read `A` and all descendants of `A`.
- `X(A)` can read and write `A` and all descendants of `A`.
- `IS(A)` can request shared and intent-shared locks on all children of `A`.
- `IX(A)` can request any lock on all children of `A`.
- `SIX(A)` combines `S` and `IX`: the transaction can read `A` and its
  descendants, and can request `IX`/`X` locks on children, but may not acquire
  `S`, `IS`, or `SIX` locks on children (these would be redundant).

You will implement the following methods in `LockType`:

- `compatible(A, B)`: returns whether lock type `A` is compatible with lock
  type `B` on the same resource. Two transactions can both hold `S` on a
  resource, but two `X` locks conflict.
- `canBeParentLock(A, B)`: returns whether holding lock `A` on a resource
  allows a transaction to acquire lock `B` on a child. For example, acquiring
  `S` on a table requires at least `IS` on its parent (database), so
  `canBeParentLock(IS, S)` is true.
- `substitutable(substitute, required)`: returns whether a transaction that
  requested `required` could safely be given `substitute` instead. The
  substitute must allow all actions that `required` permits (for example,
  `substitutable(X, S)` is true but `substitutable(S, X)` is false).

After completing this task you should pass all tests in
`TestLockType.java`.

##### Task 2: LockManager

`LockManager` handles locking for individual resources without considering the
hierarchy. It is the single source of truth for which locks each transaction
holds. In this task you will implement the core lock manager operations and
queuing behavior.

You will complete the following methods in `LockManager`:

- `acquireAndRelease`: atomically acquires one lock and releases zero or more
  existing locks for the same transaction. This operation has priority over
  queued requests: it may bypass an existing queue or be inserted at the front
  of the queue if it cannot be granted immediately.
- `acquire`: standard lock acquisition. Grants the requested lock immediately
  if there is no queue for the resource and the request is compatible with all
  existing locks. Otherwise, enqueues the request at the back of the queue and
  blocks the transaction. Implicit upgrades are not allowed (for example,
  requesting `X` on a resource where the transaction already holds `S` is
  invalid).
- `release`: standard lock release. Allows a transaction to release a lock it
  currently holds on a resource and then processes the resource’s queue.
- `promote`: explicit lock promotion/upgrade for a lock held by the
  transaction on a resource. Replaces the held lock with a stronger one on the
  same resource. This operation has priority over queued requests (similar to
  `acquireAndRelease`) and should be inserted at the front of the queue if it
  cannot be granted immediately. Promotions to `SIX` are disallowed and must
  instead go through `acquireAndRelease` so redundant descendant locks can be
  released.
- `getLockType`: returns the type of lock that a transaction currently holds
  on a specific resource.

Lock requests that cannot be satisfied immediately are placed on the per-
resource queue. After any lock is released on a resource, you must process its
queue in order:

- Consider the request at the front of the queue. If it does not conflict with
  any existing locks, grant it, release any locks it specifies to be released,
  and unblock the transaction.
- Repeat this process until the first request on the queue cannot be granted
  or the queue becomes empty.

All accesses to `LockManager`’s internal state for a given call must occur
inside a single `synchronized (this)` block. To block a transaction, call
`Transaction#prepareBlock` inside the synchronized block, then call
`Transaction#block` outside the block.

After completing the Part 1 tasks you should pass all tests in
`TestLockType.java` and at least the first five tests of
`TestLockManager.java`.

#### Part 2: Multigranularity

##### Task 3: LockContext

`LockContext` represents a single resource in the multigranularity hierarchy
and enforces multigranularity locking rules on top of `LockManager`. Contexts
are linked as parents and children (for example, database → table → page) and
all share a single underlying `LockManager`.

You will implement the following methods of `LockContext`:

- `acquire`: acquires a lock on this context via the underlying
  `LockManager` after checking multigranularity constraints. For example, a
  transaction must hold the appropriate intent lock on the parent before
  acquiring a lock here, and acquiring `IS`/`S` on a descendant when an
  ancestor has `SIX` is considered invalid.
- `release`: releases a lock on this context via the underlying
  `LockManager` after ensuring multigranularity constraints will still hold.
  For example, a transaction cannot release an intent lock on an ancestor if
  it still holds incompatible locks on descendants.
- `promote`: promotes a held lock on this context to a stronger one, enforcing
  all multigranularity constraints. Promotions from `IS`/`IX`/`S` to `SIX`
  must simultaneously release all descendant `S`/`IS` locks, since these would
  be redundant under `SIX`. Promotion to `SIX` is disallowed if an ancestor
  already holds `SIX`.
- `escalate`: replaces all locks held by the transaction on descendants of
  this context with a single lock at this level. Escalation always produces
  either an `S` or `X` lock (not intent locks) and chooses the least
  permissive type that still allows all previously permitted actions. You must
  perform escalation with a single mutating call to `LockManager` and only use
  information about the current transaction.
- `getExplicitLockType`: returns the lock type explicitly held on this
  resource by a transaction, or `NL` if none.
- `getEffectiveLockType`: returns the lock type a transaction effectively has
  on this resource, taking ancestor locks into account. For example, an `X`
  lock on the database implies `X` on all tables, and a `SIX` lock on the
  database implies an effective `S` on descendants.

Helpful methods include `LockType` helpers, `LockManager` methods,
`ResourceName#parent`, `ResourceName#isDescendantOf`, and the provided
`hasSIXAncestor`, `sisDescendants`, and `fromResourceName` helpers.

##### Task 4: LockUtil

`LockUtil` provides a declarative interface for ensuring that the current
transaction has sufficient locks to perform an operation.

You will implement:

- `ensureSufficientLockHeld(context, LockType lockType)`: ensures that the
  transaction returned by `Transaction.getTransaction()` has enough
  permissions to perform the requested operation (for example, `S` for
  reading, `X` for writing) on the resource represented by `context` and all
  descendants. This method should:
  - Acquire or promote ancestor intent locks as needed.
  - Acquire, promote, or escalate locks on `context` as needed.
  - Never reduce a transaction’s existing permissions, and grant as little
    additional permission as possible (for example, prefer `S` over `X` when
    both would work).

It is often helpful to conceptually split the logic into two phases: first
ensuring appropriate ancestor locks, then acquiring or adjusting the lock on
the target resource. You will need to use both promotion and escalation.

##### Task 5: Two-Phase Locking

In this task you will integrate your locking system with transaction
execution, implementing Strict Two-Phase Locking (2PL).

**Acquisition Phase**

- **Reads and writes**: All reads and writes to pages go through
  `Page.PageBuffer`. Modify `get` and `put` to acquire the least permissive
  locks needed on the page (and ancestors) before accessing it.
- **Scans**: For table scans, it is more efficient to acquire a single lock on
  the table rather than many fine-grained page locks. Modify `ridIterator` and
  `recordIterator` to acquire an appropriate table-level lock before scanning.
- **Write optimization**: When you know a page will be modified, you can skip
  acquiring `IS`/`S` first and instead directly request `IX`/`X`. Modify
  `PageDirectory#getPageWithSpace`, `Table#updateRecord`, and
  `Table#deleteRecord` to request the appropriate locks upfront.

Note that after you add acquisition logic, additional tests may fail until you
complete the release phase.

**Release Phase**

- Implement Strict 2PL by releasing locks only when a transaction finishes.
  Modify `Database.TransactionContextImpl.close` to release all locks the
  transaction acquired using `LockContext#release` (not `LockManager#release`)
  while preserving multigranularity constraints. Locks should be released from
  the bottom of the hierarchy upward so that constraints are never violated.

After implementing acquisition and release you should pass all tests in
`TestDatabaseDeadlockPrecheck.java` and `TestDatabase2PL.java`.

#### Putting It All Together

Once you have a working implementation of Parts 1 and 2, you can interact with
the database via the CLI to observe locks in action.

- In `CommandLineInterface.java`, uncomment the line that enables locking and
  comment out the line that disables it, then run the CLI.
- Begin a transaction and issue queries such as a join over the provided demo
  tables (Students, Courses, Enrollments). Use the `\locks` command to see the
  locks held by the current transaction.
- Perform modifications such as `INSERT` to observe lock promotions (for
  example, acquiring `X` on a page after previously reading it).
- You can also run `Server.java` and connect via the provided client script to
  experiment with concurrent transactions.

After completing this project you should pass all tests under
`database.concurrency.*`, as well as `TestDatabaseDeadlockPrecheck` and
`TestDatabase2PL`.

#### Modification Constraints
- You may not modify the signature of any provided methods or classes.
- For Part 1, only modify code in the `concurrency` directory.
- For Part 2, you will primarily modify `concurrency` classes and the
  specified files in `memory`, `table`, `cli`, and `Database`.
