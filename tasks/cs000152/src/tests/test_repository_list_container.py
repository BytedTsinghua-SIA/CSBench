from tests.utils import run_node


REPOSITORIES = {
    "edges": [
        {"node": {"id": "repo1", "fullName": "a/b", "description": "one", "language": "JS", "forksCount": 10, "stargazersCount": 20, "ratingAverage": 50, "reviewCount": 1}},
        {"node": {"id": "repo2", "fullName": "c/d", "description": "two", "language": "TS", "forksCount": 5, "stargazersCount": 6, "ratingAverage": 70, "reviewCount": 2}},
    ]
}


def test_repository_list_container():
    result = run_node("components/repositoryList.js", "buildRepositoryListContainer", [REPOSITORIES])
    assert result["ok"]
    items = result["result"]
    assert len(items) == 2
    assert items[0]["testId"] == "repositoryItem"
