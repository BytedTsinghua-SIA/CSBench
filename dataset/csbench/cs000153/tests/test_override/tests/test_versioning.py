from tests.utils import run_node


def test_tag_job_and_skip():
    job = run_node("workflows/versioning.js", "buildTagJob")
    assert job["ok"]
    assert "github-tag-action" in job["result"]
    assert "DEFAULT_BUMP" in job["result"]

    skip = run_node("workflows/versioning.js", "shouldSkipCommit", ["feat: change #skip"])
    assert skip["ok"]
    assert skip["result"] is True
