from tests.utils import run_node


def test_notification_context_flow():
    shown = run_node("context/notificationContext.js", "showNotification", ["saved", 5000, 1000])
    assert shown["ok"]
    state = shown["result"]
    should_clear = run_node("context/notificationContext.js", "shouldClear", [state, 7000])
    assert should_clear["ok"]
    assert should_clear["result"] is True


def test_notification_reducer_clear():
    state = {"message": "x", "expiresAt": 1000}
    result = run_node(
        "context/notificationContext.js",
        "notificationReducer",
        [state, {"type": "CLEAR"}],
    )
    assert result["ok"]
    assert result["result"]["message"] is None
