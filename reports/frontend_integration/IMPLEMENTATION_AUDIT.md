# Frontend Integration Implementation Audit

Date: 2026-10-26  
Branch: `codex/frontend-integration`  
Audit mode: read-only; no application source was edited before this report.

## Executive finding

The checked-out branch contains the FastAPI backend, backend tests, SQL schema/seed files, and the existing Part B/Part C reports, but it does not contain a `frontend/` directory. The submitted React/Vite frontend is present on the read-only remote ref `origin/rohini-frontend` (commits include `3c86416`, `831cd45`, `c775bba`, `57af376`, `eb55136`, `c9a18a3`, and `e3942e8`), but that ref was not checked out or modified. Therefore, frontend behavior can be audited from that ref, but frontend implementation in this worktree is blocked until the frontend is intentionally brought into this branch. No report, screenshot, tag, original branch, or database was changed.

## Repository and current state

- Current branch: `codex/frontend-integration`.
- Initial Git status: clean; no staged, unstaged, or untracked application changes.
- Current branch HEAD: `28ce3b5 Complete Part B and C agent implementation`.
- Current worktree contents: `backend/`, `docs/`, `pytest.ini`, `seed_data.py`.
- No `README.md`, frontend source, frontend package manifest, rubric PDF, or professor assignment PDF exists in this worktree.
- The remote frontend ref contains `frontend/` and `report/`, including submitted screenshots. Those files were inspected through `git show` only and were not copied, rewritten, or deleted.
- The professor's Lab 1 rubric PDF was not found in the current repository or the inspected frontend ref. Exact rubric verification is consequently unavailable; the existing project reports and the user-supplied requirements are the working rubric.

## Existing frontend pages and features (audited from `origin/rohini-frontend`)

The submitted React/Vite frontend includes:

- `App.jsx`: client-side routing, auth token presence check, student/company page selection, sidebar/navigation, logout, and dashboard shell.
- `LoginPage.jsx`: email/password login form with a student/company UI selector and navigation after login.
- `JobsPage.jsx`: jobs listing, local text/location/work-mode filtering, details modal, save-job behavior, and an application-started UI state.
- `EventsPage.jsx`: event listing, registration, save/remove saved item, and error/empty/loading states.
- `ProfilePage.jsx`: student profile form, profile update call, and PDF resume upload.
- `CompanyPage.jsx`: company dashboard/company-facing UI.
- `AssistantPage.jsx`: assistant UI exists in the inspected ref, but its API integration must be reconciled against the current `/assistant/chat` and `/assistant/confirm` contracts before it can be called complete.
- `SafetyPage.jsx` and `utils/safety.js`: client-side prompt-injection detection/sanitization demonstration and unit tests.
- `services/api.js`: centralized request helper, bearer token attachment, login/logout, jobs/events/saved items, profile update, resume upload, and dashboard calls.

Important observed frontend gaps from the inspected ref:

- No registration page or `POST /auth/register` client call is present.
- The login role selector is UI state, not authorization evidence; navigation is based on the selected dropdown value rather than the authenticated user returned by the backend.
- The inspected profile implementation uses hardcoded display/profile values and sends a fixed profile payload instead of loading the current profile from a backend GET endpoint. The backend has no student-profile GET endpoint, so a contract-preserving backend read endpoint may be required for correct persistence and refresh behavior.
- The jobs UI maps backend records to a separate local display shape and contains an application-started state; the API audit must verify that every visible operation is backed by an actual application endpoint.
- The current worktree cannot build or run this frontend because the frontend files and package manifest are absent here.

## Backend endpoints and request/response contracts

The FastAPI app is `backend/app/main.py`; auth is `backend/app/auth.py`; application endpoints are also in `backend/app/routes/applications.py`.

### Public/authentication

- `GET /health` -> `{status: "ok"}`.
- `GET /health/database` -> `{status: "ok", database: "connected"}` or HTTP 503.
- `POST /auth/register` accepts `name`, `email`, `password`, `role`, and role-specific `college` for students or `company_name` plus `location` for companies. It returns HTTP 201 with `id`, `name`, `email`, `role`, and `message`; it does not issue a token or automatically log the user in.
- `POST /auth/login` accepts `email`, `password`; it returns `access_token`, `token_type: "bearer"`, and `user: {id,name,email,role}`. Invalid credentials return HTTP 401.
- `GET /auth/me` requires `Authorization: Bearer <JWT>` and returns the database-derived identity `{id,name,email,role}`.

JWTs use `HS256`, `JWT_SECRET`, and a one-hour expiry. `get_authenticated_user` decodes the token and re-reads the user from the database, so the frontend must persist/send the access token and treat `/auth/me` as the authoritative current identity. Backend role checks remain authoritative.

### Profiles and preferences

- `POST /company/profile` and `PUT /company/profile` accept `company_name`, `location`, optional `description`, `contact_information`, and `website`; both upsert and return a message. `GET /company/profile` returns the company profile and requires company role.
- `PUT /student/profile` accepts the full `StudentProfileRequest`: optional `date_of_birth`, `city`, `state`, `country`, `career_objective`, required `college`, optional `degree`, `major`, `graduation_year`, `cgpa`, `experience`, and `phone`; it upserts and returns a message. There is currently no `GET /student/profile` endpoint, which prevents a frontend from fully rehydrating the saved student profile without a minimal backend contract addition.
- `GET /student/preferences` returns preference arrays, `remote_only`, and `minimum_salary`; `PUT /student/preferences` upserts the same shape and returns a message. Both require student role.

### Jobs and applications

- `POST /jobs` accepts `title`, `deadline`, `location`, optional `salary`, `description`, `category`, and `is_remote`; company-only; returns HTTP 201 `{id,message}`.
- `GET /jobs` supports `title`, `company`, `category`, `city`, `remote`, `minimum_salary`, `maximum_salary`, `limit`, and `offset`; returns database rows with job/company fields.
- `GET /jobs/{job_id}` returns one job plus company details or 404.
- `PUT /jobs/{job_id}` and `DELETE /jobs/{job_id}` are company-owner operations.
- `GET /company/jobs` returns the authenticated company's jobs and `application_count`.
- `POST /applications/resume` uploads a PDF for a student; `GET /applications/resume` lists the student's uploaded resumes.
- `POST /applications/{job_id}/apply` accepts optional `resume_path`, is student-only, checks job deadline and duplicate applications, and returns HTTP 201.
- `GET /applications/student` lists the student's applications.
- `GET /applications/company/jobs/{job_id}/applicants` and `PATCH /applications/company/jobs/{job_id}/applicants/{application_id}/status` are company-owner operations.

### Events, saved items, dashboards, and search

- `POST /events`, `GET /events`, `GET /events/{event_id}`, `PUT /events/{event_id}`, and `DELETE /events/{event_id}` support company-owned event CRUD and public listing/details. Listing supports `name`, `city`, `event_date`, `limit`, and `offset`.
- `POST /events/{event_id}/register`, `DELETE /events/{event_id}/register`, and `GET /events/student/registrations` are student-only; `GET /events/{event_id}/registrants` is company-owner-only.
- `POST /saved-items` accepts `{item_type: "job"|"event", item_id}` and is student-only; `GET /saved-items` returns saved records with `details`; `DELETE /saved-items/{saved_item_id}` removes a student-owned item.
- `GET /dashboard/student` returns application counts, upcoming events, and saved-item count; `GET /dashboard/company` returns owned job/event counts and application counts.
- `GET /search/students` and `GET /search/companies` provide public recruiter/search listings with filters.

### Assistant and confirmation

- `POST /assistant/chat` is student-only and accepts `{message, conversation_id?}`. It returns `{answer, conversation_id}`. Conversation state is keyed in memory by `(authenticated_user_id, conversation_id)`.
- The agent is hand-built in `backend/app/agent.py`, uses `OllamaModel`, and exposes exactly five tools: `get_student_preferences`, `search_jobs`, `get_job_details`, `search_events`, and `save_job_or_event`.
- `save_job_or_event` never writes. It creates a user-bound, expiring, single-use pending action and returns text containing `Confirmation required: {action_id,item_type,item_id}`.
- `POST /assistant/confirm` is student-only and accepts `{action_id, approved}`. Approval revalidates the pending action, authenticated student, item existence, duplicate status, and then inserts exactly one saved item. Refusal returns `{status: "cancelled", message: ...}`. Unknown, expired, replayed, cross-user, invalid, missing, or stale actions must be shown as errors/cancellation, never as success.

## Confirmed integration mismatches and missing functionality

1. **Branch/worktree mismatch — critical:** the frontend required for this task is absent from `codex/frontend-integration`; it exists only on `origin/rohini-frontend` and cannot be changed without explicitly bringing it into this branch.
2. **Registration — missing:** the inspected frontend has no registration flow for either role, although the backend contract supports both roles and does not auto-login.
3. **Role routing — unsafe:** login navigation trusts the selected role dropdown instead of `data.user.role` from the login response and a refreshed `/auth/me` check. This can produce a company UI for a student or vice versa, even though backend authorization remains intact.
4. **Auth rehydration — incomplete:** the frontend stores `access_token`, but the audited app needs an authoritative user/session load on refresh and must clear invalid/expired sessions on 401. The backend returns role from the token-backed database lookup.
5. **Student profile hydration — incomplete:** the frontend uses hardcoded profile values and fixed update fields. The backend supports update but not read; this is a contract gap requiring either an explicit minimal `GET /student/profile` endpoint or a clearly documented limitation.
6. **Company profile integration — incomplete/needs verification:** the backend supports GET/PUT, while the frontend implementation must be checked for loading/saving the real company profile and role-specific visibility.
7. **Job applications — incomplete:** the jobs page's inspected “Apply now” behavior only changes local UI state; it must upload/select a real resume and call `POST /applications/{job_id}/apply`.
8. **Job/event mapping — fragile:** inspected UI code uses local display fields such as `company`, `mode`, and `skills`; the backend returns `company_name`, `is_remote`, and no structured skills field. Mapping must be explicit and must not fabricate or drop data.
9. **API configuration — partially consolidated:** `frontend/src/services/api.js` uses `VITE_API_URL || http://localhost:9090`, but the current worktree has no frontend configuration or startup documentation. The final implementation must document one source of truth and verify the actual local backend port.
10. **Assistant UI — contract verification required:** the backend returns `answer` and `conversation_id`, and confirmation requires `action_id` plus `approved`. The frontend must parse the server-created pending action, display loading/errors, preserve conversation ID per user session, and call `/assistant/confirm` exactly; no client-side auto-approval is acceptable.
11. **Error handling — needs end-to-end verification:** API errors are converted from raw response text in the inspected request helper; the UI must render useful `detail` messages and must not show success after a failed request.

## Rubric mapping

Because the professor PDF is unavailable, this maps findings to the supplied Lab 1 requirements rather than claiming exact professor wording.

| Requirement | Evidence/implementation state | Status |
|---|---|---|
| Frontend/backend integration | Backend contracts exist; frontend absent from current worktree | Blocked in this worktree |
| Student/company registration | Backend exists; frontend flow missing | Not verified |
| Login and authenticated role routing | JWT backend exists; UI role selector is not authoritative | Partially verified |
| Role-specific dashboards and authorization | Backend `require_role` checks exist; UI requires integration | Partially verified |
| Student/company profile persistence | Backend update endpoints exist; student read endpoint missing; frontend hydration incomplete | Partially verified |
| Jobs listing/filter/detail | Backend supports filters/detail; frontend mapping needs contract correction | Partially verified |
| Company job posting/applicant management | Backend routes exist; frontend source unavailable in current worktree | Not verified |
| Events and registrations | Backend routes exist; frontend exists only on remote ref | Partially verified |
| Saved jobs/events | Backend routes and assistant gate exist; frontend confirmation/persistence needs integration tests | Partially verified |
| AI assistant five tools and hand-built loop | Existing backend report/tests document and test the implementation | Verified by existing backend tests; frontend blocked |
| Save confirmation gate | Backend contract and tests exist; frontend client must wire exact action | Partially verified |
| Prompt-injection defenses | Backend delimiters/tests and frontend safety utility exist on remote ref | Partially verified; live end-to-end not verified |
| Five transcripts, confirmation evidence, before/after injection tests, 20-turn reliability | Existing report documents backend evidence and limitations; no new evidence generated by this audit | Partially verified per existing report |
| Visual identity preservation | Submitted screenshots exist on remote ref; current worktree has no UI to compare | Blocked |

## Prioritized implementation plan

1. Resolve the branch-state dependency by bringing the existing frontend from the inspected remote ref into this branch without touching submitted reports/screenshots or the original branch. Record the exact source commit and preserve the existing styles.
2. Add a single frontend API configuration module and startup documentation; add robust response-error parsing and session rehydration from `/auth/me`.
3. Add registration for student and company roles using the existing `/auth/register` schema; do not auto-login unless the backend response changes to include a token.
4. Replace role-dropdown authorization with login-response and `/auth/me` role routing; enforce UI visibility while retaining backend checks.
5. Connect real profile GET/PUT flows. If student persistence cannot be rehydrated from existing contracts, add only a minimal authenticated `GET /student/profile` endpoint and a targeted backend test.
6. Correct jobs, applications, events, saved-item, and company-management mappings and states against actual endpoint schemas; remove local-only fake success behavior.
7. Reconcile assistant request/response and confirmation parsing with `/assistant/chat` and `/assistant/confirm`; preserve conversation IDs and show pending approval without claiming a save.
8. Run existing backend/frontend tests, add targeted integration/contract tests using safe fixtures or mocks, and document real outcomes. Do not mutate the submitted database or fabricate rubric evidence.
9. Produce `FINAL_VERIFICATION.md` with changed files, tests, role checks, visual-preservation statement, rubric status, limitations, and exact startup commands.

## Startup commands identified during audit

Backend dependencies are listed in `backend/requirements.txt`; the app entry point is `backend.app.main:app`. The exact backend command should be run from the repository root after environment variables and the local MySQL database are available:

```powershell
python -m uvicorn backend.app.main:app --reload --port 9090
```

The frontend startup command cannot be executed in this worktree because `frontend/package.json` is absent. On the inspected frontend ref, it is a Vite app and is expected to use:

```powershell
cd frontend
npm install
npm run dev
```

The backend port must match `VITE_API_URL` (the inspected frontend default is `http://localhost:9090`). This is an observed convention, not a claim that the backend is currently running.
