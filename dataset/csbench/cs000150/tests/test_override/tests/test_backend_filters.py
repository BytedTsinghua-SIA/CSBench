from tests.utils import run_node

AUTHORS = [
    {"id": "a1", "name": "Robert Martin"},
    {"id": "a2", "name": "Martin Fowler"},
]
BOOKS = [
    {"id": "b1", "title": "Clean Code", "published": 2008, "author": "Robert Martin", "genres": ["refactoring", "clean"]},
    {"id": "b2", "title": "Refactoring", "published": 1999, "author": "Martin Fowler", "genres": ["refactoring"]},
    {"id": "b3", "title": "Agile", "published": 2002, "author": "Robert Martin", "genres": ["agile"]},
]


def test_filter_by_author_and_genre():
    by_author = run_node("backend/library.js", "allBooks", [BOOKS, AUTHORS, {"author": "Robert Martin"}])
    by_genre = run_node("backend/library.js", "allBooks", [BOOKS, AUTHORS, {"genre": "refactoring"}])
    both = run_node("backend/library.js", "allBooks", [BOOKS, AUTHORS, {"author": "Robert Martin", "genre": "refactoring"}])
    assert by_author["ok"] and by_genre["ok"] and both["ok"]
    assert len(by_author["result"]) == 2
    assert len(by_genre["result"]) == 2
    assert len(both["result"]) == 1
