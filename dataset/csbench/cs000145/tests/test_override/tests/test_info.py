from tests.utils import run_node


def test_info_html_includes_count_and_date():
    result = run_node(
        "phonebook/info.js",
        "buildInfoHtml",
        [2, "Mon Jan 1 00:00:00 2024"],
    )
    assert result["ok"]
    assert "Phonebook has info for 2 people" in result["result"]
    assert "Mon Jan 1 00:00:00 2024" in result["result"]
