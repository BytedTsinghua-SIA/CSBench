from process_simulator import Process, Simulator, STATE_READY, STATE_RUNNING, STATE_BLOCKED, STATE_DONE, OP_CPU, OP_IO

class TestProcess:
    def test_process_initialization(self):
        """Test if a process is initialized with correct PID and instructions."""
        instructions = [OP_CPU, OP_IO]
        p = Process(101, instructions)
        assert p.pid == 101
        assert p.instructions == instructions
        assert p.pc == 0
        assert p.state == STATE_READY

    def test_get_next_instruction(self):
        """Test fetching instructions from a process."""
        p = Process(0, [OP_CPU])
        assert p.get_next_instruction() == OP_CPU
        p.pc = 1
        assert p.get_next_instruction() is None

    def test_execute_instruction_and_done(self):
        """Test instruction execution and state transition to DONE."""
        p = Process(0, [OP_CPU])
        p.execute_instruction()
        assert p.pc == 1
        assert p.state == STATE_DONE

class TestSimulatorBasics:
    def test_simulator_initialization(self):
        """Test simulator setup with specific behaviors."""
        sim = Simulator(switch_on_io=True, io_immediate=False, io_length=3)
        assert sim.switch_on_io is True
        assert sim.io_immediate is False
        assert sim.io_length == 3
        assert sim.clock == 0

    def test_add_process(self):
        """Test adding a process to the simulator."""
        sim = Simulator(True, False, 5)
        sim.add_process(2, 1.0) # 2 CPU instructions
        assert len(sim.processes) == 1
        assert sim.processes[0].pid == 0
        assert len(sim.processes[0].instructions) == 2

    def test_get_active_count(self):
        """Test counting non-DONE processes."""
        sim = Simulator(True, False, 5)
        sim.add_process(1, 1.0)
        sim.add_process(1, 1.0)
        assert sim.get_active_count() == 2
        sim.processes[0].state = STATE_DONE
        assert sim.get_active_count() == 1

class TestSimulatorScheduling:
    def test_select_next_process_round_robin(self):
        """Test the round-robin selection logic."""
        sim = Simulator(True, False, 5)
        sim.add_process(1, 1.0)
        sim.add_process(1, 1.0)
        
        sim.select_next_process(0)
        assert sim.current_proc_idx == 0
        assert sim.processes[0].state == STATE_RUNNING
        assert sim.processes[1].state == STATE_READY
        
        sim.select_next_process() # Should pick 1
        assert sim.current_proc_idx == 1
        assert sim.processes[1].state == STATE_RUNNING
        assert sim.processes[0].state == STATE_READY

    def test_select_next_process_none_runnable(self):
        """Test behavior when no processes are runnable."""
        sim = Simulator(True, False, 5)
        sim.add_process(1, 1.0)
        sim.processes[0].state = STATE_DONE
        sim.select_next_process()
        assert sim.current_proc_idx == -1

class TestSimulatorIO:
    def test_io_blocking_and_finish_time(self):
        """Test if a process blocks correctly when issuing I/O."""
        sim = Simulator(switch_on_io=True, io_immediate=False, io_length=10)
        sim.add_process(1, 0.0) # One I/O instruction
        sim.select_next_process(0)
        
        # In Simulator.run(), the clock would advance and instruction would execute.
        # We simulate the key state change here.
        p = sim.processes[0]
        sim.clock = 1
        curr_inst = p.get_next_instruction()
        if curr_inst == OP_IO:
            p.state = STATE_BLOCKED
            sim.io_finish_times[0].append(sim.clock + sim.io_length + 1)
        
        assert p.state == STATE_BLOCKED
        assert sim.io_finish_times[0] == [12]

class TestEdgeCases:
    def test_empty_simulator(self):
        """Test simulator behavior with zero processes."""
        sim = Simulator(True, False, 5)
        res = sim.run(print_trace=False)
        assert res is None

    def test_zero_io_length(self):
        """Test I/O behavior when I/O length is zero."""
        sim = Simulator(True, False, 0)
        sim.add_process(1, 0.0) # IO
        cpu, io, total = sim.run(print_trace=False)
        assert total == 2 # 1 tick for IO start, 1 tick for io_done (CPU)
        assert cpu == 2
        assert io == 0 # Since it finishes at T=2 (clock+0+1), it's never "outstanding" during tick
