from tests.utils import run_node


def test_review_actions():
    review = {"id": "rev1", "repositoryId": "repo1"}
    actions = run_node("components/reviewActions.js", "buildReviewActions", [review])
    assert actions["ok"]
    assert actions["result"]["viewRepositoryId"] == "repo1"

    confirm = run_node("components/reviewActions.js", "confirmDeleteReview", [True])
    assert confirm["ok"]
    assert confirm["result"] is True
