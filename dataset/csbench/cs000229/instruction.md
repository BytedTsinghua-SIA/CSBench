## Background (Excerpts from Assignment 5)

The goal of this assignment is to implement distributed training methods, including data parallelism and pipeline parallelism. You will work with GPT-2 and explore how to scale training across multiple devices (CPUs).

Distributed training is essential for training large-scale models that cannot fit on a single device or would take too long to train. You will implement two primary forms of parallelism:
- **Data Parallelism**: Distributing data across multiple devices, where each device holds a copy of the model.
- **Pipeline Parallelism**: Distributing model layers across multiple devices, where each device processes a portion of the model's layers in a pipelined fashion.

### Problem 1: Data Parallel

In this part, you will implement data parallel training for GPT-2. You are restricted to using `torch.distributed` and `torch.multiprocessing.Process` for communication and process management.

#### Phase 1.1: Dataset Partitioning
Implement the dataset partitioning logic in `data_parallel/dataset.py`. This includes:
1. `partition_dataset`: A helper function to create a partitioned `DataLoader`.
2. `Partition` class: To define a dataset slice based on indices.
3. `DataPartitioner` class: To handle the actual splitting of the dataset.

**Hints:**
- Calculate the `partitioned batch size` (e.g., $total\_batch\_size // world\_size$).
- Use `DataPartitioner` to shuffle and split indices based on the number of devices.
- Use the customized `collate_fn` from `project/utils.py` in your `DataLoader`.

**Test:**
```bash
python -m pytest -l -v -k "a5_1_1"
```

#### Phase 1.2: Process Group and Communication
Implement the distributed setup and gradient aggregation in `project/run_data_parallel.py` and `project/utils.py`.
1. `setup`: Initialize the process group using `gloo` backend (recommended for CPU).
2. `main`: Spawn processes for each rank using `torch.multiprocessing`.
3. `average_gradients`: Aggregate gradients across all devices after backward propagation.

**Hints:**
- Set `MASTER_ADDR` to `localhost` and `MASTER_PORT` to `11868`.
- Call `average_gradients` after `loss.backward()` in the training loop.

**Test:**
First, generate gradients with 2 processes:
```bash
python project/run_data_parallel.py --pytest True --n_epochs 1
```
Then run the verification:
```bash
python -m pytest -l -v -k "a5_1_2"
```

#### Phase 1.3: Performance Evaluation
Compare the performance between single-device and multi-device training. Measure `training time` and `tokens_per_second`.
- **Single Node:** `python project/run_data_parallel.py --world_size 1 --batch_size 64`
- **Double Nodes:** `python project/run_data_parallel.py --world_size 2 --batch_size 128`

Plot the results using `project/plot.py` and save them in the `submit_figures` directory.

---

### Problem 2: Pipeline Parallel

In this part, you will implement pipeline parallelism for GPT-2, splitting the model layers across multiple logical devices.

#### Phase 2.1: Module Splitting and Scheduling
Implement the core logic for partitioning in `pipeline/partition.py` and scheduling in `pipeline/pipe.py`.
1. `_split_module`: Split an `nn.Sequential` module into multiple partitions.
2. `_clock_cycles`: Generate a schedule for microbatch execution across partitions.

**Test:**
```bash
python -m pytest -l -v -k "a5_2_1"
```

#### Phase 2.2: Pipe Module Implementation
Implement the `Pipe` wrapper in `pipeline/pipe.py` to handle microbatch execution.
1. `Pipe.forward`: Split input into microbatches and manage their flow.
2. `Pipe.compute`: Execute tasks using worker threads and queues.

**Hints:**
- Ensure the final result is placed on the last device to avoid training failure.
- Use `in_queue` and `out_queue` to communicate with worker threads.

**Test:**
```bash
python -m pytest -l -v -k "a5_2_2"
```

#### Phase 2.3: GPT-2 Pipeline Parallelism
Prepare the GPT-2 model for pipeline training in `pipeline/model_parallel.py`.
1. `_prepare_pipeline_parallel`: Extract transformer blocks and package them into an `nn.Sequential` module.

**Note:** `GPT2Block` returns a tuple; you only need the hidden states for the pipeline.

**Execution:**
```bash
python project/run_pipeline.py --model_parallel_mode='model_parallel'
python project/run_pipeline.py --model_parallel_mode='pipeline_parallel'
```
Plot and save performance figures in `submit_figures`.
