from tests.utils import run_node


def test_eslint_config_and_script():
    config = run_node("setup/eslint.js", "createEslintConfig")
    assert config["ok"]
    assert "react" in config["result"]["plugins"]
    assert "react-native" in config["result"]["plugins"]
    lint = run_node("setup/eslint.js", "createLintScript")
    assert lint["ok"]
    assert "eslint" in lint["result"]
