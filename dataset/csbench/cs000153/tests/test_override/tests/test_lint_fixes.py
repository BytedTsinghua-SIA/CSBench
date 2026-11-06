from tests.utils import run_node


def test_lint_env_and_console_override():
    env = run_node("lint/fixes.js", "buildLintEnv")
    assert env["ok"]
    assert env["result"].get("browser") is True
    assert env["result"].get("jest") is True

    override = run_node("lint/fixes.js", "consoleLogOverride")
    assert override["ok"]
    assert "no-console" in override["result"]
