from tests.utils import run_node


def test_store_config_has_reducers():
    result = run_node("toolkit/store.js", "createStoreConfig")
    assert result["ok"]
    reducers = result["result"]["reducers"]
    assert "anecdotes" in reducers and "filter" in reducers and "notification" in reducers


def test_slices_have_names():
    filter_slice = run_node("toolkit/filterSlice.js", "createFilterSlice")
    anecdote_slice = run_node("toolkit/anecdoteSlice.js", "createAnecdoteSlice")
    notification_slice = run_node("toolkit/notificationSlice.js", "createNotificationSlice")
    assert filter_slice["ok"] and anecdote_slice["ok"] and notification_slice["ok"]
    assert filter_slice["result"]["name"] == "filter"
    assert anecdote_slice["result"]["name"] == "anecdotes"
    assert notification_slice["result"]["name"] == "notification"
