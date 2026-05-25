## Background

This is the first in a series of labs in which you'll build a fault-tolerant key/value storage system. In this lab you'll implement Raft, a replicated state machine protocol.

*   A replicated service achieves fault tolerance by storing complete copies of its state (i.e., data) on multiple replica servers.
*   Raft organizes client requests into a sequence, called the log, and ensures that all replica servers see the same log.
*   Raft will continue to operate as long as at least a majority of the servers are alive and can talk to each other.

In this lab you'll implement Raft as a Go object type with associated methods, meant to be used as a module in a larger service. Your implementation must follow the design in the extended Raft paper. You'll implement most of what's in the paper, including saving persistent state and reading it after a node fails and then restarts. You will not implement cluster membership changes (Section 6).

### The code

Implement Raft by adding code to `raft/raft.go`. Your implementation must support the following interface:

```go
// create a new Raft server instance:
rf := Make(peers, me, persister, applyCh)

// start agreement on a new log entry:
rf.Start(command interface{}) (index, term, isleader)

// ask a Raft for its current term, and whether it thinks it is leader
rf.GetState() (term, isLeader)
```

The service expects your implementation to send an `ApplyMsg` for each newly committed log entry to the `applyCh` channel argument to `Make()`.

### Part 3A: leader election (moderate)

Implement Raft leader election and heartbeats (`AppendEntries` RPCs with no log entries). The goal is for a single leader to be elected and for a new leader to take over if the old leader fails.

*   Add the state for leader election to the `Raft` struct in `raft.go` and define a struct for log entries.
*   Modify `Make()` to create a background goroutine that kicks off leader election using a loop and `time.Sleep()`.
*   Implement `RequestVote()` and `AppendEntries()` RPC handlers.
*   The leader must send heartbeat RPCs no more than ten times per second.
*   Raft must elect a new leader within five seconds of the failure of the old leader.

### Part 3B: log (hard)

Implement the leader and follower code to append new log entries.

*   Raft log is 1-indexed, but it is suggested to view it as 0-indexed with a dummy entry at index 0 (term 0).
*   Implement `Start()`, then send and receive new log entries via `AppendEntries` RPCs.
*   Implement the election restriction (Section 5.4.1 in the paper).
*   Avoid continuous loops without pausing; use Go's condition variables or `time.Sleep(10 * time.Millisecond)`.

### Part 3C: persistence (hard)

Raft must keep persistent state that survives a reboot, including state mentioned in the paper.

*   Use a `Persister` object to save and restore state via `ReadRaftState()` and `Save()`.
*   Complete `persist()` and `readPersist()` using the `labgob` encoder.
*   Implement the optimization to back up `nextIndex` by more than one entry at a time:
    *   **Case 1**: Leader doesn't have `XTerm` -> `nextIndex = XIndex`.
    *   **Case 2**: Leader has `XTerm` -> `nextIndex = (index of leader's last entry for XTerm) + 1`.
    *   **Case 3**: Follower's log is too short -> `nextIndex = XLen`.

### Part 3D: log compaction (hard)

Modify Raft to cooperate with services that store "snapshots" of their state to discard old log entries.

*   Implement `Snapshot(index int, snapshot []byte)` to discard log entries before the given point.
*   Implement the `InstallSnapshot` RPC for leaders to catch up lagging followers. Send the entire snapshot in a single RPC (do not implement offset-based splitting).
*   Ensure snapshots only advance the service's state; do not move it backwards.
*   Discard old log entries in a way that allows the Go garbage collector to free memory (ensure no reachable references exist).

### Implementation Advice

*   **Concurrency**: Create a goroutine with a loop that calls `time.Sleep()`. Don't use Go's `time.Timer` or `time.Ticker` as they are difficult to use correctly.
*   **Termination**: The tester calls `rf.Kill()` on shutdown. Use `rf.killed()` to check this in all loops to avoid confusing messages.
*   **RPCs**: Go RPC sends only struct fields starting with capital letters. `labgob` will warn you about this; do not ignore the warnings.
*   **Communication**: Your Raft instances must interact only with RPC (`labrpc`); they are not allowed to use shared variables or files.

---

## Special reminders for this repository (offline overrides)

- **Execution**: Run your Raft implementation via the tester: `go test -run 3A`.
- **Race Condition**: Ensure your code consistently passes tests with the `-race` flag.
- **Verification**:
  - Run individual parts: `go test -run 3A`, `go test -run 3B`, etc.
  - Final check: Each "Passed" line indicates successful verification. Your solution must pass all tests within the time limits set by the grading script.
