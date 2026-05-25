from tests.utils import run_node


def test_counts():
    books = [{"id": "b1"}, {"id": "b2"}]
    authors = [{"id": "a1"}, {"id": "a2"}, {"id": "a3"}]
    bc = run_node("backend/library.js", "bookCount", [books])
    ac = run_node("backend/library.js", "authorCount", [authors])
    assert bc["ok"] and ac["ok"]
    assert bc["result"] == 2
    assert ac["result"] == 3
