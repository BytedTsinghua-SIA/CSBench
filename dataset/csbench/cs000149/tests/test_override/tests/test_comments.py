from tests.utils import run_node

BLOG = {"id": "b1", "comments": ["hi"]}


def test_comment_flow():
    added = run_node("bloglist/views/comments.js", "addComment", [BLOG, "new comment"])
    assert added["ok"]
    listed = run_node("bloglist/views/comments.js", "listComments", [added["result"]])
    assert listed["ok"]
    assert listed["result"][1] == "new comment"
