from types import SimpleNamespace
from datetime import date, time, timedelta
from decimal import Decimal

from backend.app.memory_consolidation import consolidate_student, seed_synthetic_memories
from backend.app.mongo_migration import _json_safe


class FakeCollection:
    def __init__(self, repo):
        self.repo = repo

    def update_many(self, selector, update):
        ids = set(selector["_id"]["$in"])
        for item in self.repo.docs:
            if item["_id"] in ids:
                item.update(update["$set"])


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
