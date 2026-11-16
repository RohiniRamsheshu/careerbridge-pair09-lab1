"""Kafka producer and dead-letter publisher.

Normal business writes use the transactional outbox in ``events.outbox``. The
legacy ``publish_event`` helper remains an explicitly opt-in, post-commit
best-effort compatibility path for workflows that do not yet enqueue an outbox
row; broker failure never turns a committed API write into an API failure.
"""

import logging
import json

from backend.app import config
from backend.app.events.contracts import EventEnvelope, dlq_topic

logger = logging.getLogger("careerbridge.events")


class KafkaEventProducer:
    def __init__(self, bootstrap_servers=None, producer_factory=None):
        self.bootstrap_servers = bootstrap_servers or config.KAFKA_BOOTSTRAP_SERVERS
        self._producer_factory = producer_factory
        self._producer = None

    def _get_producer(self):
        if self._producer is not None:
            return self._producer
        factory = self._producer_factory
        if factory is None:
            try:
                from kafka import KafkaProducer
            except ImportError as exc:
                raise RuntimeError("kafka-python-ng is not installed") from exc
            factory = KafkaProducer
        self._producer = factory(
            bootstrap_servers=self.bootstrap_servers,
            value_serializer=lambda value: value.encode("utf-8"),
            key_serializer=lambda value: value.encode("utf-8") if value else None,
            acks="all",
            retries=2,
        )
        return self._producer

    def publish(self, envelope: EventEnvelope):
        producer = self._get_producer()
        future = producer.send(
            envelope.topic,
            key=str(envelope.aggregate_id),
            value=envelope.to_json(),
        )
        future.get(timeout=config.KAFKA_PUBLISH_TIMEOUT_SECONDS)
        logger.info(
            "kafka_event_published topic=%s event_id=%s trace_id=%s aggregate_id=%s",
            envelope.topic, envelope.event_id, envelope.trace_id, envelope.aggregate_id,
        )

    def publish_dlq(self, envelope: EventEnvelope, error):
        """Publish the original envelope plus bounded failure metadata to its DLQ."""
        producer = self._get_producer()
        payload = {
            "original_event": envelope.to_json(),
            "error_type": type(error).__name__,
        }
        future = producer.send(
            dlq_topic(envelope.topic),
            key=str(envelope.aggregate_id),
            value=json.dumps(payload, separators=(",", ":"), sort_keys=True),
        )
        future.get(timeout=config.KAFKA_PUBLISH_TIMEOUT_SECONDS)
        logger.warning(
            "kafka_event_dlq topic=%s event_id=%s trace_id=%s error=%s",
            dlq_topic(envelope.topic), envelope.event_id, envelope.trace_id,
            type(error).__name__,
        )

    def publish_raw_dlq(self, source_topic, raw_value, error):
        """Route an undecodable message to the source topic's DLQ."""
        event_id = None
        trace_id = None
        aggregate_id = None
        try:
            raw_body = json.loads(raw_value) if isinstance(raw_value, str) else raw_value
            if isinstance(raw_body, dict):
                event_id = raw_body.get("event_id")
                trace_id = raw_body.get("trace_id")
                aggregate_id = raw_body.get("aggregate_id")
        except (TypeError, json.JSONDecodeError):
            pass
        payload = {
            "original_raw": str(raw_value)[:10000],
            "source_topic": source_topic,
            "event_type": source_topic,
            "event_id": event_id,
            "trace_id": trace_id,
            "aggregate_id": aggregate_id,
            "error_type": type(error).__name__,
        }
        producer = self._get_producer()
        future = producer.send(
            dlq_topic(source_topic), key=None,
            value=json.dumps(payload, separators=(",", ":"), sort_keys=True),
        )
        future.get(timeout=config.KAFKA_PUBLISH_TIMEOUT_SECONDS)


_producer = KafkaEventProducer()


def publish_event(topic, aggregate_id, aggregate_type, payload, trace_id=None):
    """Publish only when explicitly enabled; never turns a committed API write into an error."""
    if not config.KAFKA_ENABLED:
        return False
    envelope = EventEnvelope.create(
        topic, aggregate_id, aggregate_type, payload, trace_id=trace_id
    )
    try:
        _producer.publish(envelope)
        return True
    except Exception as exc:  # broker outages must not corrupt the committed API operation
        logger.warning(
            "kafka_event_publish_failed topic=%s event_id=%s error=%s",
            envelope.topic, envelope.event_id, type(exc).__name__,
        )
        return False
