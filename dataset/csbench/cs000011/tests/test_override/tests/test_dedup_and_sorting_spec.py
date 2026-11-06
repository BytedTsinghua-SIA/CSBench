from pathlib import Path


def test_duplicate_url_not_inflate_counts(run_aggregator):
    """
    Same URL appears twice in the feed. Dedup must prevent double-counting
    token frequencies for that article.
    """
    res = run_aggregator("echo 'unique' | ./aggregate --url local-feed-list-dup.xml --quiet")
    assert res.returncode == 0, f"Aggregator failed: {res.stderr}"
    # The article tokens include 'unique' exactly once; should not show "2 times"
    assert "appears 1 time" in res.stdout, res.stdout
    assert "appears 2 times" not in res.stdout, res.stdout


def test_sorting_by_frequency_and_tie_break(run_aggregator):
    """
    Articles should be ordered by frequency, then by URL if tie.
    c.html has beta twice, d.html has beta once, so c.html should appear first.
    """
    res = run_aggregator("echo 'beta' | ./aggregate --url local-feed-list-sort.xml --quiet")
    assert res.returncode == 0, f"Aggregator failed: {res.stderr}"
    s = res.stdout
    first_idx = s.find("assets/c.html")
    second_idx = s.find("assets/d.html")
    assert first_idx != -1 and second_idx != -1, f"Expected both results in output: {s}"
    assert first_idx < second_idx, f"Expected c.html before d.html (sorted by frequency): {s}"
