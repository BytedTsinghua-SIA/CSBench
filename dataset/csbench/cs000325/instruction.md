# AFS Cache Consistency Simulator

## Experiment Background

This experiment provides a simulator (`afs.py`) for exploring cache consistency behavior in the Andrew File System (AFS). The program generates random client traces of file operations (opens, reads, writes, closes) to help understand how AFS maintains consistency across distributed clients.

## Core Tasks and Function Points

### Understanding AFS Behavior
- Analyze how AFS handles file caching and consistency across multiple clients
- Predict file values after various sequences of client operations
- Understand the role of callbacks and cache invalidations in maintaining consistency

### Simulator Usage and Analysis
- Run the simulator with different parameters to generate various traces
- Use command-line flags to control simulation parameters:
  - `-C`: Number of clients
  - `-n`: Operations per client
  - `-s`: Random seed for reproducible traces
  - `-c`: Compute and display answers
  - `-d`: Detail level for diagnostic information

### Key Concepts to Explore
1. **File Consistency**: How AFS ensures clients see consistent file states
2. **Cache Management**: Understanding valid/dirty/reference count states
3. **Callback Mechanism**: How server notifies clients of file changes
4. **Cache Invalidation**: When and how cached data becomes invalid

### Experimental Scenarios
- Analyze traces with different client schedules using `-S` flag
- Control exact client actions using `-A` flag for specific behavior testing
- Observe server-client interactions with detail flags
- Predict outcomes of concurrent file operations

## Learning Objectives
- Understand AFS cache consistency model
- Predict file system behavior under various access patterns
- Analyze the impact of operation ordering on file consistency
- Comprehend the role of callbacks in distributed file systems
