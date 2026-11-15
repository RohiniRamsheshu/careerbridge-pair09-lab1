# 50-request trace analysis

The repository already propagates `X-Trace-ID` through HTTP and assistant metrics, and Kafka
envelopes carry trace IDs. A 50-request analysis has not been run in this batch because the
backend and disposable performance environment are unavailable.

For each real request, retain the sanitized trace ID, start/end time, model duration, database
duration, tool duration, queue/Kafka wait, total duration, outcome, and token-count source
(provider-reported or estimated). Do not infer component timings from total HTTP latency.

Required outputs are an aggregate percentile summary, slowest and failed requests, one success
trace, one failure trace, and evidence-based bottleneck analysis. No synthetic values should be
inserted to fill the report.

## Batch 7 result

`performance/results/trace-50-sanitized.json` contains 50 real assistant response records from
the isolated backend. All 50 returned HTTP success:

- Average HTTP duration: 10,704.68 ms
- p50: 7,758 ms; p95: 22,338 ms; p99: 26,913 ms
- Model calls: 0; tool calls: 50
- Token records: 50 estimated, 0 provider-reported
- Trace IDs: present per record
- Database and Kafka queue timing: unavailable in the current API telemetry

The deterministic workload is valid trace evidence but does not measure Ollama inference. The
separate real Ollama transcript is `performance/results/ollama-transcript-sanitized.json` and
documents a failed accuracy case.

Batch 8 added a separate sanitized real request with trace ID `159a9d01-621c-4f02-8028-bc72ca0f93ac`.
The request demonstrated the post-fix honest response. It is not included in the 50-request deterministic
aggregate because it used two real Ollama calls and has a different workload profile.

