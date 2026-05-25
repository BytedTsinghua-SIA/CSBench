from tests.utils import run_node


def test_e2e_config_and_tests():
    config = run_node("e2e/config.js", "buildE2EConfig")
    assert config["ok"]
    assert "e2e-tests" in config["result"]["jestIgnore"]
    assert config["result"]["script"] == "test:e2e"

    tests = run_node("e2e/config.js", "buildE2ETests")
    assert tests["ok"]
    assert any("ivysaur" in test for test in tests["result"])
    assert any("chlorophyll" in test for test in tests["result"])
