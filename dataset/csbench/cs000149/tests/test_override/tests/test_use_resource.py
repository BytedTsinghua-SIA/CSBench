from tests.utils import run_node


def test_resource_hook_create():
    hook = run_node("hooks/useResource.js", "createResourceHook", ["/api/items", []])
    assert hook["ok"]
    resources = hook["result"]["resources"]
    service = hook["result"]["service"]
    assert resources == []
    assert service["baseUrl"] == "/api/items"
