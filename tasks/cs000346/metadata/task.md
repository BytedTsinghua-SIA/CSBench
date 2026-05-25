# Lab 5: Optimize LLM on Edge Devices

## Background

Running large language models (LLMs) on edge devices is crucial for enabling instant responses and services without relying on stable internet connections. By embedding LLMs directly into real-world systems such as in-car entertainment or spaceship control interfaces, users can access services locally, which enhances user experience, addresses privacy concerns, and eliminates queuing delays associated with cloud services.

However, LLMs are traditionally resource-intensive, requiring significant computational power and memory, making them challenging to deploy on edge devices with limited capabilities.

## Objectives

In this lab, you will learn:

- How to deploy an LLaMA2-7B-chat model with TinyChatEngine on your computer
- Implement different optimization techniques (loop unrolling, multithreading, and SIMD programming) for the linear kernel
- Observe the end-to-end latency improvement achieved by each technique

## Prerequisites

- Basic C and C++ programming knowledge
- Recommended: Read the parallel computing tutorial introducing optimization techniques

## System Requirements

- Operating Systems: macOS, Linux, or Windows
- Processor: x86 (Intel/AMD) or ARM (Apple M1/M2)
- Memory: 8 GB minimum
- Storage: 5 GB available

## Core Tasks

### 1. Setup and Model Deployment

- Install required dependencies (boost, llvm, Python, etc.)
- Download TinyChatEngine codebase and LLaMA2-7B-chat model
- Understand device-specific 4-bit weight reordering layouts (QM_ARM for ARM, QM_x86 for x86)

### 2. Implement Optimization Techniques

Complete the provided starter codes in `kernels/starter_code/` directory by implementing:

- **Loop Unrolling** (`loop_unrolling.cc`): Optimize program execution speed through space-time tradeoff
- **Multithreading** (`multithreading.cc`): Enable concurrent execution for improved performance
- **SIMD Programming** (`simd_programming.cc`): Process multiple data with single instructions
- **Multithreading with Loop Unrolling** (`multithreading_loop_unrolling.cc`): Combine multithreading and loop unrolling
- **All Techniques** (`all_techniques.cc`): Integrate all optimization techniques

### 3. Evaluation and Testing

- Use `evaluate.sh` script to test correctness and measure performance (GOPs)
- Compare implementations against the reference implementation
- Generate performance reports for each optimization technique

### 4. Submission Requirements

- Complete all optimization implementations in the starter code
- Generate a patch file using `git diff` named `{studentID}-{ISA}.patch` (ISA: x86 or ARM)
- Submit a report documenting code changes and performance improvements for each technique

## Grading (120 points total)

- **Correctness** (15 points each): Based on evaluation script output for each of 5 implementations
- **Performance Reporting** (5 points each): Document performance improvements and explanations for each technique
- **Bonus** (up to 20 points): Additional optimizations beyond required techniques (1 point per 1% speedup)
