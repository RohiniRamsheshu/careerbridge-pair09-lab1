from types import SimpleNamespace
from datetime import date, time, timedelta
from decimal import Decimal
from dataclasses import dataclass

from backend.app.memory_consolidation import consolidate_student, seed_synthetic_memories
from backend.app.mongo_migration import _json_safe
from backend.app.mongo_repository import DEFAULT_ASSISTANT_RULES, MongoRepository


class FakeCollection:
    def __init__(self, repo):
        self.repo = repo

    def update_many(self, selector, update):
        ids = set(selector["_id"]["$in"])
        for item in self.repo.docs:
            if item["_id"] in ids:
                item.update(update["$set"])


class FakeRulesCollection:
    def __init__(self):
        self.docs = {}

    @dataclass
    class Result:
        upserted_id: object = None

    def update_one(self, selector, update, upsert=False):
        key = selector["rule_key"]
        if key in self.docs:
            return self.Result()
        if not upsert:
            return self.Result()
        self.docs[key] = dict(update["$setOnInsert"])
        return self.Result(upserted_id=key)


class FakeExplicitMemoryCollection:
    @dataclass
    class Result:
        upserted_id: object = None

    def __init__(self):
        self.docs = []

    def update_one(self, selector, update, upsert=False):
        for document in self.docs:
            if all(document.get(key) == value for key, value in selector.items()):
                document.update(update["$set"])
                return self.Result()
        if upsert:
            document = {**update["$setOnInsert"], **update["$set"]}
            document["_id"] = len(self.docs) + 1
            self.docs.append(document)
            return self.Result(upserted_id=document["_id"])
        return self.Result()

    def find_one(self, selector):
        return next((document for document in self.docs if all(document.get(key) == value for key, value in selector.items())), None)


class FakeRepo:
    def __init__(self):
        self.docs = []
        self.next_id = 1
        self.db = SimpleNamespace(student_memory=FakeCollection(self))

    def add_memory(self, student_user_id, memory_key, value, **kwargs):
        item = {"_id": self.next_id, "student_user_id": student_user_id,
                "memory_key": memory_key, "value": value, "active": True,
                "confidence": kwargs.get("confidence", 1.0),
                "source": kwargs.get("source", "synthetic"), "updated_at": None}
        self.next_id += 1
        self.docs.append(item)
        return item

    def relevant_memory(self, student_user_id, query=None, limit=20):
        return [item for item in self.docs if item["student_user_id"] == student_user_id and item.get("active")][:limit]


def test_synthetic_memory_consolidates_to_fewer_than_40_active_entries():
    repo = FakeRepo()
    seed_synthetic_memories(repo, 11, total=60)

    grouped = {}
    for item in repo.docs:
        grouped.setdefault(item["memory_key"], []).append(item["value"])
    assert sum(len(items) > 1 for items in grouped.values()) >= 3
    assert sum(len(set(items)) > 1 for items in grouped.values()) >= 3

    result = consolidate_student(repo, 11)

    assert result["before"] == 60
    assert result["after"] < 40
    assert len(result["decisions"]) >= 6
    assert sum(item.get("active") is True for item in repo.docs) == result["after"]


def test_migration_json_conversion_preserves_password_hash_and_dates():
    row = {"id": 4, "role": "student", "password_hash": "$2b$12$hash", "created_at": __import__("datetime").datetime(2026, 11, 13),
           "deadline": date(2026, 12, 31), "event_time": time(10, 30),
           "salary": Decimal("120000.00"), "duration": timedelta(hours=1)}

    converted = _json_safe(row)

    assert converted["password_hash"] == row["password_hash"]
    assert converted["created_at"] == "2026-11-13T00:00:00"
    assert converted["deadline"] == "2026-12-31"
    assert converted["event_time"] == "10:30:00"
    assert converted["salary"] == "120000.00"
    assert converted["duration"] == "1:00:00"


def test_memory_retrieval_is_scoped_to_authenticated_student():
    repo = FakeRepo()
    repo.add_memory(11, "preferred_city", "San Jose")
    repo.add_memory(12, "preferred_city", "Palo Alto")

    assert [item["value"] for item in repo.relevant_memory(11)] == ["San Jose"]
    assert [item["value"] for item in repo.relevant_memory(12)] == ["Palo Alto"]


def make_rule_repository(existing=None):
    rules = FakeRulesCollection()
    rules.docs.update(existing or {})
    repository = MongoRepository.__new__(MongoRepository)
    repository.db = SimpleNamespace(assistant_rules=rules)
    return repository, rules


def test_default_assistant_rules_first_invocation_inserts_all_defaults():
    repository, rules = make_rule_repository()

    assert repository.ensure_default_rules() == len(DEFAULT_ASSISTANT_RULES)
    assert set(rules.docs) == {item["rule_key"] for item in DEFAULT_ASSISTANT_RULES}


def test_default_assistant_rules_second_invocation_inserts_zero():
    repository, rules = make_rule_repository()

    repository.ensure_default_rules()
    assert repository.ensure_default_rules() == 0
    assert set(rules.docs) == {item["rule_key"] for item in DEFAULT_ASSISTANT_RULES}


def test_default_assistant_rules_preserve_customized_existing_rule():
    key = DEFAULT_ASSISTANT_RULES[0]["rule_key"]
    custom = {key: {"rule_key": key, "text": "Custom privacy policy", "active": True}}
    repository, rules = make_rule_repository(custom)

    assert repository.ensure_default_rules() == len(DEFAULT_ASSISTANT_RULES) - 1
    assert rules.docs[key]["text"] == "Custom privacy policy"


def test_default_assistant_rules_insert_only_missing_defaults():
    existing = {item["rule_key"]: dict(item) for item in DEFAULT_ASSISTANT_RULES[:2]}
    repository, rules = make_rule_repository(existing)

    assert repository.ensure_default_rules() == 1
    assert set(rules.docs) == {item["rule_key"] for item in DEFAULT_ASSISTANT_RULES}


def test_explicit_memory_upsert_updates_same_key_without_duplicate_active_records(monkeypatch):
    collection = FakeExplicitMemoryCollection()
    repository = MongoRepository.__new__(MongoRepository)
    repository.db = SimpleNamespace(student_memory=collection)
    monkeypatch.setattr("backend.app.mongo_repository.config.KAFKA_ENABLED", False)

    first = repository.save_explicit_memory(12, "preferred_project_name", "CareerBridge Demo", "preference")
    second = repository.save_explicit_memory(12, "preferred_project_name", "CareerBridge Demo 2", "preference")

    assert first["student_user_id"] == 12
    assert second["value"] == "CareerBridge Demo 2"
    assert len(collection.docs) == 1
    assert collection.docs[0]["active"] is True
