from pathlib import Path


def test_article_concurrency_not_exceed_global_limit(run_aggregator):
    """
    With many articles on the same server, the global article threads
    should not exceed 18.
    """
    cmd = "echo '' | ./aggregate --url local-feed-list-many.xml --quiet --report-limits"
    res = run_aggregator(cmd)
    assert res.returncode == 0, f"Aggregator failed: {res.stderr}"
    assert "MAX article threads:" in res.stdout, res.stdout
    # parse value
    for line in res.stdout.splitlines():
        if line.startswith("MAX article threads:"):
            val = int(line.split(":")[1].strip())
            assert val <= 18, f"Exceeded global article limit: {val} > 18"


def test_feed_concurrency_not_exceed_limit(run_aggregator):
    """
    With multiple feeds, the concurrent feed threads should not exceed 5.
    """
    cmd = "echo '' | ./aggregate --url local-feed-list-multi.xml --quiet --report-limits"
    res = run_aggregator(cmd)
    assert res.returncode == 0, f"Aggregator failed: {res.stderr}"
    assert "MAX feed threads:" in res.stdout, res.stdout
    for line in res.stdout.splitlines():
        if line.startswith("MAX feed threads:"):
            val = int(line.split(":")[1].strip())
            assert val <= 5, f"Exceeded feed limit: {val} > 5"


def test_per_server_concurrency_not_exceed_limit(run_aggregator):
    """
    Per-server concurrency should not exceed 8 for 'assets'.
    """
    cmd = "echo '' | ./aggregate --url local-feed-list-many.xml --quiet --report-limits"
    res = run_aggregator(cmd)
    assert res.returncode == 0, f"Aggregator failed: {res.stderr}"
    # Look for server line
    lines = res.stdout.splitlines()
    matches = [l for l in lines if l.startswith("MAX per-server connections [assets]:")]
    assert matches, f"No per-server stats found in output: {res.stdout}"
    val = int(matches[0].split(":")[1].strip())
    assert val <= 8, f"Exceeded per-server limit: {val} > 8"
