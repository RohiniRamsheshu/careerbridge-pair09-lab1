"""Kafka event envelope and topic contracts.

This module is transport-neutral so synchronous route tests can validate the exact
payload before a Kafka client is introduced. It intentionally performs no I/O.
"""

from dataclasses import asdict, dataclass
from datetime import datetime, timezone
import json
from uuid import uuid4

from backend.app import config


LOGICAL_TOPICS = {
    "application.created",
    "application.updated",
    "application.status_changed",
    "event.registration_created",
    "job.created",
    "memory.updated",
    "memory.consolidate",
}

TOPICS = {f"{config.KAFKA_PREFIX}.{topic}" for topic in LOGICAL_TOPICS}


def dlq_topic(topic):
    """Return the deterministic dead-letter topic for a supported topic."""
    return f"{topic_name(topic)}.dlq"


def topic_name(topic):
    if topic in TOPICS:
        return topic
    if topic in LOGICAL_TOPICS:
        return f"{config.KAFKA_PREFIX}.{topic}"
    raise ValueError(f"Unsupported event topic: {topic}")


@dataclass(frozen=True)
class EventEnvelope:
    topic: str
    event_id: str
    trace_id: str
    aggregate_id: int
    aggregate_type: str
    payload: dict
    occurred_at: str
    schema_version: int = 1

    @classmethod
    def create(cls, topic, aggregate_id, aggregate_type, payload, trace_id=None):
        topic = topic_name(topic)
        if not isinstance(aggregate_id, int) or aggregate_id <= 0:
            raise ValueError("aggregate_id must be a positive integer")
        if not isinstance(payload, dict):
            raise ValueError("payload must be an object")
        return cls(
            topic=topic,
            event_id=str(uuid4()),
            trace_id=trace_id or str(uuid4()),
            aggregate_id=aggregate_id,
            aggregate_type=aggregate_type,
            payload=payload,
            occurred_at=datetime.now(timezone.utc).isoformat(),
        )

    def to_json(self):
        return json.dumps(asdict(self), separators=(",", ":"), sort_keys=True)
