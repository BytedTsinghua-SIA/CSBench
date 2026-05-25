from tests.utils import run_node


def test_env_apollo_uri():
    expo = {"extra": {"apolloUri": "http://localhost:4000"}}
    uri = run_node("utils/env.js", "getApolloUri", [expo, "fallback"])
    assert uri["ok"]
    assert uri["result"] == "http://localhost:4000"
