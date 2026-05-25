from tests.utils import run_node

AUTHORS = [
    {"id": "a1", "name": "Robert Martin"},
    {"id": "a2", "name": "Martin Fowler"},
]
BOOKS = [
    {"id": "b1", "title": "Clean Code", "published": 2008, "author": "Robert Martin", "genres": ["refactoring"]},
    {"id": "b2", "title": "Refactoring", "published": 1999, "author": "Martin Fowler", "genres": ["refactoring"]},
]


def test_all_books_and_authors():
    books = run_node("backend/library.js", "allBooks", [BOOKS, AUTHORS, {}])
    authors = run_node("backend/library.js", "allAuthors", [AUTHORS, BOOKS])
    assert books["ok"] and authors["ok"]
    assert books["result"][0]["author"]["name"] == "Robert Martin"
    assert authors["result"][0]["bookCount"] == 1
