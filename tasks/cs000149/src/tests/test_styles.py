from tests.utils import run_node


def test_style_theme():
    theme = run_node("bloglist/styles/styles.js", "createStyleTheme", ["styled-components"])
    assert theme["ok"]
    assert theme["result"]["method"] == "styled-components"
