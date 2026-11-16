import json

from backend.app.events.contracts import EventEnvelope
from backend.app.events.outbox import enqueue_event, record_processed_event


class FakeCursor:
    def __init__(self, rowcount=1):
        self.rowcount = rowcount
        self.calls = []

    def execute(self, sql, params=()):
        self.calls.append((sql, params))

    def close(self):
        pass


class FakeConnection:
    def __init__(self, rowcount=1):
        self.cursor_obj = FakeCursor(rowcount)
        self.commits = 0
        self.rollbacks = 0

    def cursor(self, **_kwargs):
        return self.cursor_obj

    def commit(self):
        self.commits += 1

    def rollback(self):
        self.rollbacks += 1

    def close(self):
        pass


def test_enqueue_event_serializes_typed_payload_for_same_transaction():
    cursor = FakeCursor()
    envelope = EventEnvelope.create("job.created", 7, "job", {"title": "Data"})

    enqueue_event(cursor, envelope)

    sql, params = cursor.calls[0]
    assert "event_outbox" in sql
    assert params[0] == envelope.event_id
    assert params[1] == "p09.job.created"
    assert json.loads(params[4]) == {"title": "Data"}


def test_processed_event_claim_is_durable_and_duplicate_safe():
    first = FakeConnection(rowcount=1)
    second = FakeConnection(rowcount=0)
    envelope = EventEnvelope.create("application.created", 3, "application", {})

    assert record_processed_event(envelope, lambda: first) is True
    assert record_processed_event(envelope, lambda: second) is False
    assert first.commits == 1
    assert second.commits == 1


def test_processed_event_claim_survives_worker_restart():
    envelope = EventEnvelope.create("job.created", 11, "job", {"title": "Restart safe"})
    connections = iter([FakeConnection(rowcount=1), FakeConnection(rowcount=0)])
    handler_calls = []

    def claim():
        return record_processed_event(envelope, lambda: next(connections))

    if claim():
        handler_calls.append(envelope.event_id)
    # A fresh worker instance sees the durable unique event_id claim and skips it.
    if claim():
        handler_calls.append(envelope.event_id)

    assert handler_calls == [envelope.event_id]
