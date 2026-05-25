from tests.utils import run_node


def test_initialize_anecdotes_builds_actions():
    result = run_node(
        "anecdotes/thunks.js",
        "initializeAnecdotes",
        [[{"id": "1", "votes": 0}]],
    )
    assert result["ok"]
    assert result["result"]["actions"][0]["type"] == "SET_ANECDOTES"


def test_create_and_vote_thunks_build_notifications():
    created = run_node(
        "anecdotes/thunks.js",
        "createAnecdoteThunk",
        [{"content": "new", "id": "1", "votes": 0}, 5],
    )
    voted = run_node(
        "anecdotes/thunks.js",
        "voteAnecdoteThunk",
        [{"content": "old", "id": "1", "votes": 1}, 5],
    )
    assert created["ok"] and voted["ok"]
    assert created["result"]["notification"]["message"].startswith("new")
    assert voted["result"]["notification"]["message"].startswith("you voted")
