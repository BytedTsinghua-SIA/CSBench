from tests.utils import run_node

USERS = [
    {"id": "u1", "name": "Ada", "blogs": [{"id": "b1"}]},
    {"id": "u2", "name": "Linus", "blogs": []},
]


def test_user_rows_and_detail():
    rows = run_node("bloglist/views/users.js", "buildUserRows", [USERS])
    assert rows["ok"]
    assert rows["result"][0]["blogCount"] == 1
    detail = run_node("bloglist/views/users.js", "buildUserDetail", [USERS[0]])
    assert detail["ok"]
    assert detail["result"]["name"] == "Ada"
