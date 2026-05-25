from tests.utils import run_node


def test_fly_toml_and_health_check():
    toml = run_node("deploy/fly.js", "buildFlyToml")
    assert toml["ok"]
    assert "PORT" in toml["result"]
    assert "internal_port" in toml["result"]
    assert "processes" in toml["result"]
    assert "canary" in toml["result"]

    health = run_node("deploy/fly.js", "buildHealthCheckConfig", ["/health"])
    assert health["ok"]
    assert "/health" in health["result"]

    step = run_node("deploy/fly.js", "buildDeployStep", ["FLY_API_TOKEN"])
    assert step["ok"]
    assert "FLY_API_TOKEN" in step["result"]
