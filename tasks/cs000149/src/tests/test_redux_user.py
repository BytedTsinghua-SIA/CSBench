from tests.utils import run_node


def test_user_reducer():
    set_action = run_node("bloglist/state/redux/user.js", "setUser", [{"username": "root"}])
    clear_action = run_node("bloglist/state/redux/user.js", "clearUser")
    assert set_action["ok"] and clear_action["ok"]
    updated = run_node(
        "bloglist/state/redux/user.js",
        "userReducer",
        [None, set_action["result"]],
    )
    assert updated["ok"]
    assert updated["result"]["username"] == "root"
