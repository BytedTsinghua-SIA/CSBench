from tests.utils import run_node


def test_auth_storage_cycle():
    result = run_node("utils/authStorage.js", "authStorageScenario", [])
    assert result["ok"]
    assert result["result"]["before"] is None
    assert result["result"]["after"] == "token"
    assert result["result"]["removed"] is True
