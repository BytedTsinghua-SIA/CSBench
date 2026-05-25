from tests.utils import run_node


def test_action_creators():
    vote = run_node("anecdotes/anecdoteReducer.js", "createVoteAction", ["1"])
    create = run_node("anecdotes/anecdoteReducer.js", "createAnecdoteAction", ["hello", "2"])
    set_all = run_node("anecdotes/anecdoteReducer.js", "setAnecdotesAction", [[{"id": "1"}]])
    assert vote["ok"] and create["ok"] and set_all["ok"]
    assert vote["result"]["type"] == "VOTE"
    assert create["result"]["type"] == "NEW_ANECDOTE"
    assert set_all["result"]["type"] == "SET_ANECDOTES"
