from tests.utils import run_node


def test_validation_errors():
    bad = run_node("backend/validation.js", "validateBook", [{"title": "a"}])
    assert bad["ok"]
    assert bad["result"] == "title too short"
    error = run_node("backend/validation.js", "toGraphQLError", ["invalid"])
    assert error["ok"]
    assert "invalid" in error["result"]["message"]
