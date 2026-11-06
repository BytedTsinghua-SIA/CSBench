from tests.utils import run_node


def test_sign_up_validation():
    errors = run_node(
        "components/signUp.js",
        "validateSignUp",
        [{"username": "abc", "password": "1234", "passwordConfirm": "123"}],
    )
    assert errors["ok"]
    assert "username" in errors["result"]
    assert "password" in errors["result"]
    assert "passwordConfirm" in errors["result"]
