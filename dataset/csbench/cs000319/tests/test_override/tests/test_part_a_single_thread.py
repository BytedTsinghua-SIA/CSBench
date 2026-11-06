from pathlib import Path

from harness_utils import assert_all_pass, run_cmd


def test_part_a_perf_math_ops():
    root = Path(__file__).resolve().parents[1]
    part_a = root / "asst2" / "part_a"
    run_cmd(["make", "-C", str(part_a)], cwd=root)
    output = run_cmd(
        [
            "python3",
            "../tests/run_test_harness.py",
            "-t",
            "math_operations_in_tight_for_loop",
            "-n",
            "4",
        ],
        cwd=part_a,
    )
    assert_all_pass(output)
