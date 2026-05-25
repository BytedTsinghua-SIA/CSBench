from tests.utils import run_node


def test_pubsub_flow():
    pubsub = run_node("backend/subscriptions.js", "createPubSub")
    assert pubsub["ok"]
    subscribed = run_node("backend/subscriptions.js", "subscribeBookAdded", [pubsub["result"], "client1"])
    assert subscribed["ok"]
    published = run_node("backend/subscriptions.js", "publishBookAdded", [subscribed["result"], {"id": "b1"}])
    assert published["ok"]
    assert published["result"]["events"][0]["id"] == "b1"
