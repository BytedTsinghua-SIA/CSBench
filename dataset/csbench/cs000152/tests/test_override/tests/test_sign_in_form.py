from tests.utils import run_node


def test_sign_in_form_fields_and_validation():
    fields = run_node("components/signIn.js", "buildSignInFields")
    assert fields["ok"]
    assert len(fields["result"]) == 2
    names = [field["name"] for field in fields["result"]]
    assert "username" in names and "password" in names

    errors = run_node("components/signIn.js", "validateSignIn", [{"username": "", "password": ""}])
    assert errors["ok"]
    assert "username" in errors["result"]


def test_sign_in_submit_calls():
    result = run_node(
        "components/signIn.js",
        "submitSignIn",
        [{"username": "ada", "password": "secret"}, {"track": True}],
    )
    assert result["ok"]
    assert result["result"]["called"] is True
    assert result["result"]["values"]["username"] == "ada"
