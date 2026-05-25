from tests.utils import run_node

BOOKS = [
    {"id": "b1", "author": {"name": "A"}},
    {"id": "b2", "author": {"name": "A"}},
    {"id": "b3", "author": {"name": "B"}},
]


def test_author_book_counts():
    counts = run_node("backend/nplusone.js", "buildAuthorBookCountMap", [BOOKS])
    assert counts["ok"]
    count_a = run_node("backend/nplusone.js", "resolveAuthorBookCount", [{"name": "A"}, counts["result"]])
    assert count_a["ok"]
    assert count_a["result"] == 2
