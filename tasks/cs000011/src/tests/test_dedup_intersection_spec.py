from pathlib import Path


def test_intersection_stores_only_min_url(run_aggregator):
    """
    For same title and server with multiple variants, only the lexicographically
    smallest URL should be present in search results, and tokens should be the intersection.
    """
    # Query a token present in both a.html and b.html (intersection: beta, gamma)
    res = run_aggregator("echo 'beta' | ./aggregate --url local-feed-list.xml --quiet")
    assert res.returncode == 0, f"Aggregator failed: {res.stderr}"
    # Should reference only assets/a.html (min URL), not assets/b.html
    assert "assets/a.html" in res.stdout, f"Expected min URL in results: {res.stdout}"
    assert "assets/b.html" not in res.stdout, f"Unexpected non-min URL in results: {res.stdout}"


def test_intersection_removes_non_common_tokens(run_aggregator):
    """
    Tokens not present in all variants should not appear in the index.
    """
    # 'alpha' exists only in a.html, not in b.html, so intersection excludes it
    res = run_aggregator("echo 'alpha' | ./aggregate --url local-feed-list.xml --quiet")
    assert res.returncode == 0, f"Aggregator failed: {res.stderr}"
    assert "Ah, we didn't find the term \"alpha\"." in res.stdout, res.stdout


def test_single_variant_is_indexed_as_is(run_aggregator):
    """
    When only one variant exists for a (server, title), its tokens should be indexed as-is.
    """
    res = run_aggregator("echo 'unique' | ./aggregate --url local-feed-list.xml --quiet")
    assert res.returncode == 0, f"Aggregator failed: {res.stderr}"
    assert "assets/unique.html" in res.stdout, f"Expected single variant URL in results: {res.stdout}"
