from tests.utils import run_node


def test_filter_reducer_and_action():
    action = run_node("anecdotes/filterReducer.js", "setFilterAction", ["redux"])
    assert action["ok"]
    result = run_node("anecdotes/filterReducer.js", "filterReducer", ["", action["result"]])
    assert result["ok"]
    assert result["result"] == "redux"
