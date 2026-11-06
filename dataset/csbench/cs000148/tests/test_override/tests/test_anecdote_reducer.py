from tests.utils import run_node

ANECDOTES = [
    {"id": "1", "content": "First", "votes": 1},
    {"id": "2", "content": "Second", "votes": 5},
]


def test_vote_action_increments():
    result = run_node(
        "anecdotes/anecdoteReducer.js",
        "anecdoteReducer",
        [ANECDOTES, {"type": "VOTE", "payload": "1"}],
    )
    assert result["ok"]
    updated = next(item for item in result["result"] if item["id"] == "1")
    assert updated["votes"] == 2


def test_create_anecdote_action_adds_item():
    result = run_node(
        "anecdotes/anecdoteReducer.js",
        "anecdoteReducer",
        [ANECDOTES, {"type": "NEW_ANECDOTE", "payload": {"content": "Third", "id": "3", "votes": 0}}],
    )
    assert result["ok"]
    assert len(result["result"]) == 3


def test_sort_by_votes():
    result = run_node(
        "anecdotes/anecdoteReducer.js",
        "sortByVotes",
        [ANECDOTES],
    )
    assert result["ok"]
    assert result["result"][0]["id"] == "2"


def test_build_form_payload_trims():
    result = run_node(
        "anecdotes/anecdoteReducer.js",
        "buildFormPayload",
        ["  new anecdote  "],
    )
    assert result["ok"]
    assert result["result"] == "new anecdote"


def test_build_list_view_sorted():
    result = run_node(
        "anecdotes/anecdoteReducer.js",
        "buildListView",
        [ANECDOTES],
    )
    assert result["ok"]
    assert result["result"][0]["votes"] == 5
