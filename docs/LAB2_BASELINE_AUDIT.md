# Lab 2 Baseline Audit

Date: 2026-11-12
Branch: `feature/gotham-premium-redesign`
Baseline commit: `2a5dd788f4f83029e6202d8e893455f77aeeae01`

## Baseline commands and actual results

### Backend

Command:

```powershell
pytest -q
```

Initial result: **blocked during collection**.

- `ModuleNotFoundError: No module named 'backend'` occurred for tests importing the package from the repository root.
- `ModuleNotFoundError: No module named 'bcrypt'` occurred while importing `backend.app.main`.
- No backend test assertions ran.
- Pytest also reported permission warnings for existing cache directories; no project files were changed.

The declared dependencies are in `backend/requirements.txt`; the current Python environment does not have all of them available. A minimal attempt to install the declared `bcrypt` package failed because the environment could not validate the PyPI certificate. No repository or database changes resulted.

An elevated rerun with `PYTHONPATH=.` removed the repository import-path error, but backend collection still stopped at the missing `bcrypt` import. Backend assertions therefore remained unverified in Python 3.10.

The repository-compatible Python 3.12 runtime was then verified:

```powershell
$env:PYTHONPATH='.'
& 'C:\Users\Bhushan Waingankar\AppData\Local\Python\pythoncore-3.12-64\python.exe' -m pytest -q
```

Result: **65 passed in 4.89s**.

This is the current verified backend baseline. The test run completed without database writes.

### Frontend

Commands:

```powershell
npm test -- --run
npm run build
```

Initial restricted-sandbox runs were blocked before execution by the existing Windows Vite `spawn EPERM` failure while loading `frontend/vite.config.js`. An elevated local rerun completed successfully:

- Vitest: 3 test files, 15 tests passed.
- Production build: passed; Vite transformed 35 modules and produced `frontend/dist`.

The generated `frontend/dist` directory is ignored and was not added to the worktree.

Frontend lint also completed with one existing `react(set-state-in-effect)` warning in `frontend/src/pages/CompanyPage.jsx`.

## Available local tools

Detected executable availability:

- Docker: installed, daemon readiness not established.
- `kubectl`: installed.
- AWS CLI: installed; identity was not exposed or confirmed in the audit.
- Ollama: installed; model/server readiness was not verified.
- `mongosh`: installed.
- Node/npm: installed.
- JMeter: not installed.
- Helm: not installed.

## Python environment decision

The PATH-default interpreter is Python 3.10.2 at
`C:\Users\Bhushan Waingankar\AppData\Local\Programs\Python\Python310\python.exe`.
It lacks `bcrypt` and `mysql-connector-python`, so it is not suitable for this repository.

The verified repository-compatible interpreter is Python 3.12.10 at
`C:\Users\Bhushan Waingankar\AppData\Local\Python\pythoncore-3.12-64\python.exe`.
It has the required runtime packages installed, including:

- `bcrypt 5.0.0`
- `mysql-connector-python 26.10.0`
- `fastapi 0.143.3`
- `pytest 9.1.1`
- `httpx 0.28.1`
- `pydantic 2.14.1`
- `python-jose 3.5.0`

The authentication implementation uses the standard `bcrypt.hashpw`, `bcrypt.gensalt`,
and `bcrypt.checkpw` APIs. A direct hash/check compatibility probe succeeded under
`bcrypt 5.0.0`. No version pin or application-code change was necessary.

No repository virtual environment, lock file, or local bcrypt wheel cache was found.
The failed Python 3.10 installation attempt was not retried with insecure SSL options,
and global Python configuration was not changed.

No cloud operation, database write, migration, seed, Ollama call, or service restart was performed.

## Stage 1B progress

Implemented locally:

- Pair 09 derived settings in `backend/app/config.py`.
- Backend and frontend container definitions with health checks.
- Disposable local `docker-compose.yml` with MySQL readiness, backend dependency ordering,
  frontend dependency ordering, and Pair 09 naming/environment values.
- A unit test covering the Pair 09 derived settings.

Verified:

- Backend: 70 passed in 2.47s after the Application boundary and event-contract tests.
- Frontend: 15 passed across 3 test files.
- Frontend production build: passed.
- `docker compose config --quiet`: valid.
- Docker daemon: available (`29.9.2`).

Docker build diagnosis and verification:

- BuildKit stalled while booting/pulling its builder image.
- The legacy builder fallback (`DOCKER_BUILDKIT=0`) successfully built both images:
  `p09-careerbridge-backend:latest` and `p09-careerbridge-frontend:latest`.
- The frontend image ran its production Vite build successfully during the image build.

Compose runtime verification:

- Started with temporary local-only values and the explicitly disposable
  `handshake_lab1_local` database.
- MySQL became healthy.
- Backend became healthy.
- Frontend became healthy and returned HTTP 200 on port 5173.
- `GET /health` returned `{"status":"ok"}`.
- `GET /health/database` returned `{"status":"ok","database":"connected"}`.
- No schema load, seed, account creation, or application record write was performed.

Not implemented yet:

- Six independently runnable service containers. Student and Application are currently
  compatibility-preserving in-process boundaries; they are not yet independent services.
- Kafka transport/producers/consumers, MongoDB migration/memory, Redux, JMeter, Kubernetes,
  AWS deployment, and harness implementation.

Additional Stage 1C implementation:

- `backend/app/services/application_service.py` now owns the student application list,
  company applicant list, applicant profile, resume lookup, and status-update queries.
- Existing `/applications` routes remain the compatibility adapters with the same methods,
  authorization and response shapes.
- `backend/app/events/contracts.py` defines validated Pair 09-neutral event envelopes for
  the five required Kafka topics, including event ID, trace ID, aggregate ID, payload,
  timestamp, and schema version. It performs no transport I/O yet.
- Frontend global tokens and focus-visible styles were added in `frontend/src/index.css`.

These remain separate milestones because the baseline contains no existing service
entrypoints or event/data-layer abstractions; implementing them as dummy copies would not
meet the rubric or preserveable architecture requirements.

## Current architecture

### Backend

The current Lab 1 backend is a single FastAPI application at:

```text
backend.app.main:app
```

It currently owns authentication, profiles, jobs, applications, events, registrations,
saving, dashboards, company management, resume access, and the assistant route. Database
access is centralized through `backend.app.database.get_connection()` and currently uses
MySQL configuration from environment variables with a default `handshake_lab1` database.

The assistant is a hand-built loop in `backend/app/agent.py`, with the five existing tools:

1. `get_student_preferences`
2. `search_jobs`
3. `get_job_details`
4. `search_events`
5. `save_job_or_event`

Ollama is accessed by `backend/app/ai_model.py`. The current client defaults to
`http://localhost:11434`, model `llama3.2:3b`, and a 120-second request timeout.

### Frontend

The current frontend is a Vite/React application. API calls are centralized in
`frontend/src/services/api.js`, using `VITE_API_URL` with a fallback of
`http://localhost:9090`. Routing and role protection are in `frontend/src/App.jsx`.
The current frontend has no Redux store or Redux slices; state is component-local.

### Lab 2 capability gaps confirmed by inspection

- No Dockerfiles or Docker Compose configuration were present at the baseline root.
- No Kubernetes manifests were present.
- No Kafka producer/consumer implementation was present.
- No MongoDB repositories or migration implementation were present.
- No Redux dependencies/store/slices were present.
- No JMeter plans were present, and JMeter is not installed.
- No Lab 2 agent harness output or implementation was present.
- Existing Lab 1 tests are present, but the current environment prevented collection.

## Dependency risks

The Lab 2 rubric requires six service Dockerfiles and distributed service communication,
while the current codebase has one monolithic FastAPI backend. Splitting it into Student,
Company, Job, Application, Event, and Assistant services is an architectural change. The
safe migration path is to preserve the existing HTTP routes first, extract bounded service
modules behind compatible adapters, then add event publication/consumption and deployment
manifests. Existing Lab 1 API contracts must remain the compatibility boundary.

MongoDB migration, Kafka writes, live JMeter load, and AWS deployment require separately
isolated environments. They must not use the existing `handshake_lab1` database or create
cloud resources without explicit approval.

## Recommended implementation order

1. Restore reproducible local test execution without changing application behavior.
2. Add Pair 09 configuration and local container health checks.
3. Extract compatibility-preserving service modules and add contract/regression tests.
4. Add Kafka contracts, idempotent consumers, retry/DLQ behavior, and isolated fixtures.

## Kafka batch status (2026-11-13)

The current worktree now contains Pair 09 topic derivation, typed envelopes, a lazy Kafka producer, transactional outbox hooks for application/job/event writes, and a manual-commit consumer processor with bounded retry and topic-specific DLQ publication. Deterministic tests cover serialization, routing, malformed envelopes, duplicate suppression, poison retries, outbox enqueue and durable processed-event claims. The full backend suite is 80 passing when run with the approved interpreter and normal host temp permissions.

The implementation remains at-least-once rather than exactly-once, and domain-specific downstream side effects beyond durable event processing are limited. These limitations remain explicit.

Kafka-enabled Compose verification in this batch: the backend image built with
`kafka-python-ng==2.2.3`; Kafka reached healthy; `kafka-init` created all five required topics
and five `.dlq` topics; backend `/health` and frontend HTTP 200 passed. The disposable MySQL
health endpoint returned 503 because the retained local volume's `careerbridge` credentials do
not match the newly supplied shell values. No repair or volume deletion was performed. The
The original retained volume was not used for this run. The fresh batch-2 project remains available
for inspection and should be stopped with its project name when no longer needed.

Performance-batch environment check (2026-11-13): JMeter remained unavailable; Docker Compose
was installed but the Docker API returned permission denied; Ollama 0.40.16 was installed and
its local tag endpoint was reachable. No load test or CareerBridge Ollama call was executed.
5. Add isolated Mongo migration and memory/consolidation implementation.
6. Add Redux slices while preserving current UI flows.
7. Add the deterministic harness and evidence generation.
8. Add Docker Compose and Kubernetes manifests around verified services.
9. Prepare, but do not execute, ECR/EKS deployment scripts until cloud approval.
10. Apply the Gotham visual system incrementally after functional boundaries remain green.

## MongoDB and assistant-memory batch status (2026-11-13)

Implemented locally: Mongo configuration, lazy repository, collection/index definitions,
repeatable MySQL-to-Mongo mapping, JSON-safe date/time/decimal conversion, scoped
conversation and `/memory` support, deterministic consolidation, and Kafka memory event
hooks. The fresh disposable Compose stack built successfully and all services reached
healthy status. Migration was run twice against synthetic records with zero errors and
identical counts. A 60-entry synthetic memory fixture reduced to 30 active entries.

Not complete: the Lab 1 schema has no sessions or activity_logs tables, the migration has
not demonstrated applications/registrations/saved-items/resume records, and the Mongo
memory-to-Kafka publication is not a transactional cross-store outbox. See the dedicated
Mongo documents and traceability matrix for exact evidence and limitations.

## Batch 7 performance verification

The isolated `p09-performance-batch7` environment was built with separate volumes and reached
healthy status for MySQL, MongoDB, Kafka, backend, frontend, worker and outbox-worker. Backend
and database health returned HTTP 200 and frontend returned HTTP 200. Real JMeter 5.6.3 runs
completed the required CRUD and assistant concurrency levels; exact evidence is in
`performance/results/` and the performance documents. The CRUD load used read/login samplers;
application and registration writes were verified once separately, not repeated as load writes.
The real Ollama fallback transcript exposed an unsupported generic offer and remains an open
agent correctness defect.

## Batch 10 local acceptance

The primary disposable environment remained healthy after the Gotham frontend rebuild. A synthetic local acceptance runner verified student/company authentication, job and event creation, application submission, event registration, applicant and registrant reads, and company status update. The selected runtime's `/memory` command reported unavailable because the backend could not select its `mongo` service; this is recorded as a runtime gap rather than a passing memory check. Browser and Redux DevTools evidence were not captured because browser automation was unavailable.

## Batch 11 correction

The Batch 7 Mongo container was found detached from its Compose network and also published the host port already owned by Batch 3. The override now removes only Batch 7's host publication; the service was recreated with the existing Batch 7 named volume. Backend-side Mongo ping, `/memory`, ownership isolation and a synthetic memory Kafka publication were then verified. Browser evidence remains blocked by unavailable automation.
