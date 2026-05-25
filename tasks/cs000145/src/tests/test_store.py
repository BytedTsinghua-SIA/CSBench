from tests.utils import run_node

SEED = [
    {"id": "1", "name": "Arto Hellas", "number": "040-123456"},
    {"id": "2", "name": "Ada Lovelace", "number": "39-44-5323523"},
    {"id": "3", "name": "Dan Abramov", "number": "12-43-234345"},
    {"id": "4", "name": "Mary Poppendieck", "number": "39-23-6423122"},
]


def test_add_person_assigns_id():
    result = run_node(
        "phonebook/store.js",
        "addPerson",
        [SEED, {"name": "Grace Hopper", "number": "040-22334455"}, {}],
    )
    assert result["ok"]
    created = result["result"]["person"]
    assert created["id"]
    assert created["name"] == "Grace Hopper"


def test_add_person_duplicate_name_fails():
    result = run_node(
        "phonebook/store.js",
        "addPerson",
        [SEED, {"name": "Arto Hellas", "number": "09-123456"}, {}],
    )
    assert not result["ok"]


def test_remove_person():
    result = run_node(
        "phonebook/store.js",
        "removePerson",
        [SEED, "2"],
    )
    assert result["ok"]
    assert result["result"]["removed"] is True
    assert len(result["result"]["persons"]) == 3


def test_update_person_number():
    result = run_node(
        "phonebook/store.js",
        "updatePerson",
        [SEED, "3", {"number": "040-1111111"}],
    )
    assert result["ok"]
    updated = result["result"]["person"]
    assert updated["number"] == "040-1111111"


def test_update_person_duplicate_name_fails():
    result = run_node(
        "phonebook/store.js",
        "updatePerson",
        [SEED, "3", {"name": "Ada Lovelace"}],
    )
    assert not result["ok"]
