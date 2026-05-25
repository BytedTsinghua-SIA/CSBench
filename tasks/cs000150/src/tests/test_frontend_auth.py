from tests.utils import run_node

USERS = [{"username": "root", "favoriteGenre": "refactoring"}]


def test_login_and_session():
    login = run_node("frontend/auth.js", "loginUser", [USERS, {"username": "root", "password": "secret"}, "secret"])
    assert login["ok"]
    session = run_node("frontend/auth.js", "createSession", [login["result"]])
    assert session["ok"]
    assert session["result"]["token"].startswith("token-")
    cleared = run_node("frontend/auth.js", "logoutUser", [session["result"]])
    assert cleared["ok"]
    assert cleared["result"] is None
