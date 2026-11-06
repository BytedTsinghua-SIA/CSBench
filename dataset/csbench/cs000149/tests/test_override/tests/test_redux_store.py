from tests.utils import run_node


def test_store_config_contains_reducers():
    result = run_node("bloglist/state/redux/store.js", "createStoreConfig")
    assert result["ok"]
    reducers = result["result"]["reducers"]
    assert "blogs" in reducers and "notification" in reducers and "user" in reducers
