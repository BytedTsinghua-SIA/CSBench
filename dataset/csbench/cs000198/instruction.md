# Lab 5: Data Prefetching with ChampSim

## Overview

In this lab, you will implement and evaluate various prefetching algorithms using ChampSim, a trace-based microarchitectural simulator written in C++. ChampSim models a modern high-performance out-of-order (OoO) core and enables the evaluation of microarchitectural concepts such as data prefetching, branch prediction, and cache replacement policies. Unlike timing simulators that execute programs directly, ChampSim utilizes instruction traces extracted from applications to simulate processor microarchitecture behavior.

## Getting Started

### 1. Clone the ChampSim Repository

```bash
$ git clone https://gitlab.ethz.ch/rahbera/champsim.git
```

### 2. Build ChampSim

Navigate to the ChampSim directory and run the build script with a specified prefetching algorithm name. For example, to build with the "next_line" prefetcher:

```bash
$ ./build_champsim.sh next_line
```

This command creates the ChampSim executable inside the `bin/` directory.

## ChampSim Metrics

ChampSim reports various metrics at the end of each simulation. Key metrics to consider when evaluating L2 prefetchers include:

- Number of cycles
- L1D average miss latency
- Number of L2 loads/hits/misses
- Number of L2 prefetch requests and useful prefetch requests

## Prefetcher Implementation

Implement your prefetchers by modifying the provided prefetcher API. The prefetcher interface consists of the following functions that you need to implement:

- `l2c_prefetcher_initialize()`: Called once at the start of simulation to initialize prefetcher state
- `l2c_prefetcher_operate(uint64_t addr, uint64_t ip, uint8_t cache_hit, uint8_t type, uint32_t metadata_in)`: Called on every L2 cache access
- `l2c_prefetcher_cache_fill(uint64_t addr, uint32_t set, uint32_t way, uint8_t prefetch, uint64_t evicted_addr, uint32_t metadata_in)`: Called when a cache line is filled
- `l2c_prefetcher_final_stats()`: Called at the end of simulation to print statistics

Ensure your implementations are efficient and evaluate their impact on the supplied program traces.

## Tasks

You are required to implement three different prefetcher algorithms:

1. **GHB (Global History Buffer) Prefetcher**: Implement a prefetcher based on the Global History Buffer approach that uses delta correlation to detect access patterns.

2. **FDP (Feedback Directed Prefetching) Prefetcher**: Implement a prefetcher that uses feedback mechanisms to dynamically adjust prefetch aggressiveness based on prefetch accuracy and timeliness.

3. **Hybrid Prefetcher**: Design and implement a hybrid prefetcher that combines multiple prefetching techniques to improve performance across different workload characteristics.
