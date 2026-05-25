from tests.utils import run_node


def test_review_form_validation_and_payload():
    errors = run_node(
        "components/reviewForm.js",
        "validateReview",
        [{"ownerName": "", "repositoryName": "repo", "rating": 120}],
    )
    assert errors["ok"]
    assert "ownerName" in errors["result"]
    assert "rating" in errors["result"]

    payload = run_node(
        "components/reviewForm.js",
        "buildReviewInput",
        [{"ownerName": "owner", "repositoryName": "repo", "rating": 85, "text": "ok"}],
    )
    assert payload["ok"]
    assert payload["result"]["ownerName"] == "owner"
