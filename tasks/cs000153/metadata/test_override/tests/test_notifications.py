from tests.utils import run_node


def test_notifications_steps():
    result = run_node("workflows/notifications.js", "buildDiscordNotifications")
    assert result["ok"]
    text = result["result"]
    assert "success()" in text
    assert "failure()" in text
