from tests.utils import run_node


REPO = {
    "id": "repo1",
    "fullName": "owner/name",
    "url": "https://github.com/owner/name",
    "description": "Example",
    "language": "TypeScript",
    "forksCount": 1,
    "stargazersCount": 2,
    "ratingAverage": 3,
    "reviewCount": 4,
}


def test_single_repository_view_and_route():
    view = run_node(
        "components/repositoryView.js",
        "buildSingleRepositoryView",
        [REPO, {"showGithubButton": True}],
    )
    assert view["ok"]
    assert view["result"]["url"] == "https://github.com/owner/name"
    assert view["result"]["showGithubButton"] is True

    route = run_node("components/repositoryView.js", "buildRepositoryRoute", ["repo1"])
    assert route["ok"]
    assert route["result"] == "/repositories/repo1"

    action = run_node("components/repositoryView.js", "buildRepositoryPressAction", ["repo1"])
    assert action["ok"]
    assert action["result"]["navigateTo"] == "/repositories/repo1"
