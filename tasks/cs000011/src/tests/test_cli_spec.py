import subprocess
from pathlib import Path


def test_cli_accepts_verbose_and_quiet_and_runs(run_aggregator):
    # --verbose
    res_v = run_aggregator("./aggregate --verbose --url small-feed.xml")
    assert res_v.returncode == 0, f"verbose failed: {res_v.stderr}"

    # --quiet
    res_q = run_aggregator("./aggregate --quiet --url small-feed.xml")
    assert res_q.returncode == 0, f"quiet failed: {res_q.stderr}"


def test_cli_accepts_url_flag(run_aggregator):
    res = run_aggregator("./aggregate --url small-feed.xml")
    assert res.returncode == 0, f"url flag failed: {res.stderr}"


def test_cli_rejects_unknown_flag_with_nonzero_exit(run_aggregator):
    res = run_aggregator("./aggregate --definitely-unknown")
    assert res.returncode != 0, "Should reject unknown flag"


def test_aggregate_binary_exists():
    # Resolve aggregate binary relative to src directory
    src_dir = Path(__file__).resolve().parent.parent
    aggregate_bin = src_dir / "aggregate"
    assert aggregate_bin.exists(), "aggregate binary should exist after build"
