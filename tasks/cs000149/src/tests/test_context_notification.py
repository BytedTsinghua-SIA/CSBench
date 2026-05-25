from tests.utils import run_node


def test_context_notification():
    shown = run_node(
        "bloglist/state/context/notificationContext.js",
        "showNotification",
        ["saved", 5000, 1000],
    )
    assert shown["ok"]
    state = shown["result"]
    should_clear = run_node(
        "bloglist/state/context/notificationContext.js",
        "shouldClear",
        [state, 7001],
    )
    assert should_clear["ok"]
    assert should_clear["result"] is True
