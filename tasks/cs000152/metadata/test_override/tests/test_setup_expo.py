from tests.utils import run_node


def test_create_expo_project():
    result = run_node("setup/expo.js", "createExpoProject", ["rate-repository-app"])
    assert result["ok"]
    data = result["result"]
    assert data["name"] == "rate-repository-app"
    assert data["scripts"]["start"] == "expo start"
    assert "android" in data["scripts"]
