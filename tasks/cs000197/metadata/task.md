### Lab 4: Memory Request Scheduling (Condensed Description)

### 1. Overview

In this lab, you will implement and evaluate two memory scheduling policies in Ramulator:

- **ATLAS** (Adaptive per-Thread Least-Attained-Service)
- **BLISS**

You will extend the provided Ramulator code (a fast, extensible DRAM simulator) with these two schedulers, and compare them against existing policies (FCFS, FRFCFS, FRFCFS Cap) in terms of performance and fairness.

---

### 2. Ramulator Usage (Short Guide)

- Ramulator is a cycle-accurate DRAM simulator that supports multiple DRAM standards (e.g., DDR4, LPDDR4, WideIO) and includes a simplified out-of-order processor front-end for CPU Trace Driven simulation.
- The provided version already implements several scheduling policies (e.g., FCFS, FRFCFS, FRFCFS Cap) in the memory controller. Your job is to add ATLAS and BLISS on top of this infrastructure.

#### 2.1 Building and Running

- **Build**: in the Ramulator root directory:
  - `make -j`
- After a successful build, an executable `ramulator` is generated. Running it without arguments prints a help message:
  - `./ramulator`
- Typical command format:
  - `./ramulator <configs-file> --mode=cpu,dram [--stats <filename>] <trace-filename1> <trace-filename2> ...`

#### 2.2 Simulation Modes

Ramulator supports three modes (this lab only uses CPU Trace Driven):

- **Memory Trace Driven**: uses a memory request trace; mainly for functionality testing. Not used in this lab.
- **Gem5 Driven**: Ramulator acts as the main memory subsystem of the gem5 simulator. Not used in this lab.
- **CPU Trace Driven (used in this lab)**:
  - Directly reads CPU instruction trace files and simulates a simplified out-of-order core plus DRAM system.
  - Each trace line can have one of several formats (including CPU instruction count, read/write address, etc.), as described in the original handout.
  - For cache-filtered traces, **caches must not be instantiated** in the configuration.

#### 2.3 Example Run and Stats Output

- Example command:
  - `./ramulator configs/test-config.cfg --mode=cpu cpu.trace`
  - After completion, a stats file like `DDR4.stats` is generated.
- By default, the stats filename is `<standard>.stats` (e.g., `DDR4.stats`), but you can override it with `--stats <filename>`.
- You should familiarize yourself with the existing statistics, and later **add a new statistic for Instruction Throughput**.

#### 2.4 Configuration Files

- Predefined configurations are in the `configs/` directory, e.g.:
  - `DDR3-config.cfg`, `DDR4-config.cfg`, `GDDR5-config.cfg`, `HBM-config.cfg`, `WideIO2-config.cfg`, `PCM-config.cfg`, `STTMRAM-config.cfg`, `SALP-config.cfg`, `DSARP-config.cfg`, etc.
- Important parameters (you should understand them but only modify what the assignment explicitly allows):
  - **Memory-specific**: `standard` (e.g., DDR4), `channels`, `ranks`, `speed` (e.g., DDR4 2400R), `org` (bank/row/column organization), etc.
  - **Core-specific**: number of cores is determined by the number of trace files specified on the command line; `cache` controls the cache hierarchy. Since you are given cache-filtered traces, **do not enable caches**.
  - **Simulation-specific**:
    - `expected_limit_insts`: simulation ends when all cores retire at least this many instructions.
    - `early_exit` must remain `off`, otherwise simulation may stop when any single core reaches the limit.

#### 2.5 Multi-programmed Workloads

- You can simulate multi-programmed workloads by specifying multiple trace files on the command line; Ramulator will assign one core to each trace.
- The lab provides two types of CPU traces:
  - high memory intensity
  - low memory intensity
- Example multi-programmed command:
  - `./ramulator configs/DDR4-config.cfg --mode=cpu --stats multi-programmed-simulation.stats ./traces/high-mem-intensity.trace ./traces/low-mem-intensity.trace`

#### 2.6 Code Organization (Key Modules in Ramulator)

Only high-level information relevant to the lab:

- `Main.cpp`:
  - Reads the configuration file and instantiates processor cores and memory controllers.
  - Drives both processor and memory in CPU Trace Driven mode.
- Processor side:
  - Each cycle, `proc.tick()`:
    - Each core reads instructions from its trace file.
    - On a memory instruction, the core calls `send()` to send the request to the appropriate cache/memory controller.
    - When a request completes, the corresponding `callback()` notifies the issuing core.
- Memory side (one controller per DRAM channel):
  - `memory.tick()` calls each controller’s tick.
  - Main tasks:
    - Check and serve completed reads (calling the request’s `callback`).
    - Trigger periodic refreshes via the refresh module.
    - **Use the scheduler to select a request from the queue, then have the controller issue the corresponding DRAM command (e.g., READ, ACTIVATE) and update DRAM state.**
- DRAM timing:
  - Each DRAM standard has a header file (e.g., `DDR4.h`) that defines timing parameters (e.g., `SpeedEntry`).
- Scheduler entry point:
  - `Scheduler.h` specifies the current scheduling policy type. By default it is `FRFCFS_Cap`:
    - `type = Type::FRFCFS_Cap; // Change this line to change scheduling policy`

---

### 3. Task 1/3: Implementing the ATLAS Scheduler

- Goal: implement the **ATLAS (Adaptive per-Thread Least-Attained-Service)** memory scheduler in Ramulator.
- High-level idea (as in the original description, without prescribing implementation details):
  - Periodically rank threads according to the amount of service they have received from the memory controllers.
  - Prioritize threads that have received the least service in each period, reducing core stall time and improving system throughput.
- Requirements:
  - Extend Ramulator with a new scheduler type (e.g., by adding a new type in `Scheduler.h` and associated logic) that is **functionally equivalent** to the ATLAS mechanism as described in the paper.
  - Use the default ATLAS configuration from the paper:
    - **Quantum length**: 10 million cycles
    - **α**: 0.875
    - **T**: 100K cycles
  - The software design is up to you, as long as the observable behavior matches the mechanism and parameters above.

---

### 4. Task 2/3: Implementing the BLISS Scheduler

- Goal: implement the **BLISS** memory scheduler in Ramulator.
- High-level idea:
  - Classify applications into two groups:
    - high memory intensity
    - low memory intensity
  - Detect applications that repeatedly access the same row many times in a short time window, blacklist them, and deprioritize them for a limited time to reduce interference and balance performance and fairness.
- Requirements:
  - Extend Ramulator (e.g., in `Scheduler.h` and related logic) with a BLISS scheduler that is **functionally equivalent** to the mechanism described in the paper.
  - Use the default BLISS configuration:
    - **Blacklisting Threshold**: 4
    - **Clearing Interval**: 10K cycles

---

### 5. Task 3/3: Evaluating ATLAS and BLISS vs. Conventional Schedulers

You must compare the following five schedulers under multi-programmed workloads:

- **FCFS** (First-Come First-Serve)
- **FRFCFS** (First-Ready First-Come First-Serve)
- **FRFCFS Cap**
- **ATLAS** (your implementation)
- **BLISS** (your implementation)

Evaluation metrics:

- **Instruction Throughput (IT)**:

  - \( IT = \dfrac{\sum\_{c=0}^{NumCores-1} InstructionsRetired(c)}{CPUCycles} \)
  - This is the sum of all retired instructions across all cores, divided by the total number of CPU cycles.
  - You must add a new statistic in Ramulator:
    - Use the `ScalarStat` class, following how existing stats are implemented.
    - Output a new line for instruction throughput in the `.stats` file.

- **Maximum Slowdown (MS)**:
  - \( MS = \max*{a \in Applications} \dfrac{CPUCycles*{shared}(a)}{CPUCycles\_{alone}(a)} \)
  - For each application, compute slowdown as: execution time when running in a multi-programmed workload divided by execution time when running alone. MS is the maximum of these slowdowns.
  - Because this requires multiple runs (shared and alone), MS is not a direct single-run statistic:
    - You must compute MS **offline** from multiple `.stats` files (manually or via a script).

Simulation and experimental setup:

1. **Configuration constraints**: do not change processor or memory configuration parameters except where explicitly allowed.
2. **Termination condition**: all cores must retire **20 million** instructions before simulation ends.
3. **Multi-programmed workloads** (H = high-mem-intensity trace, L = low-mem-intensity trace):
   - Workload 1: **HLLL** (4 cores)
   - Workload 2: **HHLL** (4 cores)
   - Workload 3: **HHHH** (4 cores)
   - Workload 4: **HHHHHHHH** (8 cores)
4. For each scheduler and each workload:
   - Run Ramulator.
   - Collect all data needed to compute IT and MS.
   - Compute IT and MS and plot the results.

You should produce two figures:

- One figure showing **IT** for the 4 workloads and 5 schedulers.
- One figure showing **MS** for the same workloads and schedulers.

Your report should briefly answer:

- What the graphs show and how the metrics change across workloads and schedulers.
- How each scheduler affects IT and MS, and why.
- If results deviate from your expectations, plausible explanations.

---

### 6. Bonus Task (Optional): Designing Your Own Memory Scheduler

- Propose one or more new memory scheduling ideas.
- Requirements:
  - The idea must be your own.
  - Implement the new scheduler(s) in Ramulator.
  - Evaluate it using the same methodology as in Task 3, and compare against the five existing schedulers (FCFS, FRFCFS, FRFCFS Cap, ATLAS, BLISS).
- Submission for the bonus:
  - A detailed description of your new idea.
  - The Ramulator implementation.
  - Results comparing your idea against the five baselines (plots in the same style as Task 3 are recommended).

Grading details follow the original handout and are not repeated here.

---

### 7. Submission Requirements

Package the following into a single `tar.gz` file (e.g., `lab4_<Surname>_<Name>.tar.gz`):

- **Code**:
  - All source files required to compile your modified Ramulator (including unmodified Ramulator source files needed for compilation).
  - **Do not** include trace files or compiled artifacts (e.g., executables, `.o` files).
- **Report (PDF)**:
  - A brief description of the changes you made in Ramulator to implement the new scheduling policies (ATLAS, BLISS, and your own scheduler if you did the bonus).
  - Analysis for Task 3, including:
    - IT and MS plots.
    - Explanations and discussion of the results.
- **Stats files**:
  - All `.stats` files used for Task 3 (and the bonus task, if applicable).

---

### 8. Additional Notes

- Do not distribute the provided program files (including traces and Ramulator code); they are for individual use by students of the course only.
- Make sure you read the original handout (PDF or equivalent) for full context; this file is a condensed version focused on lab-relevant information.
- When you encounter technical issues, first read error messages carefully and try to debug on your own; only then, if necessary, seek help following the course guidelines.

---

### 9. External Resources (Public Links Mentioned in the Original Text)

- Ramulator GitHub repository: `https://github.com/CMU-SAFARI/ramulator`
- For the ATLAS, BLISS, and Ramulator papers, as well as the gem5 paper, please refer to the course platform or public sources as instructed by the course.
