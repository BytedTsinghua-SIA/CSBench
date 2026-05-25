from tests.utils import run_node


REPO = {
    "id": "repo1",
    "fullName": "owner/name",
    "reviews": {
        "edges": [
            {
                "node": {
                    "id": "rev1",
                    "text": "Nice",
                    "rating": 90,
                    "createdAt": "2020-01-02T00:00:00.000Z",
                    "user": {"id": "u1", "username": "ada"},
                }
            }
        ]
    },
}


def test_review_list():
    result = run_node("components/reviewList.js", "buildReviewList", [REPO])
    assert result["ok"]
    assert result["result"]["header"]["fullName"] == "owner/name"
    assert result["result"]["items"][0]["date"] == "02.01.2020"
