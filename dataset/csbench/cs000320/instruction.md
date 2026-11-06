# Task: Process State Simulation

## Background
This experiment is based on the "Process" chapter of the "Operating Systems: Three Easy Pieces" (OSTEP) course. It utilizes the `process-run.py` script to simulate and visualize how process states (RUNNING, READY, BLOCKED, DONE) transition during execution on a single CPU system. The simulation helps in understanding the fundamental concepts of process management, scheduling, and the impact of I/O operations on system performance.

## Core Tasks
1. **Understand Process States**: Observe and analyze the transitions between the following states:
   - **RUNNING**: The process is currently using the CPU.
   - **READY**: The process is waiting for the CPU to become available.
   - **BLOCKED**: The process is waiting for an I/O operation to complete.
   - **DONE**: The process has finished its execution.

2. **Execution Trace Analysis**: Generate and interpret execution traces using the `-c` flag to see how instructions (CPU vs. I/O) affect the state of one or multiple processes over time.

3. **Scheduling & I/O Behavior Exploration**:
   - Investigate how different **process switch behaviors** (`SWITCH_ON_IO` vs. `SWITCH_ON_END`) influence execution order and efficiency.
   - Evaluate the impact of **I/O completion behaviors** (`IO_RUN_LATER` vs. `IO_RUN_IMMEDIATE`) on when a process resumes execution.
   - Adjust **I/O length** (`-L`) to see its effect on CPU idle time.

4. **Resource Utilization Evaluation**: Use the `-p` flag to collect and analyze statistics such as total execution time, CPU utilization percentage, and I/O device busy time.

## Homework Questions
1. **CPU Utilization Analysis**: Run `process-run.py` with the following flags: `-l 5:100,5:100`. What should the CPU utilization be? Why? Use `-c` and `-p` to verify.
2. **I/O Impact**: Now run with these flags: `./process-run.py -l 4:100,1:0`. These flags specify one process with 4 instructions (all CPU) and one that just issues an I/O and waits for it to be done. How long does it take to complete both processes? Use `-c` and `-p` to verify.
3. **Process Order**: Switch the order of the processes: `-l 1:0,4:100`. What happens now? Does the order matter? Why or why not? (Again, use `-c` and `-p` to see if you were right.)

## Functional Requirements
The simulation supports the following configurations:
- **Process Definition**: Define processes via `-l` with a specific number of instructions and their probability of being CPU-bound or I/O-bound.
- **Randomization**: Use `-s` (seed) to generate different random execution scenarios.
- **Switching Logic**: Configure whether the scheduler switches processes only when one ends or whenever one blocks on I/O.
- **I/O Responsiveness**: Configure whether a process should run immediately after its I/O finishes or wait for its next scheduled turn.

