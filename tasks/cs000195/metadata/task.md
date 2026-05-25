# Lab 2: Memory Hierarchy - L2 Cache and DRAM

## 1. Introduction

In this lab, you will implement a memory hierarchy that includes an L2 cache and a DRAM-based main memory. We will fully specify the cycle-by-cycle behavior of the L2 cache and DRAM.

The L2 cache is decoupled from the pipeline. When a memory access misses in the L2 cache, it issues a request to the memory hierarchy. When the data is available from the L2 (on a hit) or main memory (on a miss), the memory hierarchy makes the data available to the processor. If the pipeline is still stalling on the missing data (i.e., no cancellation occurred), the data is inserted and the stall ends in the next cycle.

## 2. Your Task: Implementing L2 Cache and DRAM

### 2.1. Unified L2 Cache

The unified L2 cache is accessed for all memory operations (instruction fetches and data accesses).

#### Organization

- **Size**: 256 KB
- **Block size**: 32 bytes
- **Associativity**: 16-way set-associative
- **Number of sets**: 512 sets (calculated from size, block size, and associativity)
- **Set index**: bits [13:5] of the address

#### MSHRs

The L2 cache has **16 MSHRs** (miss-status holding registers), which is more than enough for our simple in-order pipeline. For every L2 cache miss, the L2 cache allocates an MSHR that keeps track of the miss. An MSHR consists of three fields:

1. Valid bit
2. Address of the cache block that triggered the miss
3. Done bit

You can assume that all bits are initialized to 0. When main memory serves an L2 cache miss, it sends a fill notification to the L2 cache that sets the done bit in the corresponding MSHR (i.e., if done = 1, then MSHR entry becomes invalid and valid bit = 0). The valid bit can be used to indicate that an MSHR entry contains a valid memory address.

#### Accessing the L2 Cache

Assume that the L2 cache has a large number of ports and that accesses to it are never serialized. When a memory access occurs, the L2 cache is "probed" immediately in the same cycle. Depending on whether the access hits or misses in the L2 cache, it is handled differently.

- **L2 Cache Hit**: The data is available immediately. The accessed cache block is promoted to the MRU position.

- **L2 Cache Miss**: Immediately, the L2 cache allocates an MSHR for the miss. After 5 cycles, the L2 cache sends a memory request to main memory (this models the latency between the L2 cache and the memory controller). When the memory request is served by main memory, the L2 cache receives a fill notification. After 5 cycles, the retrieved cache block is inserted into the L2 cache and the corresponding MSHR is freed (this models the latency between the memory controller and the L2 cache). In the same cycle, if the pipeline is stalled because of the cache block, then the data becomes available and the pipeline becomes unstalled in the next cycle.

#### Management Policies

- A new cache block is inserted into the L2 cache at the MRU position.
- For an L2 cache hit, a cache block is promoted to the MRU position.
- In the same cycle, there can be as many as two L2 cache accesses: one from the fetch stage and another from the memory stage. If they happen to hit in two different cache blocks that belong to the same set, then there is an ambiguity about which block is promoted to the MRU position. In this case, we assume that the memory stage accesses the L2 cache before the fetch stage: we promote the block that is requested by the fetch stage to the MRU position and the block that is requested by the memory stage to the MRU-1 position.
- The L2 cache adopts true LRU replacement.

#### Other

- Assume that the L2 cache is initially empty.
- An L2 cache access cannot be canceled once it has been initiated.
- We do not model dirty evictions that can occur from the L2 cache (to main memory). When a newly inserted cache block evicts a dirty cache block, we assume that the dirty cache block is written into main memory instantaneously. Furthermore, this happens without causing any side effects: the LRU ordering of the cache blocks in the corresponding cache set is not affected; in DRAM, buses/banks are not utilized and the row buffer status does not change.
- When the L2 cache does not have any free MSHRs remaining (which should not happen in our simple in-order pipeline), then a memory access cannot even probe the L2 cache. In other words, a free MSHR is a prerequisite for an access to the L2 cache, regardless of whether the access would actually hit or miss in the L2 cache. A freed MSHR can be re-allocated to another L2 cache miss in the same cycle.
- Once a cache miss (data or instruction) occurs, you are free to stall the pipeline until the request is served from L2 cache (hit) or memory (miss). However, if you have both an instruction cache miss and a data cache miss from an older instruction that is already in the MEM stage, then you can serve these two instructions by allocating one entry of MSHR per each miss.

### 2.2. Main Memory (DRAM)

#### Organization

The DRAM system has a single rank on a single channel, where the channel consists of the command/address/data buses. The rank has eight banks. Each bank consists of 64 K rows, where each row is 8 KB in size.

When accessing main memory:

- **Bank index**: bits [7:5] of the address
- **Row index**: bits [31:16] of the address

For example, the 32-byte cache block at address 0x00000000 is stored in the 0th row of the 0th bank. As another example, the 32-byte cache block at address 0x00000020 is stored in the 0th row of the 1st bank.

#### Memory Controller

The memory controller holds the memory requests received from the L2 cache in a request queue. The request queue can hold an infinite number of memory requests. In each cycle, the memory controller scans the request queue (including the memory requests that arrived during the current cycle) to find the requests that are "schedulable" (to be described later). If there is only one schedulable request, the memory controller initiates the DRAM access for that request. If there are multiple schedulable requests, the memory controller prioritizes the requests in the following order, which is similar to the FR-FCFS policy:

1. Requests that are row buffer hits are prioritized over requests that are row buffer misses.
2. Among requests with the same row buffer status (hit or miss), older requests are prioritized over newer requests.

A request is "schedulable" if the bank that the request targets is ready to accept a new command. A bank is ready to accept a new command if the bank has completed all previous commands that were issued to it.

#### DRAM Timing Parameters

- **tRCD (Row to Column Delay)**: 12 cycles
- **tCL (Column Access Strobe Latency)**: 12 cycles
- **tRP (Row Precharge Time)**: 12 cycles
- **tRAS (Row Active Time)**: 28 cycles

#### DRAM Access Protocol

When a memory request is scheduled:

1. **Row Buffer Hit**: If the requested row is already open in the row buffer, the memory controller issues a column read command. The data is available after tCL cycles. Then, the data is transferred over the bus in a burst. The bus width is 8 bytes, and a burst consists of 4 transfers (totaling 32 bytes, which matches the cache block size).

2. **Row Buffer Miss**: If the requested row is not open, the memory controller must:
   - First, if a row is currently open, issue a precharge command (takes tRP cycles)
   - Then, issue an activate command to open the new row (takes tRCD cycles)
   - Finally, issue a column read command (takes tCL cycles)
   - Then transfer the data in a burst (4 transfers)

The total latency for a row buffer miss is: tRP (if precharge needed) + tRCD + tCL + burst time.

#### Row Buffer Management

- Initially, all row buffers are closed (invalid).
- When a row is activated, it remains open until it is precharged.
- A precharge is needed only when switching to a different row in the same bank.

## 3. Lab Resources

### 3.1. Source Code

The source code that we provide for this lab includes a skeleton of the timing simulator that models a five-stage MIPS pipeline.

**Do NOT modify any files or folders unless explicitly specified in the list below:**

- **Makefile**: Do not modify
- **run.py**: Script that runs your simulator and compares it against the baseline simulator. You may need to modify this script for your own debugging. However, your submission must work with the unmodified version.
- **lib/**: Source code (Modifiable; feel free to add more files)
  - **pipe.c**: Your simulator (Modifiable)
  - **pipe.h**: Your simulator (Modifiable)
  - **mips.h**: MIPS related pound defines
  - **shell.c**: Interactive shell for your simulator
  - **shell.h**: Interactive shell for your simulator
- **inputs/**: Example test inputs for your simulator (Modifiable; feel free to add more files)

### 3.2. Makefile

We provide a Makefile that automates the compilation and verification of your simulator.

The first time you use the Makefile you should compile the baseline simulator:

```bash
$ make basesim
```

This will generate `basesim`, which is the baseline simulator corresponding to the code we provide. You can use it to verify the output of a program you run on your simulator. Note that the output of a program should always match the output obtained by running the program on the baseline simulator. However, the execution time of a program on the two simulators will not be same after the addition of the L2 Cache and the DRAM.

To compile your simulator:

```bash
$ make
```

To compile your simulator and check it against the baseline simulator using one or more test inputs:

```bash
$ make run INPUT=inputs/inst/addiu.x
$ make run INPUT=inputs/inst/*.x
$ make run
```

## 4. Getting Started & Tips

### 4.1. Lecture Materials

To get started with this lab, we highly recommend you to study the following relevant materials from Digital Design and Computer Architecture course, which can be accessed at: https://safari.ethz.ch/digitaltechnik/spring2022/doku.php?id=schedule

- L22: Memory Organization and Memory Technology
- L23: Memory Hierarchy and Caches
- L24: Advanced Caches

### 4.2. The Goal

We provide you with a skeleton of the timing simulator that models a five-stage MIPS pipeline: `pipe.c` and `pipe.h`. As it is, the simulator is already architecturally correct: it can correctly execute any arbitrary MIPS program that only uses the implemented instructions. When the simulator detects data dependences, it correctly handles them by stalling and/or bypassing. When the simulator detects control dependences, it correctly handles them by stalling the pipeline as necessary.

By executing the following command, you can see that your simulator (`sim`) does indeed have identical architectural outputs (e.g., register values) as the baseline simulator (`basesim`) for all the test inputs that we provide in `inputs/`.

```bash
$ make run
```

Your job is to model accurately the timing effects of the L2 Cache and the DRAM in your timing simulator.

### 4.3. Studying the Timing Simulator

Please study `pipe.c` and `pipe.h` in detail.

The simulator models each pipeline stage as a separate function - e.g., `pipe_stage_fetch()`. The simulator models the state of the pipeline as a collection of pointers to `Pipe_Op` structures (defined in `pipe.h`). Each `Pipe_Op` represents one instruction in the pipeline by storing all of the necessary information about the instruction that is needed by the simulator. A `Pipe_Op` structure is allocated when an instruction is fetched. It then flows through the pipeline and eventually arrives at the last stage (writeback), where it is deallocated once the instruction completes. To elaborate, each stage receives a `Pipe_Op` from the previous stage, processes the `Pipe_Op`, and passes it down to the next stage. The simulator models pipeline stalls by stopping the flow of `Pipe_Op` structures and pipeline flushes by deallocating the `Pipe_Op` structures at different stages.

### 4.4. Tips

- Please do not distribute the provided program files. These are for exclusive individual use of each student of the Computer Architecture course. Distribution and sharing violates the copyright of the software provided to you.
- Read this handout in detail.
- If needed, please ask questions to the TAs using the corresponding online Q&A forum.
- When you encounter a technical problem, please first read the error messages. A search on the web can usually solve many debugging issues, and error messages.

## 5. Submission

You should submit all the files needed to compile and simulate your code in a single tarball (with the name `lab2_YourSurname_YourName.tar.gz`). Please include comments to explain what you have done in the simulator code.

The structure of the submitted tarball should look like:

```
lab2/
├── README (optional): any special instructions you have for us
├── task_1/
│   ├── Makefile
│   ├── run.py
│   ├── lib/
│   └── inputs/
└── extra_credit/ (optional)
    ├── report_writeback_refresh.pdf
    ├── Makefile
    ├── run.py
    ├── lib/
    └── inputs/
```

Please feel free to include a brief README to describe any nuances of building/running your project that we should be aware of when grading your submission.
