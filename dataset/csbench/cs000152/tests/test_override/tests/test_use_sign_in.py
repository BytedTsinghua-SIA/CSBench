from tests.utils import run_node


def test_sign_in_flow_and_sign_out():
    result = run_node(
        "hooks/useSignIn.js",
        "createSignIn",
        [{"username": "ada", "password": "secret"}, {"accessToken": "tok", "store": True, "reset": True}],
    )
    assert result["ok"]
    assert result["result"]["variables"]["credentials"]["username"] == "ada"
    assert result["result"]["callOrder"] == ["mutate", "store", "reset"]

    signed_out = run_node(
        "hooks/useSignIn.js",
        "signOut",
        [{"store": True, "reset": True}],
    )
    assert signed_out["ok"]
    assert signed_out["result"]["callOrder"] == ["remove", "reset"]
