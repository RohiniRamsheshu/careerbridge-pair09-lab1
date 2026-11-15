# CareerBridge performance testing

This directory contains reproducible Apache JMeter plans and result-analysis tooling for Pair 09.
The plans target a disposable CareerBridge environment only. They do not contain credentials,
tokens, seeded IDs, or fabricated result files.

## Prerequisites

- Apache JMeter 5.6+ (`jmeter --version`)
- A separately named disposable Compose project with its own MySQL/Mongo/Kafka volumes
- Synthetic student accounts in `performance/data/users.csv` (headerless rows; the JMX supplies variable names)
- A valid synthetic job ID and event ID passed as properties
- Backend URL passed as `-JbaseUrl`, defaulting to `http://127.0.0.1:9090`

The repository's retained volumes must not be used for write-producing load tests. Create the
test environment and accounts outside the retained `p09-mongo-batch3` project, then verify the
database name and volume names before loading the plan.

## Plans

`jmeter/careerbridge_crud.jmx` covers login, job search, event search, event registration, and
application submission. It uses `${users}` for the thread count; run it at 100, 200, 300, 400,
and 500 users. The application and registration samplers are disabled by default in the plan
until valid synthetic IDs are supplied and the isolated write environment is confirmed.

`jmeter/careerbridge_assistant.jmx` covers the real `/assistant/chat` endpoint with bounded,
non-writing prompts. Run it at 5, 10, 20, and 50 users. It does not substitute a mock assistant.

Example commands, after JMeter and the isolated environment are ready. Batch 7 uses
`performance/docker-compose.batch7.yml` to avoid the retained stack's host ports:

```powershell
jmeter -n -t performance/jmeter/careerbridge_crud.jmx `
  -Jhost=127.0.0.1 -Jport=19090 -Jusers=100 -Jloops=1 `
  -JusersCsv=performance/data/users.csv `
  -JjobId=123 -JeventId=456 `
  -l performance/results/crud-100.jtl -e -o performance/results/crud-100-report

jmeter -n -t performance/jmeter/careerbridge_assistant.jmx `
  -Jhost=127.0.0.1 -Jport=19090 -Jusers=5 -Jloops=1 `
  -JusersCsv=performance/data/users.csv `
  -l performance/results/assistant-5.jtl -e -o performance/results/assistant-5-report
```

Repeat with the required concurrency values. Do not overwrite a prior result directory.
Use `performance/tools/analyze_jtl.py` to produce a summary only from actual `.jtl` files:

```powershell
python performance/tools/analyze_jtl.py performance/results/crud-100.jtl `
  --output performance/results/crud-100-summary.json
```

The script reports average, p50, p95, p99, throughput, total/success/failure counts and error
rate. It does not infer database, Kafka, or model timings from HTTP latency.

## Current execution status

JMeter is not installed in the current environment, Docker is not accessible from the current
shell, and the backend is not running. Therefore no JTL, load result, graph, or live assistant
measurement is claimed by this batch. The exact remaining setup is documented in
`docs/JMETER_PERFORMANCE.md`.
