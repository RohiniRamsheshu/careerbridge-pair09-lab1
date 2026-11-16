# DATA 260 Lab 2 Execution Log

## 2026-11-15 — Task 1 and Task 2 checkpoint

Worktree: `C:\Users\Bhushan Waingankar\Desktop\handshake-lab1-codex`
Branch: `fix/student-resume-upload-art-deco`
HEAD before/after this checkpoint: `4fc0638`
Runtime data: unchanged; no Docker service was recreated.

### Access and inspection

- Confirmed repository path, branch, status, and HEAD.
- Read `docs/LAB2_PHASE0_BASELINE.md`.
- Read the full 7-page professor rubric PDF at
  `C:\Users\Bhushan Waingankar\Downloads\Handshake_Lab2 (1).pdf`.
- Inspected `docker-compose.yml`, `performance/docker-compose.batch7.yml`,
  `backend/Dockerfile`, `backend/app/config.py`, `backend/app/main.py`, and
  `backend/app/routes/applications.py`.
- Inspected `backend/app/mongo_repository.py`,
  `backend/app/mongo_migration.py`, `backend/app/memory_consolidation.py`, and
  the existing Mongo tests.
- Docker API access remains blocked by the Windows named pipe permission:
  `npipe:////./pipe/dockerDesktopLinuxEngine`.

### Implemented changes

1. Resume storage configuration now has one source of truth:
   - `backend/app/main.py` derives upload/profile directories from
     `config.RESUME_DIR` instead of a second hardcoded resume path.
   - `docker-compose.yml` explicitly sets
     `RESUME_DIR=/app/backend/uploads/resumes` for the API container.
   - The existing `p09-resume-data:/app/backend/uploads/resumes` volume mapping
     remains unchanged and was not recreated or inspected through Docker due to
     the access blocker.
2. Mongo assistant rules now have an explicit, opt-in, idempotent initializer:
   - `DEFAULT_ASSISTANT_RULES` defines privacy, eligibility, and confirmation
     rules.
   - `MongoRepository.ensure_default_rules()` upserts only approved rule keys.
   - It is not called during request handling or repository construction, so no
     active database records were inserted during this task.
3. The synthetic memory test now explicitly verifies at least three duplicate
   groups and at least three contradictory groups before consolidation.
4. Added an isolated idempotency test for default assistant-rule initialization.

### Tests and checks

- Focused backend tests:
  `py -3.12 -m pytest -q backend/tests/test_config.py backend/tests/test_read_routes.py backend/tests/test_mongo_memory.py`
  — **32 passed**.
- Full backend suite:
  `py -3.12 -m pytest -q` — **94 passed**.
- Python compilation:
  `py -3.12 -m compileall -q backend` — **passed**.

### Not performed / blocked

- No Docker compose inspection, targeted backend recreation, upload persistence
  test, or live `/memory` request was performed because Docker API access is
  unavailable in this execution context.
- No Mongo records, assistant rules, memory entries, sessions, or migration
  data were inserted or changed.
- Browser screenshots were not captured.

### Exact user-side runtime verification commands

Run from PowerShell after configuring the existing local secret variables, without
using `down`, `down -v`, volume deletion, reseeding, or Batch 3:

```powershell
docker context show
docker compose -f docker-compose.yml -f performance/docker-compose.batch7.yml -p p09-performance-batch7 config --quiet
docker compose -f docker-compose.yml -f performance/docker-compose.batch7.yml -p p09-performance-batch7 ps
docker compose -f docker-compose.yml -f performance/docker-compose.batch7.yml -p p09-performance-batch7 up -d --build backend
docker inspect p09-performance-batch7-backend-1 --format '{{json .Mounts}}'
docker compose -f docker-compose.yml -f performance/docker-compose.batch7.yml -p p09-performance-batch7 exec backend sh -lc 'echo "$RESUME_DIR"; ls -ld "$RESUME_DIR"'
```

The targeted `up -d --build backend` command preserves named volumes; inspect
the mount before proceeding. Upload/retrieval should then be exercised only with
synthetic credentials and a non-sensitive PDF fixture.

### Next task

Restore Docker API access in the user PowerShell context, verify the Batch 7
mount and health state read-only, then run the synthetic resume upload/retrieval
and `/memory` ownership checks. After that, continue with the highest-value
missing Lab 2 evidence without touching Batch 3 or the original Lab 1 workspace.

## Kafka implementation and failure-verification pass — 2026-11-15

### Scope completed

- Audited the typed envelope, producer, transactional outbox, manual-commit
  consumer, worker, durable `processed_events` claim, retry, and DLQ paths.
- Added strict validation for event identity, positive aggregate IDs, string
  correlation fields, timestamps, and schema version.
- Added non-sensitive structured consumer/worker logs containing topic/event
  type, event ID, trace ID, aggregate ID, outcome, attempt, and error type.
- Added safe event/trace/aggregate correlation fields to raw DLQ records when a
  malformed body contains them; raw payload remains bounded and truncated.
- Added focused tests for commit ordering, retry-before-commit behavior,
  durable restart-safe duplicate claims, raw DLQ metadata, and invalid fields.
- Added Kafka implementation, failure procedure, and evidence-index documents.

### Actual verification

```text
py -3.12 -m pytest -q backend/tests/test_kafka_pipeline.py backend/tests/test_outbox.py
```

Result: **15 passed**, with one pytest cache warning caused by Windows access
denial on `.pytest_cache`.

Docker runtime verification was **blocked**, not silently skipped: access to
`npipe:////./pipe/dockerDesktopLinuxEngine` is denied from this Codex terminal.
No container, volume, topic, or database was changed. See
`docs/KAFKA_FAILURE_SCENARIOS.md` for user-side PowerShell commands.

### Honest implementation boundary

The durable inbox uses a unique event ID and is claimed before the current
worker's memory side effect. This supports restart-safe duplicate suppression,
but is not an atomic cross-store transaction between `processed_events` and
MongoDB. The narrow claim-before-side-effect crash window remains a documented
Lab 2 limitation rather than an exactly-once claim.

### Regression result after Kafka changes

- Focused Kafka/outbox: **15 passed**.
- Full backend command `py -3.12 -m pytest -q`: **98 passed, 4 errors**.
  All four errors occurred during `tmp_path` fixture setup for existing resume
  tests because the environment cannot scan the shared Windows pytest temp
  directory (`WinError 5: Access is denied`); no assertion failure was reported.
- A rerun with a fresh repository-local `--basetemp` reached the same fixture
  permission condition and exited with the same environment limitation.
- Python compilation `py -3.12 -m compileall -q backend`: passed.
- `git diff --check`: passed; Git emitted only existing line-ending warnings.
- `py -3.12 -m ruff check ...`: not run successfully because `ruff` is not
  installed in the selected Python environment; no dependency was installed.

## Submission-preparation pass — 2026-11-15

### Verified in this execution

- Professor PDF re-read with Python 3.10 `pypdf`: 7 pages, 40 points.
- Backend using `.venv312`: **102 passed, 1 Starlette/httpx deprecation warning**.
- Frontend: **24 passed** across 4 files using `npm test -- --run`.
- Frontend production build: passed with Vite 8.3.4.
- Frontend lint: exit 0; three known `react(set-state-in-effect)` warnings in
  `CompanyPage.jsx:16`, `JobsPage.jsx:122`, and `EventsPage.jsx:40`.
- Deterministic harness: **10 passed, 0 failed**.
- `git diff --check`: passed.

The npm and backend commands were rerun in the approved elevated local context
after sandbox-only `spawn EPERM`/pytest-temp failures; no application or
dependency files were changed by the elevated runs.

### Evidence artifacts created

- Root `README.md`, `RUN_LOG.txt`, and `AI_USE.md`.
- `docs/LAB2_SUBMISSION_READINESS.md`.
- `docs/evidence/README.md` and `docs/evidence/00_overview/STATUS.md`.

These documents contain only actual results and explicit gaps. No screenshots,
cloud results, or live Docker results were fabricated.

### Runtime blocker

`docker version` remains blocked by permission denied to
`npipe:////./pipe/dockerDesktopLinuxEngine`. Batch 7 runtime, current Kafka
failure replays, Mongo runtime, resume persistence, browser workflows, and
Redux DevTools capture require the student's Windows PowerShell/browser context.

### Live browser inspection — 2026-11-15

Computer-use inspection reached the existing Chrome pages at `localhost:15173`.
The Company Portal rendered real dashboard data including current postings,
events, application counts, enrolled students, and company profile content. The
login route also rendered with the existing sign-in form. This is genuine live
UI observation, but no screenshot file was written to the repository and no
authentication or mutating workflow was submitted during this inspection.
Full student/company workflow and Redux DevTools screenshots remain manual
evidence tasks.

## Service-boundary and deployment-preparation pass — 2026-11-15

### Implementation

- Added six independently runnable route-boundary entrypoints through
  `backend/app/service_entrypoint.py` and deterministic Pair 09 ports 9091-9096.
- Added `backend/Dockerfile.student`, `.company`, `.job`, `.application`,
  `.event`, and `.assistant`.
- Added six corresponding Compose services with health checks, shared
  dependency conditions, and resume-volume access for the application boundary.
- Added Kubernetes preparation manifests under `k8s/` for the six domain
  processes, compatibility API, workers, frontend, MySQL, MongoDB, Kafka,
  storage, ConfigMap and Secret instructions.
- Added local image build and dry-run deployment scripts under `scripts/`.

### Verification

- `backend/tests/test_service_entrypoint.py` plus config tests: **4 passed**.
- Full backend suite from repository root: **104 passed, 1 warning**.
- Frontend: **24 passed**; production build passed.
- Frontend lint: exit 0 with the three pre-existing React effect warnings.
- Python compileall: passed.
- YAML parse of `docker-compose.yml` and all `k8s/*.yaml`: passed.
- `git diff --check`: passed (only existing line-ending warnings from Git).

### Limitations

The domain processes are genuine independently runnable HTTP boundaries, but
they intentionally reuse the Lab 1-compatible FastAPI business implementation
and shared persistence. This is an incremental extraction boundary, not proof
of six independently-owned databases or fully split domain code. Docker/Kafka/
Mongo runtime verification and Kubernetes cluster validation remain blocked or
deferred in this execution context; no Docker or cluster state was changed.

The evidence-pack Markdown and DOCX draft were generated under `reports/`.
DOCX rendering could not be completed because the bundled LibreOffice renderer
was unavailable on PATH; the DOCX is therefore a draft artifact and is not
claimed as visually QA-verified.
