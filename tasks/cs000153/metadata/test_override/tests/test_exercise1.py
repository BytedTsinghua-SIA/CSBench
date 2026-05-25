from tests.utils import run_node


def test_word_count_and_validation():
    words = "word " * 210
    count = run_node("exercise1.js", "countWords", [words])
    assert count["ok"]
    assert count["result"] == 210

    valid = run_node("exercise1.js", "validateEssay", [words, 200, 300])
    assert valid["ok"]
    assert valid["result"]["valid"] is True

    short = run_node("exercise1.js", "validateEssay", ["too short", 200, 300])
    assert short["ok"]
    assert short["result"]["valid"] is False
