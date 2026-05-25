from tests.utils import run_node

AUTHORS = [{"name": "A", "born": None}]
BOOKS = []
NEW_BOOK = {"title": "T", "author": {"name": "B"}, "published": 2000, "genres": []}


def test_cache_updates():
    added = run_node("frontend/cache.js", "applyAddBookCache", [AUTHORS, BOOKS, NEW_BOOK])
    assert added["ok"]
    assert len(added["result"]["authors"]) == 2
    updated = run_node("frontend/cache.js", "setAuthorBorn", [added["result"]["authors"], "B", 1970])
    assert updated["ok"]
    assert updated["result"][1]["born"] == 1970
    merged = run_node("frontend/cache.js", "updateBooksCache", [BOOKS, {"title": "T", "id": "1"}])
    assert merged["ok"]
    assert len(merged["result"]) == 1
