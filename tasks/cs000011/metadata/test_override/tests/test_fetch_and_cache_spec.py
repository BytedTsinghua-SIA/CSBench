from pathlib import Path


def test_parse_local_rss_feeds_succeeds_without_network():
    """
    The RSSFeed parser should be able to parse local XML files.
    Validate that feed files exist and are non-empty.
    """
    src_dir = Path(__file__).resolve().parent.parent
    for name in ["small-feed.xml", "medium-feed.xml", "static-alphabet-feed.xml"]:
        feed = src_dir / name
        assert feed.exists(), f"Missing feed: {name}"
        assert feed.stat().st_size > 0, f"Empty feed: {name}"


def test_aggregate_runs_with_local_feeds(run_aggregator):
    """
    Test that aggregate can run with local feed files.
    """
    res = run_aggregator("./aggregate --url small-feed.xml --quiet")
    assert res.returncode == 0, f"Failed to run with small-feed.xml: {res.stderr}"


def test_aggregate_handles_static_feed(run_aggregator):
    """
    Test with static-alphabet-feed.xml which is designed for testing.
    """
    res = run_aggregator("./aggregate --url static-alphabet-feed.xml --quiet")
    assert res.returncode == 0, f"Failed with static feed: {res.stderr}"
