from tests.utils import run_node


def test_notification_lifecycle():
    created = run_node("routing/notifications.js", "createNotification", ["saved", 1000, 5000])
    assert created["ok"]
    active = run_node("routing/notifications.js", "isNotificationActive", [created["result"], 4000])
    expired = run_node("routing/notifications.js", "isNotificationActive", [created["result"], 7000])
    assert active["ok"] and expired["ok"]
    assert active["result"] is True
    assert expired["result"] is False


def test_handle_create_anecdote_returns_navigation():
    result = run_node(
        "routing/notifications.js",
        "handleCreateAnecdote",
        [[{"id": "1"}], {"id": "2", "content": "new"}, 1000],
    )
    assert result["ok"]
    assert result["result"]["navigateTo"] == "/"
    assert result["result"]["notification"]["message"].startswith("added")
