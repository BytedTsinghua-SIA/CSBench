from tests.utils import run_node


def test_missing_name():
    result = run_node(
        "phonebook/validators.js",
        "validateNewPerson",
        [{"name": "", "number": "09-123456"}, []],
    )
    assert result["ok"]
    assert result["result"] == "name is required"


def test_missing_number():
    result = run_node(
        "phonebook/validators.js",
        "validateNewPerson",
        [{"name": "Ada Lovelace", "number": ""}, []],
    )
    assert result["ok"]
    assert result["result"] == "number is required"


def test_duplicate_name():
    result = run_node(
        "phonebook/validators.js",
        "validateNewPerson",
        [{"name": "Arto Hellas", "number": "09-123456"}, ["Arto Hellas"]],
    )
    assert result["ok"]
    assert result["result"] == "name must be unique"


def test_name_length():
    result = run_node(
        "phonebook/validators.js",
        "validateNameLength",
        ["Al", 3],
    )
    assert result["ok"]
    assert result["result"] == "name must be at least 3 characters"


def test_number_format():
    result = run_node(
        "phonebook/validators.js",
        "validateNumberFormat",
        ["10-22-334455"],
    )
    assert result["ok"]
    assert result["result"] == "number must be formatted like 09-123456"


def test_valid_person():
    result = run_node(
        "phonebook/validators.js",
        "validateNewPerson",
        [{"name": "Grace Hopper", "number": "040-22334455"}, []],
    )
    assert result["ok"]
    assert result["result"] is None
