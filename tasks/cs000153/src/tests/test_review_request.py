from tests.utils import run_node


def test_review_request():
    result = run_node("repo/review.js", "buildReviewRequest", [{"reviewer": "mluukkai"}])
    assert result["ok"]
    assert result["result"]["reviewer"] == "mluukkai"
