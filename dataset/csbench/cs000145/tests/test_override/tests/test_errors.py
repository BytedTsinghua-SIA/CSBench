from tests.utils import run_node


def test_validation_error_maps_to_400():
    result = run_node(
        "phonebook/middleware.js",
        "mapError",
        [{"name": "ValidationError", "message": "name must be unique"}],
    )
    assert result["ok"]
    assert result["result"]["status"] == 400


def test_not_found_error_maps_to_404():
    result = run_node(
        "phonebook/middleware.js",
        "mapError",
        [{"name": "NotFoundError", "message": "not found"}],
    )
    assert result["ok"]
    assert result["result"]["status"] == 404
