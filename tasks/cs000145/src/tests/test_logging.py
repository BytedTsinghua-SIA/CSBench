from tests.utils import run_node


def test_morgan_format_includes_body_token():
    result = run_node("phonebook/logging.js", "buildMorganFormat")
    assert result["ok"]
    assert ":body" in result["result"]
    assert ":method" in result["result"]
