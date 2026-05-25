from tests.utils import run_node


def test_dockerignore_update():
    content = "node_modules\ndist\n.env\n"
    result = run_node("deploy/dockerignore.js", "updateDockerignore", [content])
    assert result["ok"]
    assert "dist" not in result["result"].split("\n")
