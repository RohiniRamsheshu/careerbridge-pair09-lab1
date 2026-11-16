"""MongoDB repositories for migration, assistant memory and conversations."""

from datetime import datetime, timezone

from backend.app import config
from backend.app.events.producer import publish_event


COLLECTIONS = ("student_accounts", "student_profiles", "preferences", "sessions",
               "companies", "jobs", "applications", "resumes", "events",
               "registrations", "saved_items", "activity_logs", "assistant_rules",
               "student_memory", "conversations")

DEFAULT_ASSISTANT_RULES = (
    {
        "rule_key": "privacy.student_data",
        "text": "Never reveal another student's private information.",
        "category": "privacy",
    },
    {
        "rule_key": "eligibility.requirements",
        "text": "Always state eligibility requirements when they are available.",
        "category": "reliability",
    },
    {
        "rule_key": "writes.confirmation",
        "text": "Require explicit confirmation before a save or other state-changing action.",
        "category": "safety",
    },
)


class MongoRepository:
    def __init__(self, uri=None, database=None, client=None):
        if client is None:
            try:
                from pymongo import MongoClient
            except ImportError as exc:
                raise RuntimeError("pymongo is not installed") from exc
            client = MongoClient(uri or config.MONGO_URI, serverSelectionTimeoutMS=3000)
        self.client = client
        self.db = client[database or config.MONGO_DB]

    def ping(self):
        self.client.admin.command("ping")
        return True

    def ensure_indexes(self):
        self.db.student_accounts.create_index("source_id", unique=True)
        self.db.student_profiles.create_index("user_id", unique=True)
        self.db.preferences.create_index("student_user_id", unique=True)
        self.db.sessions.create_index("expires_at", expireAfterSeconds=0)
        self.db.companies.create_index("source_id", unique=True)
        self.db.jobs.create_index("source_id", unique=True)
        self.db.applications.create_index("source_id", unique=True)
        self.db.resumes.create_index([("student_user_id", 1), ("source_id", 1)], unique=True)
        self.db.events.create_index("source_id", unique=True)
        self.db.registrations.create_index("source_id", unique=True)
        self.db.saved_items.create_index("source_id", unique=True)
        self.db.activity_logs.create_index("created_at")
        self.db.assistant_rules.create_index("rule_key", unique=True)
        self.db.student_memory.create_index([("student_user_id", 1), ("active", 1)])
        self.db.student_memory.create_index([("student_user_id", 1), ("memory_key", 1)])
        self.db.conversations.create_index([("student_user_id", 1), ("conversation_id", 1)], unique=True)

    def upsert(self, collection, source_id, document):
        payload = dict(document)
        payload["source_id"] = str(source_id)
        self.db[collection].replace_one({"source_id": str(source_id)}, payload, upsert=True)

    def add_memory(self, student_user_id, memory_key, value, kind="fact", confidence=1.0,
                   source="user", temporary=False, provenance=None):
        now = datetime.now(timezone.utc)
        document = {
            "student_user_id": int(student_user_id), "memory_key": memory_key,
            "value": value, "kind": kind, "confidence": float(confidence),
            "source": source, "temporary": bool(temporary), "active": True,
            "provenance": provenance or [], "created_at": now, "updated_at": now,
        }
        result = self.db.student_memory.insert_one(document)
        document["_id"] = result.inserted_id
        if config.KAFKA_ENABLED:
            publish_event(
                "memory.updated", int(student_user_id), "student_memory",
                {"memory_id": str(result.inserted_id), "memory_key": memory_key},
            )
        return document

    def save_explicit_memory(self, student_user_id, memory_key, value, kind="fact"):
        """Create or update one explicitly user-approved active memory.

        The general ``add_memory`` method remains insert-only for the
        consolidation fixture. User-facing writes use this atomic key-scoped
        upsert so repeated explicit requests do not create active duplicates.
        """
        now = datetime.now(timezone.utc)
        student_id = int(student_user_id)
        selector = {
            "student_user_id": student_id,
            "memory_key": memory_key,
            "active": True,
        }
        update = {
            "$set": {
                "value": value,
                "kind": kind,
                "confidence": 1.0,
                "source": "user",
                "temporary": False,
                "updated_at": now,
            },
            "$setOnInsert": {
                "student_user_id": student_id,
                "memory_key": memory_key,
                "active": True,
                "provenance": ["explicit user memory request"],
                "created_at": now,
            },
        }
        result = self.db.student_memory.update_one(selector, update, upsert=True)
        if config.KAFKA_ENABLED:
            publish_event(
                "memory.updated", student_id, "student_memory",
                {"memory_key": memory_key, "operation": "upsert"},
            )
        document = self.db.student_memory.find_one(selector)
        if document is None and result.upserted_id is not None:
            document = {"_id": result.upserted_id, **update["$setOnInsert"], **update["$set"]}
        return document

    def relevant_memory(self, student_user_id, query=None, limit=20):
        query_filter = {"student_user_id": int(student_user_id), "active": True}
        if query:
            query_filter["$or"] = [
                {"memory_key": {"$regex": query, "$options": "i"}},
                {"value": {"$regex": query, "$options": "i"}},
                {"kind": {"$regex": query, "$options": "i"}},
            ]
        return list(self.db.student_memory.find(query_filter).sort("updated_at", -1).limit(limit))

    def rules(self, limit=20):
        return list(self.db.assistant_rules.find({"active": True}).limit(limit))

    def ensure_default_rules(self, rules=None):
        """Explicitly seed approved rules without duplicating existing rules.

        This is intentionally opt-in. Repository construction and normal
        assistant requests never write to MongoDB, which keeps environment
        initialization separate from request handling.
        """
        inserted = 0
        for rule in rules or DEFAULT_ASSISTANT_RULES:
            payload = dict(rule)
            payload.setdefault("active", True)
            result = self.db.assistant_rules.update_one(
                {"rule_key": payload["rule_key"]},
                {"$setOnInsert": payload},
                upsert=True,
            )
            inserted += int(result.upserted_id is not None)
        return inserted

    def get_conversation(self, student_user_id, conversation_id):
        return self.db.conversations.find_one({"student_user_id": int(student_user_id), "conversation_id": conversation_id})

    def save_conversation(self, student_user_id, conversation_id, messages):
        now = datetime.now(timezone.utc)
        self.db.conversations.update_one(
            {"student_user_id": int(student_user_id), "conversation_id": conversation_id},
            {"$set": {"messages": messages[-100:], "updated_at": now},
             "$setOnInsert": {"created_at": now}}, upsert=True,
        )

    def memory_context(self, student_user_id, query):
        memories = self.relevant_memory(student_user_id, query=query, limit=8)
        rules = self.rules(limit=8)
        lines = ["<memory_context>"]
        lines.extend(f"rule: {item.get('text', '')}" for item in rules)
        lines.extend(f"student_memory: {item.get('memory_key')}: {item.get('value')}" for item in memories)
        lines.append("</memory_context>")
        return "\n".join(lines)

    def memory_summary(self, student_user_id):
        return [{key: value for key, value in item.items() if key not in {"_id"}}
                for item in self.relevant_memory(student_user_id, limit=50)]
