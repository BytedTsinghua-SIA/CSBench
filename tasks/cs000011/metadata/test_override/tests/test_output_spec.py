from pathlib import Path


def test_aggregate_produces_output(run_aggregator):
    """
    Test that aggregate produces the expected query prompt.
    """
    res = run_aggregator("./aggregate --url small-feed.xml --quiet")
    assert "Enter a search term" in res.stdout, f"Missing query prompt: {res.stdout}"


def test_aggregate_handles_empty_query(run_aggregator):
    """
    Test that aggregate exits gracefully on empty input.
    """
    res = run_aggregator("echo '' | ./aggregate --url small-feed.xml --quiet")
    assert res.returncode == 0, f"Failed on empty query: {res.stderr}"
