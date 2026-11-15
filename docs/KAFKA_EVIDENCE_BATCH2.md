# Kafka Batch 2 evidence

Date: 2026-11-13. Environment: fresh Compose project `p09-kafka-batch2`, new MySQL and Kafka volumes, no shared database access.

## Runtime

Verified with `docker compose -p p09-kafka-batch2 up --build -d` and `docker compose -p p09-kafka-batch2 ps`. Kafka, the API, the frontend, the consumer worker, and the outbox worker were separate containers. Kafka initialized the five required topics and five `.dlq` topics. Backend `/health` and `/health/database` passed; frontend returned HTTP 200.

## End-to-end application workflows

Using disposable accounts created through the real HTTP API:

| Workflow | API result | Outbox result | Consumer result |
|---|---:|---|---|
| Job creation | 201, job ID 3 | `p09.job.created`, delivered, attempts 1 | One processed event |
| Event registration | 201, registration ID 1 | `p09.event.registration_created`, delivered, attempts 1 | One processed event |
| Application submission | 201, application ID 4 | `p09.application.created`, delivered, attempts 1 | One processed event |
| Application status update | 200 | `p09.application.updated` and `p09.application.status_changed`, delivered, attempts 1 | One processed event for each |

The database query showed five delivered outbox rows and five corresponding processed-event rows. Event payloads contained expected aggregate IDs and trace IDs. HTTP response shapes remained the existing Lab 1 shapes.

## Failure demonstrations

### Duplicate event

The same valid envelope ID `demo-duplicate-0001` was published twice to `p09.job.created`. The durable `processed_events` query returned exactly one row for that event ID.

### Worker crash and restart

The normal worker was stopped. A one-shot worker with `WORKER_CRASH_AFTER_PROCESSING_ONCE=1` consumed `demo-crash-0001`, committed its processed-event transaction, and terminated before Kafka offset commit. Before restart, the consumer-group description showed `p09.job.created` at current offset 3 with log end 4 and lag 1, with no active members. After restart, the event remained exactly one processed-event row and the group advanced to current offset 4 with lag 0.

This is at-least-once delivery with durable idempotency, not exactly-once delivery.

### Poison message and DLQ

The raw message `not-json` was published to `p09.job.created`. The worker retried it three times and published this DLQ record to `p09.job.created.dlq`:

```json
{"error_type":"JSONDecodeError","original_raw":"not-json","source_topic":"p09.job.created"}
```

A valid event `demo-after-poison-0001` published afterward was processed successfully with exactly one durable processed-event row.

## Limitations

- The outbox publisher is bounded and auditable but does not claim exactly-once delivery.
- Domain-specific consumer side effects currently use `processed_events` as the durable idempotent effect; additional domain handlers can be added in the same transaction.
- The retained `p09-careerbridge` volume was not repaired or reused.
