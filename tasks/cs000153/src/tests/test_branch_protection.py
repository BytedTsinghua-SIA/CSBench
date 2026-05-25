from tests.utils import run_node


def test_branch_protection_rules():
    basic = run_node("repo/protection.js", "buildProtectionRules")
    assert basic["ok"]
    assert basic["result"]["requireReviews"] is True
    assert basic["result"]["requireStatusChecks"] is True

    strict = run_node("repo/protection.js", "buildStrictProtectionRules")
    assert strict["ok"]
    assert strict["result"]["requireAdminReview"] is True
