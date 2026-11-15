"""Deterministic, auditable student-memory consolidation rules."""

from datetime import datetime, timezone


def _winner(items):
    source_rank = {"user": 3, "profile": 2, "inferred": 1, "synthetic": 0}
    return max(items, key=lambda item: (
        float(item.get("confidence", 0)),
        source_rank.get(item.get("source"), 0),
        item.get("updated_at") or datetime.min.replace(tzinfo=timezone.utc),
    ))


def consolidate_student(repo, student_user_id):
    memories = repo.relevant_memory(student_user_id, limit=1000)
    groups = {}
    for memory in memories:
        groups.setdefault(memory.get("memory_key") or str(memory.get("_id")), []).append(memory)
    decisions = []
    active_ids = set()
    for key, items in groups.items():
        winner = _winner(items)
        active_ids.add(winner["_id"])
        losers = [item for item in items if item["_id"] != winner["_id"]]
        if losers:
            decisions.append({"memory_key": key, "kept": str(winner["_id"]),
                              "merged": [str(item["_id"]) for item in losers],
                              "reason": "confidence, source priority, then recency"})
            repo.db.student_memory.update_many(
                {"_id": {"$in": [item["_id"] for item in losers]}},
                {"$set": {"active": False, "consolidated_into": winner["_id"], "consolidated_at": datetime.now(timezone.utc)}},
            )
    return {"before": len(memories), "after": len(active_ids), "decisions": decisions}


def seed_synthetic_memories(repo, student_user_id, total=60):
    if total < 60:
        raise ValueError("synthetic memory dataset must contain at least 60 entries")
    for index in range(total):
        key = f"synthetic.fact.{index % 30}"
        value = f"value-{index % 30}"
        if index in {30, 31, 32}:
            key = f"synthetic.fact.{index - 27}"
            value = f"value-{index - 27}"
        if index in {33, 34, 35}:
            key = f"synthetic.fact.{index - 33}"
            value = "newer-contradictory-value"
        repo.add_memory(student_user_id, key, value, kind="preference", confidence=0.8,
                        source="synthetic", provenance=["lab2 synthetic fixture"])
