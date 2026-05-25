from tests.utils import run_node


def test_context_user_reducer():
    set_action = run_node("bloglist/state/context/userContext.js", "setSession", [{"username": "root"}])
    assert set_action["ok"]
    updated = run_node(
        "bloglist/state/context/userContext.js",
        "userReducer",
        [{"user": None}, set_action["result"]],
    )
    assert updated["ok"]
    assert updated["result"]["user"]["username"] == "root"
