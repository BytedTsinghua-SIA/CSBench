from tests.utils import run_node


def test_notification_actions_and_reducer():
    set_action = run_node("anecdotes/notificationReducer.js", "setNotificationAction", ["hello"])
    clear_action = run_node("anecdotes/notificationReducer.js", "clearNotificationAction")
    assert set_action["ok"] and clear_action["ok"]
    updated = run_node(
        "anecdotes/notificationReducer.js",
        "notificationReducer",
        [{"message": None}, set_action["result"]],
    )
    assert updated["ok"]
    assert updated["result"]["message"] == "hello"


def test_timed_notification():
    result = run_node(
        "anecdotes/notificationReducer.js",
        "buildTimedNotification",
        ["voted", 5, 1000],
    )
    assert result["ok"]
    assert result["result"]["expiresAt"] == 6000
