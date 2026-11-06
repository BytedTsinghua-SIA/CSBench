## Task Instructions

https://pdos.csail.mit.edu/6.824/labs/lab-mr.html

### Task Source

MIT 6.5840 / 6.824 Distributed Systems - MapReduce Lab

### Task Overview

Implement a distributed MapReduce system consisting of a coordinator and workers. The coordinator is responsible for distributing map and reduce tasks to workers, while workers execute the tasks and report results back. The system must handle worker crashes gracefully and ensure that all tasks are completed exactly once.

### Detailed Requirements

#### 1. Coordinator Implementation (`src/mr/coordinator.go`)

The coordinator manages the MapReduce job and must:

- Store the map task state (idle, in-progress, completed)
- Store the reduce task state (idle, in-progress, completed)
- Assign map tasks to workers via RPC
- Assign reduce tasks to workers via RPC (only after all map tasks complete)
- Track task completion via RPC reports from workers
- Detect crashed workers and reassign their tasks (tasks taking >10 seconds)
- Implement a `Done()` method that returns true when all jobs are finished

RPC handlers to implement:
- `RequestJob`: Worker calls this to get a new task assignment
- `ReportJob`: Worker calls this to report task completion

#### 2. Worker Implementation (`src/mr/worker.go`)

The worker executes MapReduce tasks and must:

- Request jobs from the coordinator via RPC
- Execute map tasks by:
  - Reading the input file
  - Calling the user-defined map function
  - Partitioning output into nReduce intermediate files
  - Using the format `mr-{mapTaskId}-{reduceTaskId}` for intermediate files
- Execute reduce tasks by:
  - Reading all intermediate files for the assigned reduce task
  - Sorting intermediate data by key
  - Calling the user-defined reduce function for each key
  - Writing output to `mr-out-{reduceTaskId}`
- Report task completion back to coordinator
- Exit when coordinator reports all jobs are done

#### 3. RPC Definitions (`src/mr/rpc.go`)

Define the following RPC structures:

```go
type JobType int
const (
    MapJob JobType = iota
    ReduceJob
    WaitJob
    ExitJob
)

type JobStatus int
const (
    Idle JobStatus = iota
    InProgress
    Completed
)

type RequestJobArgs struct {
    WorkerID int
}

type RequestJobReply struct {
    JobType    JobType
    JobID      int
    InputFile  string
    NReduce    int
    ReduceTask int
}

type ReportJobArgs struct {
    WorkerID  int
    JobType   JobType
    JobID     int
    Succeeded bool
}

type ReportJobReply struct {
    Continue bool
}
```

#### 4. Important Implementation Notes

- Use `ihash(key) % nReduce` to partition map output to reduce tasks
- Write intermediate files atomically (write to temp file, then rename)
- Workers should only exit when coordinator reports `ExitJob`
- Coordinator must handle the case where workers crash (RPC timeout)
- Map tasks must complete before any reduce tasks start
- The coordinator's crash detection should only reassign tasks that have been in-progress for more than 10 seconds

#### 5. Testing

The system will be tested with:
- Word count application (wc.so)
- Document indexer application (indexer.so)
- Parallelism tests (map and reduce)
- Job count verification
- Early exit verification
- Crash recovery simulation

All tests must pass for the implementation to be considered correct.
