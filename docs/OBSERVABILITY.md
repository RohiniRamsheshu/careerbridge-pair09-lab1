# Observability and trace analysis

HTTP requests receive an `X-Trace-ID` response header and log a structured
`http_request` record. Assistant execution carries that trace ID into routing and
assistant timing logs. Existing Kafka envelopes already contain `trace_id`, and
producer/consumer logs include it for event publication and processing.

Assistant metrics distinguish routing/tool time, model time, total time, model-call
count, tool-call count, repair count, token counts, and context utilization. Kafka
queue waiting and database timings are not yet separately instrumented for every
SQL statement.

No 50-request trace analysis was fabricated in this batch. A reproducible workload
and sanitized success/failure trace still need to be run against the disposable
stack. Until then, the first bottleneck is not claimed.
