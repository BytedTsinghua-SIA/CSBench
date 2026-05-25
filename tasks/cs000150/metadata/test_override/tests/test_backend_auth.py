from tests.utils import run_node

USERS = [{"id": "u1", "username": "root", "favoriteGenre": "refactoring"}]


def test_user_create_and_login():
    created = run_node("backend/auth.js", "createUser", [USERS, {"username": "alice", "favoriteGenre": "crime"}])
    assert created["ok"]
    assert len(created["result"]["users"]) == 2
    login = run_node("backend/auth.js", "login", [created["result"]["users"], {"username": "alice", "password": "secret"}])
    assert login["ok"]
    assert login["result"]["value"].startswith("token-")


def test_get_current_user():
    token = run_node("backend/auth.js", "login", [USERS, {"username": "root", "password": "secret"}])["result"]["value"]
    current = run_node("backend/auth.js", "getCurrentUser", [USERS, token])
    assert current["ok"]
    assert current["result"]["username"] == "root"
