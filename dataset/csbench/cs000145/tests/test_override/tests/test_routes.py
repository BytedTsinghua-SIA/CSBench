from tests.utils import run_node

EXPECTED = {
    ("get", "/api/persons"),
    ("get", "/info"),
    ("get", "/api/persons/:id"),
    ("post", "/api/persons"),
    ("put", "/api/persons/:id"),
    ("delete", "/api/persons/:id"),
}


def test_routes_cover_core_endpoints():
    result = run_node("phonebook/routes.js", "getRoutes")
    assert result["ok"]
    routes = {(route["method"], route["path"]) for route in result["result"]}
    assert EXPECTED.issubset(routes)
