from pathlib import Path


def test_aggregate_handles_network_failures_gracefully(run_aggregator):
    """
    Test that aggregate doesn't crash when feeds fail to download.
    """
    res = run_aggregator("./aggregate --url small-feed.xml --quiet")
    # Should complete even if some feeds fail
    assert res.returncode == 0, f"Crashed on network failure: {res.stderr}"


def test_aggregate_continues_after_feed_failure(run_aggregator):
    """
    Test that aggregate continues processing after individual feed failures.
    """
    res = run_aggregator("./aggregate --url medium-feed.xml --quiet")
    # Should reach the query prompt even if feeds fail
    assert res.returncode == 0 or "Enter a search term" in res.stdout
