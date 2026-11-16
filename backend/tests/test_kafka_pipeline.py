import json

import pytest

from backend.app.events.consumer import ConsumerProcessor, run_kafka_consumer
from backend.app.events.contracts import EventEnvelope, dlq_topic
from backend.app.events.producer import KafkaEventProducer


class FakeFuture:
    def __init__(self):
        self.waited = False

    def get(self, timeout):
        self.waited = True
        return {"offset": 1}


class FakeProducer:
    def __init__(self, **kwargs):
        self.kwargs = kwargs
        self.sent = []
        self.future = FakeFuture()

    def send(self, topic, key, value):
        self.sent.append((topic, key, value))
        return self.future


def test_producer_serializes_typed_envelope_and_waits_for_broker_ack():
    fake = FakeProducer()
    producer = KafkaEventProducer(producer_factory=lambda **kwargs: fake)
    envelope = EventEnvelope.create("job.created", 12, "job", {"title": "Data role"})

    producer.publish(envelope)

    assert fake.sent[0][0] == "p09.job.created"
    assert fake.sent[0][1] == "12"
    assert json.loads(fake.sent[0][2])["event_id"] == envelope.event_id
    assert fake.future.waited is True


def test_dlq_topic_keeps_pair_prefix_and_event_name():
    assert dlq_topic("job.created") == "p09.job.created.dlq"


def test_raw_dlq_retains_safe_correlation_metadata():
    fake = FakeProducer()
    producer = KafkaEventProducer(producer_factory=lambda **kwargs: fake)
    envelope = EventEnvelope.create("job.created", 12, "job", {"title": "Bad"})

    producer.publish_raw_dlq(envelope.topic, envelope.to_json(), ValueError("invalid"))

    dlq_body = json.loads(fake.sent[0][2])
    assert dlq_body["source_topic"] == envelope.topic
    assert dlq_body["event_type"] == envelope.topic
    assert dlq_body["event_id"] == envelope.event_id
    assert dlq_body["trace_id"] == envelope.trace_id
    assert dlq_body["aggregate_id"] == envelope.aggregate_id
    assert "Bad" in dlq_body["original_raw"]


def test_consumer_duplicate_is_idempotent_and_handler_runs_once():
    calls = []
    dlq = []
    envelope = EventEnvelope.create("application.created", 4, "application", {"job_id": 2})
    processor = ConsumerProcessor(lambda event: calls.append(event.event_id), lambda event, error: dlq.append(error))

    first = processor.process(envelope.to_json())
    second = processor.process(envelope.to_json())

    assert first["status"] == "processed"
    assert second["status"] == "duplicate"
    assert calls == [envelope.event_id]
    assert dlq == []


def test_consumer_retries_then_routes_poison_message_to_dlq():
    attempts = []
    dlq = []
    envelope = EventEnvelope.create("job.created", 9, "job", {"title": "Poison"})

    def failing_handler(_event):
        attempts.append(1)
        raise RuntimeError("unprocessable")

    processor = ConsumerProcessor(failing_handler, lambda event, error: dlq.append((event.event_id, str(error))), max_retries=3, backoff_seconds=0)
    result = processor.process(envelope.to_json())

    assert result == {"status": "dlq", "event_id": envelope.event_id, "attempts": 3}
    assert len(attempts) == 3
    assert dlq == [(envelope.event_id, "unprocessable")]


@pytest.mark.parametrize("raw", ["{}", "[]", json.dumps({"topic": "p09.unknown"})])
def test_consumer_rejects_malformed_envelope(raw):
    processor = ConsumerProcessor(lambda event: None, lambda event, error: None)
    with pytest.raises((ValueError, json.JSONDecodeError)):
        processor.process(raw)


def test_consumer_routes_malformed_envelope_to_raw_dlq_after_bounded_retries():
    raw_dlq = []
    processor = ConsumerProcessor(
        lambda event: None, lambda event, error: None,
        max_retries=2, backoff_seconds=0,
        raw_dlq_publisher=lambda topic, raw, error: raw_dlq.append((topic, raw, type(error).__name__)),
    )
    result = processor.process("not-json", "p09.job.created")
    assert result["status"] == "dlq"
    assert result["attempts"] == 2
    assert raw_dlq == [("p09.job.created", "not-json", "JSONDecodeError")]


def test_consumer_commits_only_after_successful_handler():
    envelope = EventEnvelope.create("job.created", 9, "job", {"title": "Safe"})
    observations = []

    class Message:
        topic = envelope.topic
        value = envelope.to_json()

    class FakeConsumer:
        instance = None

        def __init__(self, *_topics, **_kwargs):
            self.commits = 0
            self.closed = False
            FakeConsumer.instance = self

        def __iter__(self):
            return iter([Message()])

        def commit(self):
            self.commits += 1

        def close(self):
            self.closed = True

    def handler(_event):
        observations.append(FakeConsumer.instance.commits)

    run_kafka_consumer(
        [envelope.topic],
        "p09-test-workers",
        handler,
        lambda _event, _error: None,
        consumer_factory=FakeConsumer,
    )

    assert observations == [0]
    assert FakeConsumer.instance.commits == 1
    assert FakeConsumer.instance.closed is True


def test_consumer_rejects_invalid_event_identity_and_aggregate_id():
    envelope = json.loads(EventEnvelope.create("job.created", 9, "job", {}).to_json())
    envelope["event_id"] = 17
    with pytest.raises(ValueError, match="invalid event payload"):
        ConsumerProcessor(lambda _event: None, lambda _event, _error: None).process(envelope)

    envelope = json.loads(EventEnvelope.create("job.created", 9, "job", {}).to_json())
    envelope["aggregate_id"] = 0
    with pytest.raises(ValueError, match="invalid event payload"):
        ConsumerProcessor(lambda _event: None, lambda _event, _error: None).process(envelope)


def test_consumer_retry_does_not_commit_until_retry_succeeds():
    envelope = EventEnvelope.create("job.created", 9, "job", {"title": "Retry"})
    calls = []

    class Message:
        topic = envelope.topic
        value = envelope.to_json()

    class FakeConsumer:
        instance = None

        def __init__(self, *_topics, **_kwargs):
            self.commits = 0
            FakeConsumer.instance = self

        def __iter__(self):
            return iter([Message()])

        def commit(self):
            self.commits += 1

        def close(self):
            pass

    def handler(_event):
        calls.append(FakeConsumer.instance.commits)
        if len(calls) == 1:
            raise RuntimeError("temporary database failure")

    run_kafka_consumer(
        [envelope.topic],
        "p09-test-workers",
        handler,
        lambda _event, _error: None,
        consumer_factory=FakeConsumer,
        processor_factory=lambda fn, dlq, raw_dlq_publisher=None: ConsumerProcessor(
            fn, dlq, max_retries=2, backoff_seconds=0,
            raw_dlq_publisher=raw_dlq_publisher,
        ),
    )

    assert calls == [0, 0]
    assert FakeConsumer.instance.commits == 1
