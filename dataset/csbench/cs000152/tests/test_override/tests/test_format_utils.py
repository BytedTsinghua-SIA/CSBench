from tests.utils import run_node


def test_format_count_and_date():
    count = run_node("utils/format.js", "formatCount", [8439])
    assert count["ok"]
    assert count["result"] == "8.4k"
    small = run_node("utils/format.js", "formatCount", [999])
    assert small["ok"]
    assert small["result"] == "999"

    date = run_node("utils/format.js", "formatDate", ["2020-01-02T00:00:00.000Z"])
    assert date["ok"]
    assert date["result"] == "02.01.2020"
