from tests.utils import run_node


def test_platform_specific_font():
    android = run_node("theme.js", "getFontFamily", ["android"])
    assert android["ok"]
    assert android["result"] == "Roboto"
    ios = run_node("theme.js", "getFontFamily", ["ios"])
    assert ios["ok"]
    assert ios["result"] == "Arial"
    other = run_node("theme.js", "getFontFamily", ["web"])
    assert other["ok"]
    assert other["result"] == "System"
