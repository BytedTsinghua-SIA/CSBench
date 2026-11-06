from tests.utils import run_node


def test_health_check_workflow():
    result = run_node("workflows/healthCheck.js", "buildHealthCheckWorkflow", [{"url": "https://example.com/health"}])
    assert result["ok"]
    text = result["result"]
    assert "schedule" in text
    assert "url-health-check" in text
    assert "https://example.com/health" in text
