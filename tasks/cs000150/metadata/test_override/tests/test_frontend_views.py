from tests.utils import run_node

AUTHORS = [
    {"name": "A", "born": 1950, "bookCount": 2},
]
BOOKS = [
    {"title": "T", "author": {"name": "A"}, "published": 2000, "genres": ["x"]},
]


def test_views_and_normalize():
    authors_view = run_node("frontend/views/authors.js", "buildAuthorsView", [AUTHORS])
    options = run_node("frontend/views/authors.js", "buildAuthorOptions", [AUTHORS])
    books_view = run_node("frontend/views/books.js", "buildBooksView", [BOOKS])
    normalized = run_node("frontend/views/books.js", "normalizeBookAuthor", [BOOKS[0]])
    assert authors_view["ok"] and options["ok"] and books_view["ok"] and normalized["ok"]
    assert options["result"][0] == "A"
    assert "genres" not in books_view["result"][0]
    assert normalized["result"]["author"] == "A"
