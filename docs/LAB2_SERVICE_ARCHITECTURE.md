# CareerBridge Lab 2 Service Architecture

Pair 09 uses the existing Lab 1 HTTP API as the compatibility boundary. The initial
extraction is a modular service boundary inside the FastAPI deployment; independent
containers will be introduced only after each boundary has contract tests and a real
startup/health path.

## Ownership

| Boundary | Owns | Existing compatible routes | Dependencies |
|---|---|---|---|
| Student | Student profile, preferences, student search, student-facing identity | `/student/profile`, `/student/preferences`, `/search/students`, `/auth/me` | Auth, MySQL initially; Mongo target in migration stage |
| Company | Company profile, company-owned records, company directory | `/company/profile`, `/company/jobs`, `/company/events`, `/search/companies` | Auth, Job/Event/Application boundaries, MySQL initially |
| Job | Job discovery, details, company ownership for postings | `/jobs`, `/jobs/{job_id}`, `/company/jobs` | Company profile, database; Kafka `job.created` later |
| Application | Apply, student history, company applicants, status updates, resume authorization | `/applications/*` | Student, Job, Auth; Kafka application events later |
| Event | Event discovery, registration, company event management and registrants | `/events/*`, `/company/events` | Student, Company, Auth; Kafka registration events later |
| AI Assistant | Five tools, bounded hand-built loop, confirmation proposal, conversation state | `/assistant/chat`, `/assistant/confirm` | Student identity, Job/Event tools, Ollama, confirmation store |

## Implemented extraction

`backend/app/services/student_service.py` owns student profile retrieval and update SQL.
`backend/app/main.py` remains the compatibility adapter: it performs authentication and
role enforcement, passes the existing `query_db` adapter to the service, and returns the
existing response shapes and status codes. Existing route tests continue to monkeypatch
the application query adapter, so no database is required for the contract tests.

## Communication plan

Synchronous compatibility calls remain HTTP/API-internal until extracted boundaries are
verified. State-changing workflows will publish typed events only after the corresponding
database transaction and idempotency strategy are implemented. Planned Pair 09 topics are:

- `p09.application.created`
- `p09.application.updated`
- `p09.application.status_changed`
- `p09.event.registration_created`
- `p09.job.created`

## Extraction rules

1. Preserve every existing Lab 1 route, method, request model, response shape, and role check.
2. Extract one bounded responsibility at a time and keep the route as a thin compatibility adapter.
3. Add mocked contract tests before changing persistence or introducing asynchronous delivery.
4. Do not duplicate SQL in a second service; pass repository/query dependencies explicitly during migration.
5. A boundary is not marked independently deployable until it has a real entrypoint, dependencies, health check, and runtime verification.
