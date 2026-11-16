# CareerBridge Lab 2 Requirement Traceability

This matrix reconciles the professor's seven-page `Handshake_Lab2 (1).pdf` with the
Pair 09 implementation addendum. The PDF is authoritative. Addendum-only wording is
included where it makes the PDF requirement operationally explicit.

## Pair-specific configuration

| Parameter | Required value | Implementation location | Verification | Evidence | Status |
|---|---|---|---|---|---|
| `PAIR` | `09` | `backend/app/config.py`, deployment configuration | Unit-tested derived configuration | README and Lab 2 report | Partially verified |
| `PORT_BASE` | `9090` (`9000 + 09 * 10`) | `backend/app/config.py`, `docker-compose.yml` | Unit test and Compose config validation | README, command output | Partially verified |
| Database/Kafka prefix | `p09` | `backend/app/config.py`, `docker-compose.yml` | Configuration inspection; Kafka runtime not yet tested | README, screenshots, logs | Partially verified |
| `SEED` | `09` | `backend/app/config.py` | Unit-tested default; seed reproduction not run | README, report | Partially verified |
| `CITY_SET` | San Jose, Mountain View, Palo Alto | `backend/app/config.py` | Unit-tested default; live data not verified here | README, report, test evidence | Partially verified |

## Part 1 — Docker, Kubernetes, and AWS (11 points)

| PDF requirement / points | Implementation location | Verification procedure | Evidence location | Status |
|---|---|---|---|---|
| Six service Dockerfiles: Student, Company, Job, Application, Event, AI Assistant; required dependencies only, startup command, port, health check, `p09` naming (4) | Current `backend/Dockerfile` and `frontend/Dockerfile`; service extraction pending | Compose syntax verified; image build blocked by BuildKit startup | Build output, screenshots, README | Partially verified |
| Docker Compose runs complete stack locally (2) | `docker-compose.yml` | Disposable `p09-mongo-batch3` stack built; backend, frontend, MySQL, MongoDB, Kafka, workers healthy | Compose status and health output | Partially verified; six independent services are not present |
| Kubernetes manifests for every service: Deployments, Services, ConfigMaps, Secrets where appropriate; `p09` namespace/resource prefixes; discovery; replicas; resource requests/limits; no committed secrets (3) | `k8s/` or equivalent manifests | `kubectl apply`, inspect resources, service discovery, readiness | `kubectl` output, screenshots, sanitized manifests | Not started |
| Services communicate in cluster (1) | Service configuration and code | Run cross-service health/request checks in cluster | Logs and request evidence | Not started |
| AWS ECR/EKS deployment and evidence (1) | AWS/IaC/deployment scripts and manifests | Authenticate securely, push tagged images, deploy namespace/manifests, confirm healthy pods | ECR/EKS screenshots and commands | Not started |
| Expose frontend/API by LoadBalancer or approved Ingress; configure secrets/env safely; complete one successful deployed request | Kubernetes ingress/service configuration | Send one end-to-end request and capture request/response | Endpoint screenshot and sanitized response | Not started |
| AWS demo/viva must be restorable; resources may be paused/scaled down but not deleted; both partners must run/explain/modify selected code | README/runbook and recording | Restore deployment before scheduled demo; rehearse both partners | Recording, run log, report | Not started |

## Part 2 — Kafka asynchronous messaging (8 points)

| Requirement | Implementation location | Verification procedure | Evidence | Status |
|---|---|---|---|---|
| Kafka deployed inside Kubernetes; student-facing APIs publish and workers consume; architecture diagram in report | Kafka manifests, producers, consumers, report diagram | Inspect topics, publish events, observe consumer processing | Diagram, manifests, logs | Not started |
| `application.created` / `application.updated`: Application API → Application Worker | Application API/worker | Create/update in isolated environment and inspect event/consumer effect | Event payload, logs, DB verification | Not started |
| `application.status_changed`: Company or Application API → Notification/Application Worker | Application/company routes and worker | Change status and inspect event flow | Logs and resulting effect | Not started |
| `event.registration_created`: Event API → Event Worker | Event route/worker | Register in isolated environment and inspect event flow | Logs and verification | Not started |
| `job.created`: Job API → Search Index or Job Worker | Job route/worker | Create in isolated environment and inspect event flow | Logs and verification | Not started |
| Duplicate same-key event is idempotent and creates no duplicate effect | Consumer idempotency logic | Publish same-key event more than once | Event IDs, logs, DB check, screenshot | Not started |
| Worker failure recovers without data loss or duplicate effects; offset commits after DB write | Consumer transaction/offset logic | Stop worker during processing, restart, inspect ordering and outcome | Logs and DB verification | Not started |
| Poison message has bounded retries, reaches DLQ, and pipeline continues | Retry/DLQ handling | Publish invalid message and inspect retry count/DLQ/next message | Logs, DLQ output, screenshot | Not started |

## Part 3 — MongoDB and assistant memory (9 points)

| Requirement | Implementation location | Verification procedure | Evidence | Status |
|---|---|---|---|---|
| Migrate student accounts, profiles, preferences, sessions, companies, jobs, applications, resumes/metadata, events, registrations, saved jobs/events, activity logs (4) | `backend/app/mongo_migration.py`, `backend/app/mongo_repository.py` | Disposable migration runs with stable IDs and zero errors; missing source tables explicitly reported | `docs/MONGODB_MIGRATION.md` | Partially verified; source/fixture gaps remain |
| Preserve bcrypt hashes and expiring sessions; never store plaintext passwords | Auth/session persistence; Mongo TTL index | Disposable hash-preservation boolean passed; sessions source table absent | `docs/MONGODB_MIGRATION.md` | Partially verified |
| `assistant_rules` instruction memory: privacy/eligibility rules | `MongoRepository.rules`, prompt builder | Collection/index and injection code implemented; no rule seed/live rule transcript | `docs/ASSISTANT_MEMORY.md` | Partially verified |
| `student_memory` learned memory: ISO date/category/description entries | `MongoRepository`, `memory_consolidation.py` | 60-entry disposable experiment and authenticated `/memory` check | `docs/MEMORY_CONSOLIDATION_EVIDENCE.md` | Verified for deterministic fixture; broader live coverage partial |
| `conversations` session memory: current conversation only, compact/discard at session end | `MongoRepository.save_conversation/get_conversation`, assistant route | Code and bounded persistence implemented; leave/return and compaction not live-verified | `docs/ASSISTANT_MEMORY.md` | Partially verified |
| Inject appropriate memory into prompts and implement `/memory` command | `backend/app/main.py`, `backend/app/agent.py` | Authenticated disposable `/memory` returned scoped `preferred_city` | `docs/ASSISTANT_MEMORY.md` | Partially verified |
| Consolidation runs as Kafka consumer, not a blocking user request | `backend/app/events/worker.py`, memory topics | Disposable worker log showed `p09.memory.consolidate`; Mongo counts changed | `docs/MEMORY_CONSOLIDATION_EVIDENCE.md` | Partially verified; cross-store durability limited |
| Seed one student with ≥60 entries, ≥3 deliberate contradictions, ≥3 duplicates; record before state | `seed_synthetic_memories` | Disposable fixture seeded 60 entries and consolidated | `docs/MEMORY_CONSOLIDATION_EVIDENCE.md` | Verified for synthetic experiment |
| Consolidation leaves <40 entries; merges duplicates; resolves contradictions; explain one decision or incorrect model handling | `consolidate_student` | Disposable result 60 → 30 with 30 decisions and deterministic rule explanation | `docs/MEMORY_CONSOLIDATION_EVIDENCE.md` | Verified for deterministic experiment |

## Part 4 — Redux integration (4 points)

| Requirement | Implementation location | Verification procedure | Evidence | Status |
|---|---|---|---|---|
| Six real slices: auth/session; jobs/companies; applications; events/registrations; saved items; assistant conversation | `frontend/src/store/` or equivalent | Inspect imports and exercise each slice through real UI flows | Source and Redux DevTools | Not started |
| Actions, reducers, selectors correctly used | Redux modules/components | Dispatch and inspect state transitions/selectors | DevTools screenshots | Not started |
| DevTools evidence for at least two slices, including conversation | Redux DevTools | Capture state/action history | Screenshots in evidence | Not started |
| Leaving assistant and returning preserves conversation thread | Assistant route/store persistence | Navigate away/back and verify messages remain | Browser recording/screenshot | Not started |

## Part 5 — JMeter performance (5 points)

| Requirement | Implementation location | Verification procedure | Evidence | Status |
|---|---|---|---|---|
| Reproducible `.jmx` plans and meaningful seeded data | `performance/` or `jmeter/` | Run plans with documented variables and isolated/approved environment | `.jmx`, README, screenshots | Not started |
| Login at 100/200/300/400/500 users; average response, throughput, error rate at each | JMeter plan | Execute all five levels | Results table/graph | Not started |
| Job search at 100/200/300/400/500 users; same metrics | JMeter plan | Execute all five levels | Results table/graph | Not started |
| Application submission through Kafka at 100/200/300/400/500 users; same metrics | JMeter plan and Kafka flow | Execute only against approved isolated environment | Results, Kafka evidence | Not started |
| Event search or registration at 100/200/300/400/500 users; same metrics | JMeter plan | Execute all five levels | Results table/graph | Not started |
| Assistant endpoint at 5/10/20/50 users; p50/p95/p99/error rate | Assistant JMeter plan | Execute all four levels | Results and analysis | Not started |
| Graph average response time vs concurrency; explain queueing, inference, DB work, worker capacity, first bottleneck; compare CRUD vs assistant | `METRICS.md`/report | Analyze actual results only | Graph and narrative | Not started |

## Part 6 — Context, guardrails, observability (3 points)

| Requirement | Implementation location | Verification procedure | Evidence | Status |
|---|---|---|---|---|
| After every model call record prompt/completion tokens; display tokens/context percentage; warn above 70% | Agent/model client and assistant UI | Run model-backed turns and inspect telemetry/UI | Screenshots and logs | Not started |
| Compaction above chosen threshold summarizes preferences, jobs, companies, events, applications, current request; replaces history; exposes command; reports before/after tokens; proves recall | Conversation/memory modules | Trigger compaction and ask recall question | Transcript and token evidence | Not started |
| Trace IDs across API requests, Kafka messages, service logs; one success and one failure | Middleware, producers/consumers, logging | Trace two complete flows end to end | Sanitized logs and diagram | Not started |
| Fifty-request trace analysis identifies dominant inference, DB, tool, or queue-wait latency | Observability/analysis scripts | Collect and analyze 50 requests | `METRICS.md`/report | Not started |
| Guardrail 1: allowlist declared tools; reject unknown tools | Agent guardrail/tool dispatcher | Unknown-tool harness case | Harness output | Not started |
| Guardrail 2: typed JSON schema validation; reject malformed/extra arguments | Tool schemas/validator | Malformed and extra-argument cases | Harness output | Not started |
| Guardrail 3: authentication, role, ownership checks | Auth and tool execution | Authorized/unauthorized cases | Tests and logs | Not started |
| Guardrail 4: read-only automatic; explicit confirmation before writes | Confirmation flow | Accepted and declined write cases; exact write count | Harness/transcript | Not started |
| Guardrail 5: delimit retrieved text as untrusted; resist prompt injection | Prompt construction and validators | Injection before/after execution | Before/after transcripts | Not started |
| Guardrail 6: redact private data, passwords, tokens, API keys | Serialization/logging | Inspect responses/logs and privacy tests | Sanitized evidence | Not started |
| Guardrail 7: request timeout, hard iteration ceiling, at most one repair retry | Agent loop | Timeout, ceiling, repair cases | Harness output | Not started |
| Guardrail 8: honest no-match/error answers without invented records | Agent response handling | No-match and tool-error cases | Harness/transcripts | Not started |
| Harness uses the same production guardrail, validation, authorization, and tool-execution modules | `agent_harness` and production modules | Compare imports/execute harness | Source and one-command output | Not started |
| Harness cases: read-only success; accepted write; declined write; malformed args; unknown tool; no-match; history follow-up; injection before and after; iteration/timeout; one recovery retry | Harness test suite | Run all required cases | Machine-readable output | Not started |
| Machine-readable `agent_harness.json` or `.jsonl` includes input, messages, tools, args, results, final answer, guardrail outcome, errors, retries, counts, elapsed time | Harness output | Validate output schema | Artifact file | Not started |
| Human-readable metrics include pass/fail, before/after reliability, blocked injection, declined confirmation, repaired call, bounded stop | `METRICS.md` or report | Review generated summary | Metrics/report | Not started |
| Harness has one README command and supplements, rather than replaces, real Ollama transcripts | README, harness, transcripts | Run command and inspect real transcript set | README/transcripts | Not started |

## Submission deliverables

| Deliverable | PDF requirement | Evidence location | Status |
|---|---|---|---|
| Private pair repository, regular contributions by both partners, `lab1` and `lab2` tags | Required | Git history/tags | Not started; Git changes require later approval |
| Updated README and requirements.txt | Required | Repository root | Not started |
| Dockerfiles, Compose, Kubernetes, AWS ECR/EKS configuration | Required | Repository | Not started |
| Kafka producers/consumers, architecture diagram, failure evidence | Required | Repository/report/screenshots | Not started |
| Mongo migration, schema, memory/consolidation evidence | Required | Repository/report/logs | Not started |
| Redux implementation and DevTools screenshots | Required | Frontend/evidence | Not started |
| JMeter plans, results, screenshots, graph, analysis | Required | Performance/evidence | Not started |
| Agent guardrails, harness source/output, guardrail evidence | Required | Harness/evidence | Not started |
| `RUN_LOG.txt` and updated `METRICS.md` | Required; Lab 2 updated with failures/traces | Repository | Not started |
| `AI_USE.md` and pair verification recording | Required | Repository/submission | Not started |
| `LabPair-##_Lab2_Report.pdf` | Required; architecture, cloud, Kafka, Mongo, memory, Redux, performance, token compaction, trace, guardrail/harness evidence | Submission | Not started |
| Screenshots: AWS/ECR/EKS, endpoint, Kafka flows, Redux DevTools, safety tests | Required | Evidence folder/report | Not started |
| Real Ollama demonstration transcripts | Required; harness does not replace them | Transcript/evidence files | Not started |

## Safety and sequencing

Implementation must remain in the isolated worktree. No AWS resources, database migrations,
seed writes, live accounts, live Ollama calls, or load tests may run until an isolated
environment is explicitly approved. No commit, tag, push, merge, reset, or rebase is
authorized in the current session.

## Current implementation updates

## Execution update — 2026-11-15

| Requirement | Implementation / verification | Status |
|---|---|---|
| Resume storage uses the configured persistent path | `backend/app/main.py` now derives directories from `config.RESUME_DIR`; Compose explicitly sets `/app/backend/uploads/resumes`; focused resume tests and full suite pass | **IMPLEMENTED**; live volume mount remains **BLOCKED** by Docker API permission |
| Assistant instruction memory has approved default rules | `backend/app/mongo_repository.py` defines `DEFAULT_ASSISTANT_RULES` and opt-in idempotent `ensure_default_rules()`; isolated test verifies first seed and rerun behavior | **IMPLEMENTED**; no active database seeding performed |
| 60-entry memory fixture includes required duplicates and contradictions | `backend/tests/test_mongo_memory.py` now asserts duplicate groups and contradictory-value groups before consolidation; full suite passes 94 tests | **VERIFIED** for isolated deterministic fixture |
| Current backend regression baseline | `py -3.12 -m pytest -q` | **VERIFIED — 94 passed** |

| Area | Implementation | Verification | Status |
|---|---|---|---|
| Student boundary | `backend/app/services/student_service.py` behind existing profile routes | Full backend suite remains green | Partially verified; modular, not independently deployed |
| Application boundary | `backend/app/services/application_service.py` behind existing application routes | Full backend suite remains green, including authorization/resume tests | Partially verified; modular, not independently deployed |
| Event contract foundation | `backend/app/events/contracts.py` and `test_event_contracts.py` | Typed envelope and invalid-input tests | Partially verified; Kafka transport not connected |
| Pair 09 local container foundation | `backend/Dockerfile`, `frontend/Dockerfile`, `docker-compose.yml` | Images built; disposable Compose health checks passed | Partially verified; current monolith still supplies runtime |
| Gotham foundation | `frontend/src/index.css` tokens, typography, focus-visible states | Frontend tests/build pass | Partially verified; screen redesign remains |

## Current Kafka batch update

| Requirement | Implementation location | Verification | Evidence | Status |
|---|---|---|---|---|
| Pair-prefixed typed topics and versioned envelopes | `backend/app/events/contracts.py`, `backend/tests/test_event_contracts.py` | Contract tests validate prefix, IDs, payloads and serialization | Test output | Partially verified |
| Producers connected after successful application/job/event commits | `backend/app/main.py`, `backend/app/routes/applications.py`, `backend/app/events/producer.py` | Route tests plus mocked producer tests; broker run still pending | Source and test output | Partially verified |
| Manual-commit consumer, validation, bounded retries and DLQ routing primitive | `backend/app/events/consumer.py`, `backend/app/events/producer.py`, `backend/tests/test_kafka_pipeline.py` | Mocked duplicate/poison/malformed tests | Test output | Partially verified |
| Transactional MySQL outbox and bounded publisher | `backend/schema.sql`, `backend/app/events/outbox.py`, `docker-compose.yml` | Fresh isolated DB; delivered rows and broker records inspected | `docs/KAFKA_EVIDENCE_BATCH2.md` | Partially verified; no shared-DB migration |
| Durable idempotency and manual offset ordering | `processed_events`, `backend/app/events/consumer.py`, `backend/app/events/worker.py` | Duplicate and crash/restart tests against fresh broker | `docs/KAFKA_EVIDENCE_BATCH2.md` | Verified for the demonstrated worker effect |
| Local KRaft broker, topic initialization and health checks | `docker-compose.yml` | Fresh project startup and topic listing | `docs/KAFKA_EVIDENCE_BATCH2.md` | Verified |
| Three professor-required real Kafka failure demonstrations | `backend/app/events/worker.py`, `docs/KAFKA_ARCHITECTURE.md` | Duplicate, controlled crash/restart and poison/DLQ scenarios | `docs/KAFKA_EVIDENCE_BATCH2.md` | Verified in disposable environment |

## Current MongoDB and assistant-memory batch update (2026-11-13)

| Requirement | Implementation | Actual verification | Status |
|---|---|---|---|
| Mongo migration mapping and repeatable stable IDs | `backend/app/mongo_migration.py`, `backend/app/mongo_repository.py` | Two runs against disposable `p09-mongo-batch3`; identical counts and zero errors | Partially verified; source tables for sessions/activity logs absent |
| Required Mongo domains | Migration table map and resume metadata derivation | Synthetic users/profiles/company/jobs/events migrated; sanitized collection counts checked | Partially verified; applications, registrations, saved items, sessions, activity logs need source fixtures/tables |
| Bcrypt preservation and session expiry | Opaque hash conversion; `sessions.expires_at` TTL index | Hash-preservation boolean passed; no session source exists in Lab 1 schema | Partially verified |
| `assistant_rules`, `student_memory`, `conversations` | `MongoRepository.ensure_indexes`, memory and conversation methods | Indexes created in disposable Mongo; `/memory` authenticated route returned scoped memory | Partially verified; rule seeding and full conversation round-trip still outstanding |
| Memory prompt injection and student isolation | `agent.py` scoped `<memory_context>`; `main.py` authenticated scope | Scoped `/memory` live check and isolated unit test passed | Partially verified; live malicious-content test outstanding |
| 60-entry duplicate/contradiction experiment | `memory_consolidation.py` | Disposable run: 60 before, 30 active after, 30 decisions | Verified for deterministic experiment |
| Asynchronous Kafka consolidation | `memory.updated`/`memory.consolidate` contracts and `worker.py` | Real worker log showed `p09.memory.consolidate`; Mongo active/inactive counts checked | Partially verified; Mongo/Kafka cross-store outbox durability not implemented |

Evidence: `docs/MONGODB_MIGRATION.md`, `docs/ASSISTANT_MEMORY.md`, and
`docs/MEMORY_CONSOLIDATION_EVIDENCE.md`. These documents distinguish implementation,
unit testing, disposable integration testing, and remaining source/evidence gaps.

## Redux integration update (2026-11-13)

| Requirement | Implementation | Actual verification | Status |
|---|---|---|---|
| Six real Redux Toolkit slices | `frontend/src/store/slices.js`, `store/index.js` | Store and reducer tests cover auth, jobs, applications, events, saved, assistant | Partially verified; live DevTools evidence outstanding |
| Provider and real page integration | `frontend/src/main.jsx`, App, Jobs, Events, Saved, Assistant pages | Frontend suite and production build pass; pages dispatch real API thunks | Partially verified; browser workflow capture outstanding |
| Actions, reducers, selectors, async loading/error | `frontend/src/store/slices.js` | 6 reducer/selector tests plus existing frontend tests | Verified by automated tests |
| Assistant navigation persistence | Provider above router; assistant slice | Store state persists during route navigation by architecture; no browser capture yet | Partially verified |
| Redux DevTools screenshots for assistant and second slice | DevTools enabled in development | Reproducible capture steps documented | Not yet evidenced |

## Context, guardrail, and observability closeout update (2026-11-13)

| Requirement | Implementation | Actual verification | Status |
|---|---|---|---|
| Token accounting and context warning | `backend/app/ai_model.py`, `backend/app/context_management.py`, assistant API/UI | Provider metadata support plus estimate flag; synthetic API greeting returned metrics and zero model calls | Partially verified; real Ollama counts outstanding |
| Context compaction and recall | `context_management.py`, Mongo conversation persistence | Unit-tested reduction and recent-message preservation | Partially verified; live model recall transcript outstanding |
| Trace IDs through HTTP/assistant/Kafka | HTTP middleware, assistant metrics, existing event envelopes | Synthetic API returned caller trace ID; Kafka envelope carries trace IDs | Partially verified; 50-request analysis outstanding |
| Eight production guardrails | `agent.py`, `confirmation.py`, auth/resume routes | Harness imports production modules; 10/10 synthetic cases passed | Partially verified; real Ollama injection evidence outstanding |
| Machine-readable harness and metrics | `backend/agent_harness.py`, `agent_harness.json`, `METRICS.md` | `python -m backend.agent_harness`: 10 passed, 0 failed | Partially verified; harness supplements real Ollama transcripts |

## Performance and observability update (2026-11-13)

| Requirement | Implementation | Actual verification | Status |
|---|---|---|---|
| Reproducible JMeter CRUD and assistant plans | `performance/jmeter/careerbridge_crud.jmx`, `careerbridge_assistant.jmx`, `performance/README.md` | XML parsed successfully; JMeter unavailable, no live run | Partially implemented; not executed |
| CRUD levels 100/200/300/400/500 | JMeter CRUD plan accepts `-Jusers` and bounded duration | No JTL results | Not verified |
| Assistant levels 5/10/20/50 with p50/p95/p99 | JMeter assistant plan accepts `-Jusers`; analyzer reports percentiles from actual JTL | No JTL results; no backend running | Not verified |
| 50-request trace analysis | `docs/TRACE_ANALYSIS.md`, existing trace instrumentation | No 50-request workload executed | Not verified |
| Real Ollama transcript and token evidence | `docs/OLLAMA_EVIDENCE.md`, existing assistant telemetry | Ollama reachable, CareerBridge backend not running | Not verified |
## Performance Batch 7 verification (2026-11-13)

| Requirement | Evidence | Status |
|---|---|---|
| JMeter CRUD levels 100/200/300/400/500 | `performance/results/crud-*-summary.json`, raw JTLs, `crud-summary.csv` | Partially verified: login/job/event read workload executed; write samplers disabled |
| Assistant levels 5/10/20/50 with p50/p95/p99 | `performance/results/assistant-*-summary.json`, raw JTLs, `assistant-summary.csv` | Verified for deterministic assistant prompt; Ollama inference separate |
| Average latency graphs | `crud-average-vs-concurrency.svg`, `assistant-average-vs-concurrency.svg` | Verified from actual JTL summaries |
| 50 traceable requests | `trace-50-sanitized.json`, `trace-50-summary.json`, `docs/TRACE_ANALYSIS.md` | Partially verified: 50 traces/tool timings; DB/Kafka component timings unavailable |
| Real Ollama transcript and token accounting | `ollama-transcript-sanitized.json`, `docs/OLLAMA_EVIDENCE.md` | Verified invocation; correctness failed for unsupported generic offer |
| Application/event write persistence and Kafka publication | isolated API checks and outbox-worker logs | Partially verified: one application and one registration; not load-tested |

### Batch 8 assistant correctness update

| Requirement | Evidence | Status |
|---|---|---|
| Factual assistant responses grounded in tool results | `backend/app/agent.py`, `backend/tests/test_agent_part_bc.py`, live `ollama-batch8-sanitized.json` | Partially verified: unsupported offer claim blocked in live isolated request; broader model correctness still requires more scenarios |
| Real Ollama latency/token evidence after fix | `performance/results/ollama-batch8-sanitized.json`, `docs/OLLAMA_EVIDENCE.md` | Verified for one isolated request; approximately 74.3 seconds and two model calls |
| Browser workflow and Redux DevTools screenshots | `docs/SUBMISSION_EVIDENCE_CHECKLIST.md` | Not verified: browser automation unavailable |

## Batch 10 local acceptance

| Requirement | Evidence | Status |
|---|---|---|
| Synthetic student/company end-to-end workflow | `performance/tools/local_acceptance.py`, `docs/LOCAL_ACCEPTANCE_REPORT.md` | Partially verified: authentication, owned job/event creation, application, registration, applicant/registrant reads and status update passed |
| Gotham shared design system | `frontend/src/index.css`, `frontend/src/App.css`, `docs/GOTHAM_DESIGN_SYSTEM.md` | Implemented and build-verified; browser screenshots outstanding |
| Mongo memory runtime in primary environment | local acceptance `/memory` result and isolated Mongo connectivity check | Failed in `p09-performance-batch7`: backend cannot select the `mongo` server; requires environment remediation |

## Batch 11 recovery and browser status

| Requirement | Evidence | Status |
|---|---|---|
| Mongo service reachability and `/memory` | `docs/MONGO_RECOVERY_REPORT.md`, read-only backend ping, authenticated `/memory` calls | Verified after removing the conflicting Batch 7 host-port binding and preserving its named volume |
| Student memory ownership isolation | `docs/MONGO_RECOVERY_REPORT.md` | Verified: second synthetic student did not see the first student's marker |
| Memory Kafka integration | sanitized worker logs and `docs/MONGO_RECOVERY_REPORT.md` | Partially verified: memory consolidation topic subscription and synthetic publication observed |
| Browser workflows and screenshots | `docs/BROWSER_ACCEPTANCE.md`, `docs/MANUAL_BROWSER_EVIDENCE_GUIDE.md` | Blocked: browser automation initialization unavailable; manual evidence required |

## Kafka implementation pass (2026-11-15)

| Requirement | Implementation | Verification | Status |
|---|---|---|---|
| Typed/versioned envelopes and required Pair 09 topics | `backend/app/events/contracts.py` | Focused Kafka tests | Unit-tested |
| Producer acknowledgement and transactional outbox worker | `backend/app/events/producer.py`, `backend/app/events/outbox.py` | Existing disposable evidence; no new runtime run | Implemented; runtime not re-run |
| Manual offsets after terminal processing | `backend/app/events/consumer.py` | Fake broker test proves commit follows handler success; retry test proves no early commit | Unit-tested |
| Durable duplicate handling | `processed_events` primary key and `record_processed_event()` | First/replay and restart-safe claim tests | Unit-tested; runtime not re-run |
| Bounded retries and DLQ metadata | `consumer.py`, `producer.py` | Retry/DLQ and raw-correlation tests | Unit-tested; runtime not re-run |
| Event observability | producer/consumer/worker structured logs | Code review and test suite | Implemented; runtime log capture pending |
| Three professor failure demonstrations | `docs/KAFKA_FAILURE_SCENARIOS.md`, historical `docs/KAFKA_EVIDENCE_BATCH2.md` | Docker unavailable in this pass | Historical evidence exists; current runtime re-verification blocked |

## Submission-preparation verification (2026-11-15)

| Requirement | Current evidence | Status |
|---|---|---|
| Professor rubric source | `C:\Users\Bhushan Waingankar\Downloads\Handshake_Lab2 (1).pdf` | Verified: 7 pages, 40 points |
| Backend regression | `RUN_LOG.txt` and `docs/LAB2_EXECUTION_LOG.md` | Verified: 102 passed, 1 warning |
| Frontend regression/build | `RUN_LOG.txt` | Verified: 24 passed; build passed |
| Frontend lint | `RUN_LOG.txt` | Verified: exit 0; three known warnings |
| Deterministic harness | `agent_harness.json`, `RUN_LOG.txt` | Verified: 10 passed, 0 failed |
| Current Compose/Kafka/Mongo runtime | `docs/evidence/00_overview/STATUS.md` | Blocked by Docker named-pipe permission |
| Browser and Redux DevTools evidence | `docs/BROWSER_ACCEPTANCE.md`, manual guide | Missing; manual screenshots required |
| Kubernetes and AWS | `docs/LAB2_SUBMISSION_READINESS.md` | Missing/deferred; no resources created |
| Final report readiness | `docs/LAB2_SUBMISSION_READINESS.md` | Not ready; gaps remain |

## Service and Kubernetes preparation update (2026-11-15)

| Requirement | Implementation/evidence | Status |
|---|---|---|
| Six logical service build targets | `backend/Dockerfile.student`, `.company`, `.job`, `.application`, `.event`, `.assistant`; `backend/app/service_entrypoint.py` | Implemented and unit-tested; runtime build not verified |
| Six Compose domain processes | `docker-compose.yml` services `student-service`, `company-service`, `job-service`, `application-service`, `event-service`, `assistant-service` | Implemented; current Docker runtime verification blocked |
| Compatibility API and workers in Kubernetes | `k8s/api-and-workers.yaml` | Implemented as preparation; not cluster-verified |
| Kubernetes infrastructure and persistence | `k8s/infrastructure.yaml`, `k8s/storage-and-ingress.yaml`, `k8s/configmap.yaml`, `k8s/secret.example.yaml` | Prepared and YAML-parsed; not applied |
| ECR/EKS preparation | `scripts/build-p09-images.ps1`, `scripts/deploy-p09-eks.ps1`, `k8s/README.md` | Prepared only; no AWS resources or cloud evidence |

The six processes are route-boundary deployments over the existing modular
FastAPI implementation. The repository does not claim six independently-owned
domain databases or a completed microservice extraction.
