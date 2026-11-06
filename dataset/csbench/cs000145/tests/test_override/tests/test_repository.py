import json
import tempfile
from pathlib import Path

from tests.utils import run_node


def test_repository_seeds_data_when_missing():
    with tempfile.TemporaryDirectory() as tmpdir:
        db_path = str(Path(tmpdir) / "phonebook.json")
        result = run_node("phonebook/repository.js", "repoList", [db_path])
        assert result["ok"]
        assert len(result["result"]) == 4


def test_repository_add_and_list():
    with tempfile.TemporaryDirectory() as tmpdir:
        db_path = str(Path(tmpdir) / "phonebook.json")
        add_result = run_node(
            "phonebook/repository.js",
            "repoAdd",
            [db_path, {"name": "Grace Hopper", "number": "040-22334455"}],
        )
        assert add_result["ok"]
        list_result = run_node("phonebook/repository.js", "repoList", [db_path])
        assert list_result["ok"]
        assert len(list_result["result"]) == 5


def test_repository_update_and_find():
    with tempfile.TemporaryDirectory() as tmpdir:
        db_path = str(Path(tmpdir) / "phonebook.json")
        add_result = run_node(
            "phonebook/repository.js",
            "repoAdd",
            [db_path, {"name": "Grace Hopper", "number": "040-22334455"}],
        )
        assert add_result["ok"]
        created_id = add_result["result"]["id"]
        update_result = run_node(
            "phonebook/repository.js",
            "repoUpdate",
            [db_path, created_id, {"number": "09-123456"}],
        )
        assert update_result["ok"]
        find_result = run_node(
            "phonebook/repository.js",
            "repoFindById",
            [db_path, created_id],
        )
        assert find_result["ok"]
        assert find_result["result"]["number"] == "09-123456"


def test_repository_remove():
    with tempfile.TemporaryDirectory() as tmpdir:
        db_path = str(Path(tmpdir) / "phonebook.json")
        list_result = run_node("phonebook/repository.js", "repoList", [db_path])
        assert list_result["ok"]
        first_id = list_result["result"][0]["id"]
        remove_result = run_node(
            "phonebook/repository.js",
            "repoRemove",
            [db_path, first_id],
        )
        assert remove_result["ok"]
        assert remove_result["result"] is True


def test_repository_upsert_by_name_updates_existing():
    with tempfile.TemporaryDirectory() as tmpdir:
        db_path = str(Path(tmpdir) / "phonebook.json")
        upsert_result = run_node(
            "phonebook/repository.js",
            "repoUpsertByName",
            [db_path, {"name": "Arto Hellas", "number": "050-9999999"}],
        )
        assert upsert_result["ok"]
        assert upsert_result["result"]["updated"] is True
        assert upsert_result["result"]["person"]["number"] == "050-9999999"
