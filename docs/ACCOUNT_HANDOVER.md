# CareerBridge Account Handover

This document hands the project to a new ChatGPT Edu/Codex session. The current worktree is
the source of truth; do not infer completion from the submitted Lab 1 report.

## Repository and protection

- Development repository: `C:\Users\Bhushan Waingankar\Desktop\handshake-lab1-codex`
- Branch: `feature/gotham-premium-redesign`
- HEAD: `2a5dd788f4f83029e6202d8e893455f77aeeae01`
- Original workspace: `C:\Users\Bhushan Waingankar\Desktop\handshake-lab1` on `shoury-backend`
- Checkpoint branch: `backup/lab1-before-redesign`
- Checkpoint commit: `2a5dd788f4f83029e6202d8e893455f77aeeae01`
- Independent backup: `C:\Users\Bhushan Waingankar\Desktop\handshake-lab1-codex-backup-20261112`

The original workspace, checkpoint, backup, submitted report/screenshots, and shared GitHub
repository must remain untouched. No commit, push, tag, reset, rebase, merge, or cleanup is
authorized without explicit approval.

## Purpose and architecture

CareerBridge is a Handshake-style SJSU DATA 260 platform for student/company accounts,
profiles, job discovery, applications, events, registrations, saved items, company management,
and a hand-built AI opportunity assistant.

Current stack: React 19, Vite 8, React Router, FastAPI 0.143.3, MySQL, bcrypt, JWT,
local Ollama, and component-local frontend state. The backend remains a monolithic FastAPI
process, with early modular Student and Application boundaries. Redux, Kafka, MongoDB,
JMeter, Kubernetes, and independently deployed six services are not complete.

Verified Python runtime:

```text
C:\Users\Bhushan Waingankar\AppData\Local\Python\pythoncore-3.12-64\python.exe
Python 3.12.10
```

Verified packages include bcrypt 5.0.0, FastAPI 0.143.3, pytest 9.1.1, httpx 0.28.1,
pydantic 2.14.1, mysql-connector-python 26.10.0, and python-jose 3.5.0.

## Pair 09 configuration

- `PAIR=09`
- `PORT_BASE=9090`, derived from `9000 + (PAIR × 10)`.
- Database/Kafka prefix: `p09`.
- `SEED=09`.
- `CITY_SET`: San Jose, Mountain View, Palo Alto.

These values are centralized in `backend/app/config.py`. The disposable Compose database is
`handshake_lab1_local`; never write to the shared `handshake_lab1` database.

## Lab 1 API compatibility

Preserve existing paths, methods, request/response shapes, authentication, role checks,
ownership checks, and database relationships. Important routes are:

- Health/auth: `GET /health`, `GET /health/database`, `POST /auth/register`,
  `POST /auth/login`, `GET /auth/me`.
- Profiles/preferences/search: `/company/profile`, `/student/profile`,
  `/student/preferences`, `/search/students`, `/search/companies`.
- Jobs: `POST/GET /jobs`, `GET/PUT/DELETE /jobs/{job_id}`, `GET /company/jobs`.
- Applications: resume upload/list, `/applications/{job_id}/apply`, student history,
  company applicants/profile/resume/status routes under `/applications/company/...`.
- Events: event CRUD, event registration/unregistration, student registrations,
  company events, registrants, and authorized registrant profiles.
- Saved items: `POST/GET /saved-items`, `DELETE /saved-items/{saved_item_id}`.
- Dashboards: `/dashboard/student`, `/dashboard/company`.
- Assistant: `POST /assistant/chat`, `POST /assistant/confirm`.

Student data is authenticated-user scoped. Company applicant/profile/resume/status access
requires company role, owned job, and related application. Company event registrant profile
access requires company ownership and registration membership. Resume preview validates path
containment and PDF signature and does not expose filesystem paths in the profile response.

## Lab 1 workflows and assistant

Students can register/login, edit supported profile data, search jobs/events, view details,
apply, register for events, save/unsave jobs/events, view application history, and use the
assistant. Companies can register/login, edit company profile, create/manage owned jobs/events,
view applicants/registrants, preview authorized resumes, and update application statuses.

The hand-built assistant is in `backend/app/agent.py`, using `OllamaModel` from
`backend/app/ai_model.py`. Its five required tools are:

1. `get_student_preferences`
2. `search_jobs`
3. `get_job_details`
4. `search_events`
5. `save_job_or_event`

Existing behavior includes typed argument validation, tool allowlisting, bounded iterations,
untrusted retrieved-data delimiters, role authorization, and explicit confirmation before saves.
The exact pending action must be approved by the authenticated student; preserve expiry,
single-use, replay, cross-user, decline, and target revalidation behavior.

## Current architectural decisions

- Keep Lab 1 HTTP routes as the compatibility boundary.
- Extract domain logic behind route adapters instead of copying the monolith six times.
- Student logic: `backend/app/services/student_service.py`.
- Application logic: `backend/app/services/application_service.py`.
- Typed event envelopes: `backend/app/events/contracts.py`; Kafka transport is not connected.
- Pair configuration: `backend/app/config.py`.
- Local containers: `backend/Dockerfile`, `frontend/Dockerfile`, `docker-compose.yml`.
- Gotham work currently consists of tokens, display typography fallback, and focus states in
  `frontend/src/index.css`; full screen redesign is not complete.

## Professor Lab 2 requirements

The PDF is authoritative. Total: 40 points, due November 16, 2026.

- Part 1 Docker/Kubernetes/AWS: 11 points.
- Part 2 Kafka asynchronous messaging: 8 points.
- Part 3 MongoDB and assistant memory: 9 points.
- Part 4 Redux integration: 4 points.
- Part 5 JMeter performance: 5 points.
- Part 6 context management, guardrails, observability: 3 points.

The exact matrix is in `docs/LAB2_REQUIREMENT_TRACEABILITY.md`. It includes six service
Dockerfiles, Compose, Kubernetes, ECR/EKS, LoadBalancer/Ingress, Kafka topics and three
failure demonstrations, complete Mongo migration, three memory layers with 60-entry
consolidation, six Redux slices and DevTools evidence, JMeter concurrency/metrics, token
tracking/compaction, 50-request traces, eight guardrails, deterministic harness output,
real Ollama transcripts, README/RUN_LOG/METRICS/AI_USE, report PDF, screenshots, recording,
tags, viva/restoration, and both-partner participation.

## AWS and submission restrictions

AWS CLI is installed, but identity and permissions are unverified. Never request credentials
in chat. Do not change IAM, create ECR/EKS/networking/LoadBalancer resources, incur charges,
or deploy without explicit approval after showing resources, permissions, costs, and restoration.

The PDF requires a private pair repository, regular contributions by both partners, `lab1` and
`lab2` tags, a Lab 2 report, screenshots, metrics/logs, AI disclosure, and pair verification
recording. Coordinate with Rohini before any final submission history or demonstration.
