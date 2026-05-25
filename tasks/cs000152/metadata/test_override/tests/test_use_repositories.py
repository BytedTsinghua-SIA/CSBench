from tests.utils import run_node


def test_repositories_query_and_variables():
    query = run_node("hooks/useRepositories.js", "buildRepositoriesQuery")
    assert query["ok"]
    assert "repositories" in query["result"]
    assert "fullName" in query["result"]

    vars_latest = run_node(
        "hooks/useRepositories.js",
        "getRepositoryQueryVariables",
        [{"order": "latest", "searchKeyword": ""}],
    )
    assert vars_latest["ok"]
    assert vars_latest["result"]["orderBy"] == "CREATED_AT"

    vars_rating = run_node(
        "hooks/useRepositories.js",
        "getRepositoryQueryVariables",
        [{"order": "highest", "searchKeyword": "react"}],
    )
    assert vars_rating["ok"]
    assert vars_rating["result"]["orderBy"] == "RATING_AVERAGE"
    assert vars_rating["result"]["searchKeyword"] == "react"

    keyword = run_node("hooks/useRepositories.js", "normalizeSearchKeyword", ["  hello "])
    assert keyword["ok"]
    assert keyword["result"] == "hello"
