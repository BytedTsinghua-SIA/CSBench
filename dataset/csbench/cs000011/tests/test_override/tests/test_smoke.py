from pathlib import Path


def test_repository_layout_and_assets_exist():
    # locate src root from this test file
    tests_dir = Path(__file__).resolve().parent
    src_dir = tests_dir.parent

    # essential build files
    assert (src_dir / "Makefile").exists(), "Missing Makefile in src/"
    assert (src_dir / "aggregate.cc").exists(), "Missing aggregate.cc"

    # core headers and sources
    for p in [
        "news-aggregator.cc",
        "news-aggregator.h",
        "rss-feed.cc",
        "rss-feed.h",
        "rss-feed-list.cc",
        "rss-feed-list.h",
        "html-document.cc",
        "html-document.h",
        "utils.cc",
        "utils.h",
        "string-utils.cc",
        "string-utils.h",
        "ostreamlock.h",
    ]:
        assert (src_dir / p).exists(), f"Missing source/header: {p}"

    # sample feeds for offline testing
    for feed in [
        "small-feed.xml",
        "medium-feed.xml",
        "static-alphabet-feed.xml",
        "single-server-source-feed.xml",
    ]:
        fp = src_dir / feed
        assert fp.exists(), f"Missing feed file: {feed}"
        # quick sanity: non-empty file
        assert fp.stat().st_size > 0, f"Feed file is empty: {feed}"


