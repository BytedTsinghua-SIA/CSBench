from tests.utils import run_node


REVIEWS = {
    "edges": [
        {"node": {"id": "rev1", "rating": 90, "text": "Ok", "createdAt": "2020-01-02T00:00:00.000Z", "repository": {"id": "repo1", "fullName": "owner/name"}}}
    ]
}


def test_user_reviews():
    result = run_node("components/userReviews.js", "buildUserReviews", [REVIEWS])
    assert result["ok"]
    assert result["result"][0]["repositoryFullName"] == "owner/name"
