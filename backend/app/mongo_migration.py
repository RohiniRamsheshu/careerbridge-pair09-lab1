"""Repeatable MySQL-to-Mongo migration with stable source identifiers."""

import json
from datetime import date, datetime, time, timedelta
from decimal import Decimal

from backend.app.database import get_connection
from backend.app.mongo_repository import MongoRepository


TABLE_MAP = {
    "users": "student_accounts",
    "student_profiles": "student_profiles",
    "student_preferences": "preferences",
    "company_profiles": "companies",
    "jobs": "jobs",
    "applications": "applications",
    "events": "events",
    "event_registrations": "registrations",
    "saved_items": "saved_items",
}


def _json_safe(row):
    result = {}
    for key, value in row.items():
        if isinstance(value, (datetime, date)):
            result[key] = value.isoformat()
        elif isinstance(value, (bytes, bytearray)):
            result[key] = value.decode("utf-8", errors="replace")
        elif isinstance(value, Decimal):
            result[key] = str(value)
        elif isinstance(value, timedelta):
            result[key] = str(value)
        elif isinstance(value, time):
            result[key] = value.isoformat()
        else:
            result[key] = value
    return result


def migrate_mysql_to_mongo(connection_factory=get_connection, repository=None, batch_size=100):
    repository = repository or MongoRepository()
    repository.ensure_indexes()
    connection = connection_factory()
    cursor = connection.cursor(dictionary=True)
    counts = {"migrated": {}, "missing_source_tables": [], "errors": []}
    try:
        for table, collection in TABLE_MAP.items():
            try:
                cursor.execute(f"SELECT * FROM {table}")
                rows = cursor.fetchall()
            except Exception as exc:
                counts["missing_source_tables"].append(table)
                counts["errors"].append({"table": table, "error": type(exc).__name__})
                continue
            migrated = 0
            for row in rows:
                safe = _json_safe(row)
                if table == "users":
                    if safe.get("role") == "student":
                        collection = "student_accounts"
                    elif safe.get("role") == "company":
                        collection = "companies"
                    else:
                        continue
                source_id = safe.get("id") or safe.get("user_id") or safe.get("student_user_id")
                if source_id is None:
                    source_id = json.dumps(safe, sort_keys=True, default=str)
                repository.upsert(collection, f"{table}:{source_id}", safe)
                migrated += 1
            counts["migrated"][table] = migrated

        # Resume metadata is derived from application paths without copying files.
        cursor.execute("SELECT id, student_user_id, resume_path FROM applications")
        for row in cursor.fetchall():
            repository.upsert("resumes", f"application:{row['id']}", {
                "application_id": row["id"], "student_user_id": row["student_user_id"],
                "resume_path": row["resume_path"], "metadata_only": True,
            })
        counts["migrated"]["resumes_metadata"] = len(repository.db.resumes.find({"metadata_only": True}).distinct("application_id"))
        for absent in ("sessions", "activity_logs"):
            if absent not in counts["missing_source_tables"]:
                counts["missing_source_tables"].append(absent)
        return counts
    finally:
        cursor.close()
        connection.close()


if __name__ == "__main__":
    print(json.dumps(migrate_mysql_to_mongo(), indent=2, default=str))
