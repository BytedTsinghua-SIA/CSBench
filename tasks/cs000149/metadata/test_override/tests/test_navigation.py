from tests.utils import run_node


def test_navigation_links():
    result = run_node("bloglist/views/navigation.js", "buildNavigation", [{"name": "Ada"}, "/blogs"])
    assert result["ok"]
    paths = {link["path"] for link in result["result"]["links"]}
    assert "/blogs" in paths and "/users" in paths
