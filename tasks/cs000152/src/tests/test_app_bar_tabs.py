from tests.utils import run_node


def test_app_bar_tabs():
    signed_out = run_node("components/appBar.js", "getAppBarTabs", [{"signedIn": False}])
    assert signed_out["ok"]
    labels = [tab["label"] for tab in signed_out["result"]]
    assert "Repositories" in labels
    assert "Sign in" in labels

    signed_in = run_node("components/appBar.js", "getAppBarTabs", [{"signedIn": True}])
    assert signed_in["ok"]
    labels_in = [tab["label"] for tab in signed_in["result"]]
    assert "Sign out" in labels_in
    assert "Create a review" in labels_in
