#!/usr/bin/env python3

import sys
import random
import argparse

STATE_RUNNING = 'RUNNING'
STATE_READY = 'READY'
STATE_BLOCKED = 'BLOCKED'
STATE_DONE = 'DONE'

OP_CPU = 'cpu'
OP_IO = 'io'
OP_IO_DONE = 'io_done'

class Process:
    def __init__(self, pid, instructions):
        pass

    def get_next_instruction(self):
        pass

    def execute_instruction(self):
        pass

class Simulator:
    def __init__(self, switch_on_io, io_immediate, io_length):
        pass

    def add_process(self, instruction_count, cpu_chance):
        pass

    def get_active_count(self):
        pass

    def get_runnable_pids(self):
        pass

    def select_next_process(self, preferred_pid=-1):
        pass

    def run(self, print_trace=True):
        pass

def main():
    parser = argparse.ArgumentParser(description='Process State Simulator')
    parser.add_argument('-s', '--seed', type=int, default=0, help='Random seed')
    parser.add_argument('-l', '--processlist', type=str, default='', 
                        help='Comma-separated list of X:Y (X=instructions, Y=% CPU chance)')
    parser.add_argument('-L', '--iolength', type=int, default=5, help='Length of I/O')
    parser.add_argument('-S', '--switch', type=str, default='SWITCH_ON_IO', 
                        choices=['SWITCH_ON_IO', 'SWITCH_ON_END'], help='When to switch processes')
    parser.add_argument('-I', '--iodone', type=str, default='IO_RUN_LATER', 
                        choices=['IO_RUN_LATER', 'IO_RUN_IMMEDIATE'], help='I/O completion behavior')
    parser.add_argument('-c', '--compute', action='store_true', help='Show execution trace')
    parser.add_argument('-p', '--printstats', action='store_true', help='Print statistics')

    args = parser.parse_args()

    random.seed(args.seed)

    sim = Simulator(
        switch_on_io=(args.switch == 'SWITCH_ON_IO'),
        io_immediate=(args.iodone == 'IO_RUN_IMMEDIATE'),
        io_length=args.iolength
    )

    if not args.processlist:
        print("Please provide a process list using -l (e.g., -l 5:100,3:0)")
        return

    for proc_desc in args.processlist.split(','):
        parts = proc_desc.split(':')
        if len(parts) != 2:
            continue
        count, chance = int(parts[0]), float(parts[1]) / 100.0
        sim.add_process(count, chance)

    cpu_busy, io_busy, total_time = sim.run(print_trace=args.compute)

    if args.printstats and args.compute:
        print(f"\nStats: Total Time {total_time}")
        print(f"Stats: CPU Busy {cpu_busy} ({100.0 * cpu_busy / total_time:.2f}%)")
        print(f"Stats: IO Busy  {io_busy} ({100.0 * io_busy / total_time:.2f}%)")

if __name__ == "__main__":
    main()
