import os
import re
import shutil
import subprocess
import unittest
from pathlib import Path


class RamulatorTestCase(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.root_dir = Path(__file__).resolve().parent
        cls.ramulator_bin = cls.root_dir / "ramulator"
        cls.base_config = cls.root_dir / "configs" / "test-config.cfg"
        cls.trace_file = cls.root_dir / "cpu.trace"

        if not cls.ramulator_bin.is_file():
            raise RuntimeError(
                "ramulator binary not found. Please run 'make' in src directory first."
            )
        if not cls.base_config.is_file():
            raise RuntimeError(f"Base config not found: {cls.base_config}")
        if not cls.trace_file.is_file():
            raise RuntimeError(f"Trace file not found: {cls.trace_file}")

    def _run_ramulator(self, config: Path, stats_file: Path):
        cmd = [
            str(self.ramulator_bin),
            str(config),
            "--mode=cpu",
            "--stats",
            str(stats_file),
            str(self.trace_file),
        ]
        result = subprocess.run(
            cmd,
            cwd=self.root_dir,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
        )
        if result.returncode != 0:
            self.fail(
                f"Ramulator returned non-zero exit code {result.returncode}.\n"
                f"STDOUT:\n{result.stdout}\nSTDERR:\n{result.stderr}"
            )

    def _read_stats(self, stats_file: Path) -> str:
        if not stats_file.is_file():
            self.fail(f"Stats file not found: {stats_file}")
        return stats_file.read_text()

    def _extract_instruction_throughput(self, stats_content: str) -> float:
        for line in stats_content.splitlines():
            if "ramulator.instruction_throughput" in line:
                # Expect format: name  value  # comment
                tokens = line.split()
                if len(tokens) >= 2:
                    try:
                        return float(tokens[1])
                    except ValueError:
                        self.fail(
                            f"Cannot parse instruction_throughput from line: {line}"
                        )
        self.fail("instruction_throughput not found in stats content.")

    def _make_scheduler_config(self, scheduler_name: str) -> Path:
        cfg_path = self.root_dir / "configs" / f"test-{scheduler_name}.cfg"
        base_text = self.base_config.read_text().splitlines()
        filtered = []
        for line in base_text:
            stripped = line.lstrip()
            if stripped.startswith("scheduler "):
                continue
            filtered.append(line)
        filtered.append(f"scheduler {scheduler_name}")
        cfg_path.write_text("\n".join(filtered) + "\n")
        return cfg_path

    # 1) instruction_throughput default test (corresponds to shell default test)
    def test_instruction_throughput_default(self):
        stats_file = self.root_dir / "test_default_py.stats"
        if stats_file.is_file():
            stats_file.unlink()

        self._run_ramulator(self.base_config, stats_file)
        content = self._read_stats(stats_file)
        it_value = self._extract_instruction_throughput(content)

        # Expect instruction throughput to be positive for the sample trace
        self.assertGreater(
            it_value, 0.0, "instruction_throughput should be > 0 for default config."
        )

    # 2) Scheduler tests (each method corresponds to one scheduler in the shell script)
    def test_scheduler_FCFS(self):
        self._test_scheduler_common("FCFS")

    def test_scheduler_FRFCFS(self):
        self._test_scheduler_common("FRFCFS")

    def test_scheduler_FRFCFS_Cap(self):
        self._test_scheduler_common("FRFCFS_Cap")

    def test_scheduler_ATLAS(self):
        self._test_scheduler_common("ATLAS")

    def test_scheduler_BLISS(self):
        self._test_scheduler_common("BLISS")

    def _test_scheduler_common(self, scheduler_name: str):
        cfg = self._make_scheduler_config(scheduler_name)
        stats_file = self.root_dir / f"test_{scheduler_name}_py.stats"
        if stats_file.is_file():
            stats_file.unlink()

        self._run_ramulator(cfg, stats_file)
        content = self._read_stats(stats_file)

        # Just check that instruction_throughput exists for this scheduler
        try:
            it_value = self._extract_instruction_throughput(content)
        except AssertionError as e:
            self.fail(
                f"instruction_throughput not found or invalid for scheduler={scheduler_name}: {e}"
            )

        # Sanity: value should be non-negative
        self.assertGreaterEqual(
            it_value,
            0.0,
            f"instruction_throughput should be >= 0 for scheduler={scheduler_name}.",
        )


if __name__ == "__main__":
    unittest.main()
