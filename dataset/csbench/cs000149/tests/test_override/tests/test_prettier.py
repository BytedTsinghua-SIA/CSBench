from tests.utils import run_node


def test_prettier_config():
    result = run_node("bloglist/format/prettier.js", "createPrettierConfig")
    assert result["ok"]
    assert result["result"]["singleQuote"] is True
