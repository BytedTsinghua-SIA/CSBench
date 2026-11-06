from pathlib import Path

from harness_utils import assert_all_pass, run_cmd


def test_part_b_perf_super_light_async():
    root = Path(__file__).resolve().parents[1]
    part_b = root / "asst2" / "part_b"
    run_cmd(["make", "-C", str(part_b)], cwd=root)
    output = run_cmd(
        [
            "python3",
            "../tests/run_test_harness.py",
            "-t",
            "super_light",
            "-n",
            "4",
            "-a",
        ],
        cwd=part_b,
    )
    assert_all_pass(output)
