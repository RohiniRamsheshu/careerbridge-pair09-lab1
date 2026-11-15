import json

import pytest

from backend.app.events.contracts import EventEnvelope


def test_application_event_contract_contains_trace_and_payload():
    event = EventEnvelope.create(
        "application.created",
        42,
        "application",
        {"job_id": 7, "student_user_id": 9},
        trace_id="trace-42",
    )

    body = json.loads(event.to_json())
    assert body["topic"] == "p09.application.created"
    assert body["aggregate_id"] == 42
    assert body["trace_id"] == "trace-42"
    assert body["payload"]["job_id"] == 7


@pytest.mark.parametrize(
    "topic,aggregate_id,payload",
    [("unknown", 1, {}), ("job.created", 0, {}), ("job.created", 1, None)],
)
def test_event_contract_rejects_invalid_envelopes(topic, aggregate_id, payload):
    with pytest.raises(ValueError):
        EventEnvelope.create(topic, aggregate_id, "job", payload)
