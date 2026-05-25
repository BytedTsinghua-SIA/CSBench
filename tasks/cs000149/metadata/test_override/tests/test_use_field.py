from tests.utils import run_node


def test_use_field_reset_and_props():
    field = run_node("hooks/useField.js", "createField", ["text", "hello"]).get("result")
    assert field["value"] == "hello"
    reset = run_node("hooks/useField.js", "resetField", [field])
    assert reset["ok"]
    assert reset["result"]["value"] == ""
    props = run_node("hooks/useField.js", "fieldInputProps", [field])
    assert props["ok"]
    assert "reset" not in props["result"]
