from tests.utils import run_node


def test_hello_workflow():
    result = run_node("workflows/hello.js", "buildHelloWorkflow")
    assert result["ok"]
    text = result["result"]
    assert "Hello World" in text
    assert "date" in text
    assert "ls -l" in text
