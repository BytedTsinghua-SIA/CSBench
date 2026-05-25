from tests.utils import run_node


def test_menu_links():
    result = run_node("routing/router.js", "buildMenuLinks")
    assert result["ok"]
    paths = {link["path"] for link in result["result"]}
    assert "/" in paths and "/create" in paths


def test_resolve_routes():
    root = run_node("routing/router.js", "resolveRoute", ["/"])
    create = run_node("routing/router.js", "resolveRoute", ["/create"])
    show = run_node("routing/router.js", "resolveRoute", ["/anecdotes/5"])
    assert root["ok"] and create["ok"] and show["ok"]
    assert root["result"]["view"] == "list"
    assert create["result"]["view"] == "create"
    assert show["result"]["id"] == "5"
