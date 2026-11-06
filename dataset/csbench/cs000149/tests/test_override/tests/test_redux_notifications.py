from tests.utils import run_node


def test_redux_notification_reducer():
    set_action = run_node("bloglist/state/redux/notification.js", "setNotification", ["hello"])
    clear_action = run_node("bloglist/state/redux/notification.js", "clearNotification")
    assert set_action["ok"] and clear_action["ok"]
    updated = run_node(
        "bloglist/state/redux/notification.js",
        "notificationReducer",
        [{"message": None}, set_action["result"]],
    )
    assert updated["ok"]
    assert updated["result"]["message"] == "hello"
