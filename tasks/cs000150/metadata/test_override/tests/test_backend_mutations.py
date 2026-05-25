from tests.utils import run_node

AUTHORS = [
    {"id": "a1", "name": "Robert Martin", "born": None},
]
BOOKS = []


def test_add_book_and_edit_author():
    added = run_node(
        "backend/library.js",
        "addBook",
        [BOOKS, AUTHORS, {"title": "New", "author": "New Author", "published": 2020, "genres": ["test"]}, {}],
    )
    assert added["ok"]
    assert len(added["result"]["authors"]) == 2
    edited = run_node(
        "backend/library.js",
        "editAuthor",
        [added["result"]["authors"], "New Author", 1970, {}],
    )
    assert edited["ok"]
    assert edited["result"]["author"]["born"] == 1970


def test_add_book_requires_auth():
    result = run_node(
        "backend/library.js",
        "addBook",
        [BOOKS, AUTHORS, {"title": "No", "author": "Auth", "published": 2020, "genres": ["x"]}, {"requireAuth": True, "currentUser": None}],
    )
    assert not result["ok"]
