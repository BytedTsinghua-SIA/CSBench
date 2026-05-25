from tests.utils import run_node


def test_country_url_and_mapping():
    url = run_node("hooks/useCountry.js", "buildCountryUrl", ["Finland"])
    assert url["ok"]
    assert "Finland" in url["result"]
    mapped = run_node(
        "hooks/useCountry.js",
        "mapCountryResponse",
        ["Finland", {"name": {"common": "Finland"}, "capital": ["Helsinki"]}],
    )
    assert mapped["ok"]
    assert mapped["result"]["found"] is True


def test_country_should_fetch():
    yes = run_node("hooks/useCountry.js", "shouldFetchCountry", ["Finland"])
    no = run_node("hooks/useCountry.js", "shouldFetchCountry", [""])
    assert yes["ok"] and no["ok"]
    assert yes["result"] is True
    assert no["result"] is False
