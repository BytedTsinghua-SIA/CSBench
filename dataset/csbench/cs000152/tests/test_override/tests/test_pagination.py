from tests.utils import run_node


def test_pagination_vars_and_merge():
    vars_result = run_node("utils/pagination.js", "getPaginationVariables", [{"first": 3, "after": "cursor"}])
    assert vars_result["ok"]
    assert vars_result["result"]["first"] == 3
    assert vars_result["result"]["after"] == "cursor"

    merged = run_node(
        "utils/pagination.js",
        "mergeEdges",
        [[{"node": {"id": "a"}}], [{"node": {"id": "b"}}]],
    )
    assert merged["ok"]
    assert len(merged["result"]) == 2
