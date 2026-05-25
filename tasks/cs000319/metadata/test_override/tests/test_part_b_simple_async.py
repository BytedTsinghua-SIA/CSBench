from pathlib import Path

from harness_utils import assert_all_pass, run_cmd


def test_part_b_perf_math_ops_async():
    root = Path(__file__).resolve().parents[1]
    part_b = root / "asst2" / "part_b"
    run_cmd(["make", "-C", str(part_b)], cwd=root)
    output = run_cmd(
        [
            "python3",
            "../tests/run_test_harness.py",
            "-t",
            "math_operations_in_tight_for_loop",
            "-n",
            "4",
            "-a",
        ],
        cwd=part_b,
    )
    assert_all_pass(output)
