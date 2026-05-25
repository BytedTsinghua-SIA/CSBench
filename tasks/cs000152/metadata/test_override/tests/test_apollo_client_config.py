from tests.utils import run_node


def test_apollo_client_config():
    config = run_node(
        "utils/apolloClient.js",
        "createApolloClientConfig",
        [{"apolloUri": "http://localhost:4000"}],
    )
    assert config["ok"]
    assert config["result"]["uri"] == "http://localhost:4000"
    assert config["result"]["fetchPolicy"] == "cache-and-network"
