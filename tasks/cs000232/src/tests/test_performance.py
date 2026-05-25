import statistics
from conftest import time_program, quake_serial

THREADS = [1, 2, 4, 8, 16, 32]
NUM_RUNS = 2  # number of runs for averaging, as per requirement


def average_time(binary, threads, input_file, runs=NUM_RUNS):
    """Run program multiple times and return average time."""
    times = []
    for _ in range(runs):
        t = time_program(binary, threads, input_file)
        times.append(t)
    return statistics.mean(times)


def test_parallel_speedup_at_4_threads(quake_omp, quake_serial, quake_input):
    serial_time = average_time(quake_serial, 1, quake_input)
    print(f"serial average ({NUM_RUNS} runs): {serial_time:.3f}s")

    times = {}
    for t in THREADS:
        times[t] = average_time(quake_omp, t, quake_input)
        print(f"{t} threads average ({NUM_RUNS} runs): {times[t]:.3f}s")

    # At least ensure 4 threads is not slower than 1 thread
    assert times[4] < times[1] * 0.95, "No speedup at 4 threads"


def test_parallel_speedup_threshold(quake_omp, quake_serial, quake_input):
    serial_time = average_time(quake_serial, 1, quake_input)
    print(f"serial average ({NUM_RUNS} runs): {serial_time:.3f}s")

    times = {}
    for t in THREADS:
        times[t] = average_time(quake_omp, t, quake_input)
        print(f"{t} threads average ({NUM_RUNS} runs): {times[t]:.3f}s")

    # At least two thread counts must achieve speedup > 1.10 (relative to serial)
    speedups = {}
    speedup_counts = 0
    for t in THREADS:
        speedup = serial_time / times[t]
        speedups[t] = speedup
        if speedup > 1.10:
            speedup_counts += 1
    print(f"Speedups: {speedups}")
    assert speedup_counts >= 2, f"Only {speedup_counts} thread counts have speedup > 1.10 (need at least 2)"