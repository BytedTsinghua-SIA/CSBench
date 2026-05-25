from tests.utils import run_node

BOOKS = [
    {"title": "A", "genres": ["refactoring"], "author": {"name": "X"}},
    {"title": "B", "genres": ["crime"], "author": {"name": "Y"}},
]


def test_filters_and_genres():
    filtered = run_node("frontend/filters.js", "filterBooksByGenre", [BOOKS, "crime"])
    assert filtered["ok"]
    assert len(filtered["result"]) == 1
    rec = run_node("frontend/filters.js", "recommendBooksForUser", [BOOKS, {"favoriteGenre": "refactoring"}])
    assert rec["ok"]
    assert rec["result"][0]["title"] == "A"
    vars = run_node("frontend/filters.js", "buildGenreQueryVariables", ["crime"])
    assert vars["ok"]
    assert vars["result"]["genre"] == "crime"
    genres = run_node("frontend/filters.js", "listGenres", [BOOKS])
    assert genres["ok"]
    assert "crime" in genres["result"]
