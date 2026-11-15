"""Reusable manual-commit consumer processor with retry and DLQ behavior."""

import logging
import time

from backend.app.events.contracts import EventEnvelope, TOPICS

logger = logging.getLogger("careerbridge.consumer")


class ConsumerProcessor:
    def __init__(self, handler, dlq_publisher, max_retries=3, backoff_seconds=0.1,
                 dedupe=None, raw_dlq_publisher=None):
        self.handler = handler
        self.dlq_publisher = dlq_publisher
        self.max_retries = max_retries
        self.backoff_seconds = backoff_seconds
        self.dedupe = dedupe if dedupe is not None else set()
        self.raw_dlq_publisher = raw_dlq_publisher

    def process(self, raw_value, source_topic=None):
        try:
            envelope = self._decode(raw_value)
        except Exception as exc:
            if self.raw_dlq_publisher is None:
                raise
            for attempt in range(1, self.max_retries + 1):
                if attempt < self.max_retries:
                    time.sleep(self.backoff_seconds * attempt)
            self.raw_dlq_publisher(source_topic, raw_value, exc)
            return {"status": "dlq", "error_type": type(exc).__name__, "attempts": self.max_retries}
        if envelope.event_id in self.dedupe:
            return {"status": "duplicate", "event_id": envelope.event_id}

        last_error = None
        for attempt in range(1, self.max_retries + 1):
            try:
                self.handler(envelope)
                self.dedupe.add(envelope.event_id)
                return {"status": "processed", "event_id": envelope.event_id, "attempt": attempt}
            except Exception as exc:  # bounded retry; offset remains uncommitted until success
                last_error = exc
                if attempt < self.max_retries:
                    time.sleep(self.backoff_seconds * attempt)

        self.dlq_publisher(envelope, last_error)
        return {"status": "dlq", "event_id": envelope.event_id, "attempts": self.max_retries}

    @staticmethod
    def _decode(raw_value):
        import json

        body = json.loads(raw_value) if isinstance(raw_value, str) else raw_value
        if not isinstance(body, dict):
            raise ValueError("event must be a JSON object")
        required = {"topic", "event_id", "trace_id", "aggregate_id", "aggregate_type", "payload", "occurred_at", "schema_version"}
        if set(body) != required or body["topic"] not in TOPICS:
            raise ValueError("invalid event envelope")
        if not isinstance(body["aggregate_id"], int) or not isinstance(body["payload"], dict):
            raise ValueError("invalid event payload")
        return EventEnvelope(**body)


def run_kafka_consumer(topics, group_id, handler, dlq_publisher, consumer_factory=None,
                       processor_factory=None, raw_dlq_publisher=None):
    """Run a real Kafka consumer with manual commits after handler success."""
    if consumer_factory is None:
        from kafka import KafkaConsumer
        consumer_factory = KafkaConsumer
    consumer = consumer_factory(
        *topics,
        bootstrap_servers=__import__("backend.app.config", fromlist=["KAFKA_BOOTSTRAP_SERVERS"]).KAFKA_BOOTSTRAP_SERVERS,
        group_id=group_id,
        enable_auto_commit=False,
        value_deserializer=lambda value: value.decode("utf-8"),
    )
    processor = (processor_factory or ConsumerProcessor)(
        handler, dlq_publisher, raw_dlq_publisher=raw_dlq_publisher
    )
    try:
        for message in consumer:
            result = processor.process(message.value, message.topic)
            if result["status"] in {"processed", "duplicate", "dlq"}:
                consumer.commit()
    finally:
        consumer.close()


def kafka_topic_names(topics):
    """Normalize logical topic names for worker configuration and startup checks."""
    from backend.app.events.contracts import topic_name
    return [topic_name(topic) for topic in topics]
