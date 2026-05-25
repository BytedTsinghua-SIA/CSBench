import subprocess


EXPECTED_IMPLS = [
    "[Serial]",
    "[Parallel + Always Spawn]",
    "[Parallel + Thread Pool + Spin]",
    "[Parallel + Thread Pool + Sleep]",
]


def run_cmd(cmd, cwd):
    result = subprocess.run(cmd, cwd=cwd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    return (result.stdout or "") + (result.stderr or "")


def parse_overall_results(output):
    results = {}
    for line in output.splitlines():
        if ":" not in line:
            continue
        left, right = line.split(":", 1)
        impl = left.strip()
        if impl in EXPECTED_IMPLS:
            results[impl] = right.strip()
    return results


def assert_all_pass(output):
    if "Overall performance results" not in output:
        raise AssertionError
    results = parse_overall_results(output)
    for impl in EXPECTED_IMPLS:
        if results.get(impl) != "All passed Perf":
            raise AssertionError
