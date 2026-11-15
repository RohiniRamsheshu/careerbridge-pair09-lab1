"""Transactional outbox and durable consumer inbox helpers."""

import json
import logging
import os
from datetime import datetime, timedelta, timezone

from backend.app import config
from backend.app.database import get_connection
from backend.app.events.contracts import EventEnvelope
from backend.app.events.producer import KafkaEventProducer

logger = logging.getLogger("careerbridge.outbox")


def enqueue_event(cursor, envelope: EventEnvelope):
    """Insert an event into the same transaction as its business write."""
    cursor.execute(
        """
        INSERT INTO event_outbox
        (event_id, topic, aggregate_id, aggregate_type, payload, trace_id, occurred_at)
        VALUES (%s, %s, %s, %s, %s, %s, %s)
        """,
        (
            envelope.event_id,
            envelope.topic,
            envelope.aggregate_id,
            envelope.aggregate_type,
            json.dumps(envelope.payload, separators=(",", ":"), sort_keys=True),
            envelope.trace_id,
            envelope.occurred_at,
        ),
    )


def make_event(topic, aggregate_id, aggregate_type, payload, trace_id=None):
    return EventEnvelope.create(topic, aggregate_id, aggregate_type, payload, trace_id)


def record_processed_event(envelope, connection_factory=get_connection):
    """Durably claim an event before its consumer transaction is committed.

    The unique event ID makes redelivery safe across worker restarts. The insert
    is the consumer's idempotent side effect for this foundation; domain-specific
    handlers can be added in the same transaction later.
    """
    connection = connection_factory()
    cursor = connection.cursor()
    try:
        cursor.execute(
            """
            INSERT IGNORE INTO processed_events
            (event_id, topic, aggregate_id, trace_id)
            VALUES (%s, %s, %s, %s)
            """,
            (envelope.event_id, envelope.topic, envelope.aggregate_id, envelope.trace_id),
        )
        connection.commit()
        if cursor.rowcount == 1 and os.getenv("WORKER_CRASH_AFTER_PROCESSING_ONCE") == "1":
            os._exit(17)
        return cursor.rowcount == 1
    except Exception:
        connection.rollback()
        raise
    finally:
        cursor.close()
        connection.close()


def publish_pending_once(connection_factory=get_connection, producer=None):
    """Publish one claimed outbox row and mark it delivered after broker ack."""
    producer = producer or KafkaEventProducer()
    connection = connection_factory()
    cursor = connection.cursor(dictionary=True)
    try:
        now = datetime.now(timezone.utc).replace(tzinfo=None)
        cursor.execute(
            """
            UPDATE event_outbox
            SET status = 'pending', locked_until = NULL
            WHERE status = 'publishing' AND locked_until < %s
            """,
            (now,),
        )
        cursor.execute(
            """
            SELECT * FROM event_outbox
            WHERE status IN ('pending', 'failed')
              AND next_attempt_at <= %s
            ORDER BY id
            LIMIT 1
            FOR UPDATE SKIP LOCKED
            """,
            (now,),
        )
        row = cursor.fetchone()
        if not row:
            connection.commit()
            return None

        locked_until = now + timedelta(seconds=max(config.KAFKA_PUBLISH_TIMEOUT_SECONDS * 2, 10))
        cursor.execute(
            """
            UPDATE event_outbox
            SET status = 'publishing', attempts = attempts + 1, locked_until = %s
            WHERE id = %s
            """,
            (locked_until, row["id"]),
        )
        connection.commit()

        envelope = EventEnvelope(
            topic=row["topic"], event_id=row["event_id"], trace_id=row["trace_id"],
            aggregate_id=row["aggregate_id"], aggregate_type=row["aggregate_type"],
            payload=json.loads(row["payload"]),
            occurred_at=row["occurred_at"].isoformat() if hasattr(row["occurred_at"], "isoformat") else row["occurred_at"],
            schema_version=row.get("schema_version", 1),
        )
        try:
            producer.publish(envelope)
        except Exception as exc:
            cursor.execute(
                """
                UPDATE event_outbox
                SET status = 'failed', last_error = %s,
                    next_attempt_at = DATE_ADD(NOW(), INTERVAL LEAST(60, POW(2, attempts)) SECOND),
                    locked_until = NULL
                WHERE id = %s
                """,
                (type(exc).__name__, row["id"]),
            )
            connection.commit()
            logger.warning("outbox_publish_failed event_id=%s error=%s", envelope.event_id, type(exc).__name__)
            return {"status": "failed", "event_id": envelope.event_id}

        cursor.execute(
            """
            UPDATE event_outbox
            SET status = 'delivered', delivered_at = CURRENT_TIMESTAMP, locked_until = NULL
            WHERE id = %s
            """,
            (row["id"],),
        )
        connection.commit()
        return {"status": "delivered", "event_id": envelope.event_id}
    finally:
        cursor.close()
        connection.close()
