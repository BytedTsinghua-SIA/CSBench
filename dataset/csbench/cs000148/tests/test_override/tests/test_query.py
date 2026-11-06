from tests.utils import run_node


def test_resolve_query_view():
    error_view = run_node("query/anecdotes.js", "resolveQueryView", [{"isError": True}])
    loading_view = run_node("query/anecdotes.js", "resolveQueryView", [{"isLoading": True}])
    data_view = run_node("query/anecdotes.js", "resolveQueryView", [{"data": [1]}])
    assert error_view["ok"] and loading_view["ok"] and data_view["ok"]
    assert error_view["result"]["view"] == "error"
    assert loading_view["result"]["view"] == "loading"
    assert data_view["result"]["view"] == "ready"


def test_merge_updated_anecdote():
    anecdotes = [{"id": "1", "votes": 0}, {"id": "2", "votes": 1}]
    updated = {"id": "2", "votes": 5}
    result = run_node("query/anecdotes.js", "mergeUpdatedAnecdote", [anecdotes, updated])
    assert result["ok"]
    assert result["result"][1]["votes"] == 5


def test_is_valid_content():
    valid = run_node("query/anecdotes.js", "isValidContent", ["long enough"])
    invalid = run_node("query/anecdotes.js", "isValidContent", ["no"])
    assert valid["ok"] and invalid["ok"]
    assert valid["result"] is True
    assert invalid["result"] is False
