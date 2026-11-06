from tests.utils import run_node


def test_build_fetch_request():
    result = run_node(
        "services/anecdoteService.js",
        "buildFetchRequest",
        ["POST", "http://localhost:3001/anecdotes", {"content": "hi"}],
    )
    assert result["ok"]
    assert result["result"]["method"] == "POST"
    assert result["result"]["body"] == "{\"content\": \"hi\"}"


def test_apply_vote_update():
    result = run_node(
        "services/anecdoteService.js",
        "applyVoteUpdate",
        [{"id": "1", "votes": 2}, 1],
    )
    assert result["ok"]
    assert result["result"]["votes"] == 3
