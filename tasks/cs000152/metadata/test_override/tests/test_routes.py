from tests.utils import run_node


def test_routes_include_sign_in():
    routes = run_node("components/routes.js", "getRoutes")
    assert routes["ok"]
    paths = [route["path"] for route in routes["result"]]
    assert "/" in paths
    assert "/signin" in paths
