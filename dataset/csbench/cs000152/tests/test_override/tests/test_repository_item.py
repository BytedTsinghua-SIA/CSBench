from tests.utils import run_node


REPO = {
    "id": "repo1",
    "fullName": "owner/name",
    "description": "Example",
    "language": "TypeScript",
    "forksCount": 1589,
    "stargazersCount": 21553,
    "ratingAverage": 88,
    "reviewCount": 4,
    "ownerAvatarUrl": "https://example.com/avatar.png",
}


def test_repository_item():
    item = run_node("components/repositoryItem.js", "buildRepositoryItem", [REPO])
    assert item["ok"]
    result = item["result"]
    assert result["fullName"] == "owner/name"
    assert result["forksCount"] == "1.6k"
    assert result["ownerAvatarUrl"].startswith("https://")
