from tests.utils import run_node


def test_subscription_helpers():
    note = run_node("frontend/subscriptions.js", "handleBookAddedNotification", [{"title": "New"}])
    assert note["ok"]
    assert "New" in note["result"]
    updated = run_node("frontend/subscriptions.js", "applyBookAdded", [[{"id": "1"}], {"id": "2"}])
    assert updated["ok"]
    assert len(updated["result"]) == 2
