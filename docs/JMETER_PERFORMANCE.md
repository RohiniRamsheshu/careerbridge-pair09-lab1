# JMeter performance testing

## Scope

Pair 09 requires CRUD concurrency at 100, 200, 300, 400, and 500 users and assistant
concurrency at 5, 10, 20, and 50 users. The plans under `performance/jmeter/` target the
actual CareerBridge routes and use external synthetic-account data.

## Current environment check

Checked on 2026-11-13:

- `jmeter --version`: unavailable; no JMeter executable is installed.
- `docker compose version`: Docker Compose v5.6.1 is installed, but Docker API access failed
  with permission denied on `npipe:////./pipe/dockerDesktopLinuxEngine`.
- `ollama --version`: 0.40.16.
- Ollama `/api/tags`: reachable; local models included `llama3.2:3b` and `nomic-embed-text`.
- No backend/Compose service was running during this check.

Batch 7 recheck: Docker Desktop processes were present, but the Docker engine still returned
permission denied on its named pipe. Java and JMeter were also absent. No restart or privilege
bypass was attempted.

No load test, `.jtl`, assistant concurrency result, or 50-request trace measurement is claimed.

## Safe execution procedure

1. Start a separately named disposable Compose project with unique MySQL, MongoDB, and Kafka
   volumes. Verify `DB_NAME`, volume names, and backend URL before creating synthetic accounts.
2. Create only synthetic users and records in that environment. Keep account data in an ignored
   local CSV based on `performance/data/users.csv.example`; never commit credentials.
3. Install Apache JMeter 5.6+ through an approved local/container method. Do not disable TLS
   verification or alter global Python/Node configuration.
4. Run `careerbridge_crud.jmx` at each CRUD concurrency level and `careerbridge_assistant.jmx`
   at each assistant level, using unique result directories.
5. Verify asynchronous application/registration records and corresponding Kafka/outbox evidence
   after each write-enabled run. HTTP 201 alone is not sufficient evidence.
6. Analyze each actual JTL with `performance/tools/analyze_jtl.py` and retain raw JTL files.

The assistant plan uses a bounded, read-only prompt. It must run only after the disposable
backend has Ollama connectivity configured. Provider/model timings and token telemetry come
from the application trace response/logs, not from JMeter's HTTP timing.

## Required result table

Populate this table only from real JTL and trace outputs:

| Scenario | Concurrency | Requests | Avg ms | p50 | p95 | p99 | Throughput | Error rate |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| CRUD login | 100/200/300/400/500 | pending | pending | pending | pending | pending | pending | pending |
| CRUD job search | 100/200/300/400/500 | pending | pending | pending | pending | pending | pending | pending |
| CRUD application | 100/200/300/400/500 | pending | pending | pending | pending | pending | pending | pending |
| CRUD event search/registration | 100/200/300/400/500 | pending | pending | pending | pending | pending | pending | pending |
| Assistant | 5/10/20/50 | pending | pending | pending | pending | pending | pending | pending |

## Batch 7 executed results

JMeter 5.6.3 ran with Temurin JDK 25.0.5 against the isolated backend at
`http://127.0.0.1:19090`. CRUD samplers exercised login, job search, and event search. The
application and event-registration samplers remained disabled during load because the plan had
one synthetic student/job/event row; one application and one registration were verified
separately with unique isolated data.

| CRUD users | Samples | Average ms | p50 | p95 | p99 | Throughput/s | Error rate |
|---:|---:|---:|---:|---:|---:|---:|---:|
| 100 | 300 | 24,792.597 | 20,994 | 62,395 | 64,924 | 3.705 | 0% |
| 200 | 600 | 38,224.918 | 32,122 | 86,624 | 95,470 | 4.938 | 0% |
| 300 | 900 | 46,309.949 | 41,428 | 102,784 | 112,773 | 6.132 | 0% |
| 400 | 1,200 | 58,736.101 | 49,322 | 129,876 | 143,585 | 6.405 | 0% |
| 500 | 1,500 | 70,869.903 | 57,881 | 156,510 | 175,791 | 6.687 | 0% |

| Assistant users | Chat samples | Average ms | p50 | p95 | p99 | Throughput/s | Error rate |
|---:|---:|---:|---:|---:|---:|---:|---:|
| 5 | 5 | 7,451.8 | 7,587 | 7,841 | 7,841 | 0.635 | 0% |
| 10 | 10 | 5,785.9 | 5,651 | 7,668 | 7,668 | 1.075 | 0% |
| 20 | 20 | 4,724.05 | 4,720 | 5,597 | 6,935 | 1.454 | 0% |
| 50 | 50 | 8,329.44 | 7,665 | 12,405 | 13,145 | 2.455 | 0% |

Raw JTLs, summaries, CSV tables and SVG graphs are under `performance/results/`.
