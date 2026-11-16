# Kafka Failure Scenarios

These are reproducible procedures for the disposable Pair 09 environment. The
commands below are prepared for user-side PowerShell execution; no new runtime
evidence is claimed by this update because Docker API access is unavailable in
the current execution context.

## Duplicate event

Publish the same serialized envelope twice with the same `event_id` and key.
Then inspect the durable inbox:

```powershell
docker compose -f docker-compose.yml -f performance/docker-compose.batch7.yml -p p09-performance-batch7 exec kafka sh -lc 'printf "%s\n%s\n" "$EVENT_JSON" "$EVENT_JSON" | /opt/kafka/bin/kafka-console-producer.sh --bootstrap-server kafka:9092 --topic p09.job.created --property parse.key=true --property key.separator=|'
docker compose -f docker-compose.yml -f performance/docker-compose.batch7.yml -p p09-performance-batch7 exec mysql sh -lc 'mysql -uroot -p"$MYSQL_ROOT_PASSWORD" handshake_lab1_local -e "SELECT event_id, COUNT(*) AS claims FROM processed_events GROUP BY event_id HAVING claims > 1;"'
```

Use a synthetic envelope and export it only in the disposable shell; never put
credentials or real records in the evidence. Expected durable result: one row
for the event ID and one duplicate outcome in worker logs.

## Worker failure and restart

Set `WORKER_CRASH_AFTER_PROCESSING_ONCE=1` only in the disposable worker
environment, start one worker, publish a synthetic event, and inspect the
consumer group before and after restarting the worker. The crash hook is already
implemented in `record_processed_event()` and is not a substitute for a real
process-crash claim unless the process actually terminates.

```powershell
docker compose -f docker-compose.yml -f performance/docker-compose.batch7.yml -p p09-performance-batch7 logs --no-color worker
docker compose -f docker-compose.yml -f performance/docker-compose.batch7.yml -p p09-performance-batch7 exec kafka /opt/kafka/bin/kafka-consumer-groups.sh --bootstrap-server kafka:9092 --group p09-careerbridge-workers --describe
docker compose -f docker-compose.yml -f performance/docker-compose.batch7.yml -p p09-performance-batch7 up -d worker
```

Verify the offset advances only after the restarted worker has a durable
processed-event row. Record the event ID, group lag, worker termination, and
database row count.

## Poison message and DLQ

Publish invalid JSON to a supported topic, inspect bounded retry logs and then
consume the matching DLQ. Publish a valid synthetic message afterward and verify
that it is processed.

```powershell
docker compose -f docker-compose.yml -f performance/docker-compose.batch7.yml -p p09-performance-batch7 exec kafka sh -lc 'printf "not-json\n" | /opt/kafka/bin/kafka-console-producer.sh --bootstrap-server kafka:9092 --topic p09.job.created'
docker compose -f docker-compose.yml -f performance/docker-compose.batch7.yml -p p09-performance-batch7 exec kafka /opt/kafka/bin/kafka-console-consumer.sh --bootstrap-server kafka:9092 --topic p09.job.created.dlq --from-beginning --max-messages 1
```

The DLQ record contains bounded original data, source topic, event type when
known, event/trace/aggregate identifiers when decodable, and the error type.

## Current verification status

- **Implemented:** typed envelope validation, manual commit, durable inbox
  primary key, bounded retries, typed/raw DLQ publishing, and correlation logs.
- **Unit-tested:** 2026-11-15 focused Kafka/outbox suite, 15 passed.
- **Runtime-verified in this update:** blocked by Docker named-pipe permission.
- **Historical disposable evidence:** see `KAFKA_EVIDENCE_BATCH2.md`; it is not
  relabeled as current execution evidence.
