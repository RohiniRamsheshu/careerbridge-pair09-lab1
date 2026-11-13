# Frontend Integration Implementation Plan

Date: 2026-10-26
Branch: `codex/frontend-integration`
Scope: local isolated worktree only

## Preserved baseline

Before this plan, the worktree was confirmed at HEAD `28ce3b5` with remote `https://github.com/RohiniRamsheshu/careerbridge-pair09-lab1.git`. Existing changes are preserved: modified `backend/app/main.py`, untracked `frontend/`, and untracked `reports/`. The existing student-profile read endpoint in `backend/app/main.py`, restored frontend source, audit, and final-verification reports are treated as pre-existing work and will not be discarded or rewritten.

## Phase 1 — Part A implementation

1. Student profile completeness
   - Files: `frontend/src/pages/ProfilePage.jsx`, `frontend/src/services/api.js`, targeted `frontend/src/App.css` additions only if required.
   - Use the existing `GET /student/profile` and `PUT /student/profile` contracts.
   - Add supported fields already present in `StudentProfileRequest`: date of birth, city/state/country, career objective, college, degree, major, graduation year, CGPA, experience, and phone.
   - Do not invent database fields. Skills, profile pictures, and email editing will be handled only if an existing endpoint/schema supports them; otherwise they remain explicit gaps.

2. Company profile completeness
   - Files: `frontend/src/pages/CompanyPage.jsx`, `frontend/src/services/api.js`.
   - Use `GET /company/profile` and `PUT /company/profile` for company name, location, description, contact information, and website.
   - Preserve company-only routing and backend authorization.

3. Jobs filtering
   - Files: `frontend/src/pages/JobsPage.jsx`, `frontend/src/services/api.js`.
   - Use backend-supported `title`, `company`, `category`, `city`, `remote`, `minimum_salary`, `maximum_salary`, `limit`, and `offset` query parameters.
   - Replace local-only filtering where it prevents actual backend search; preserve existing filters/cards/layout.

4. Company applications and student search
   - Files: `frontend/src/pages/CompanyPage.jsx`, `frontend/src/services/api.js`.
   - Use existing `/applications/company/jobs/{job_id}/applicants`, PATCH status endpoint, and `GET /search/students`.
   - Add targeted applicant status controls and student search only within the existing company workspace visual language.

5. Events and saved/registration history
   - Files: `frontend/src/pages/EventsPage.jsx`, `frontend/src/pages/CompanyPage.jsx`, `frontend/src/services/api.js`.
   - Use existing event CRUD, registration history, registrant, and saved-item endpoints.
   - Add student registered-event visibility and company event management without changing the page hierarchy.

6. Any additional confirmed Part A gaps
   - Inspect route/schema support first.
   - Make the smallest safe backend addition only when a required capability is genuinely absent, with a focused test and no schema/data mutation.

## Phase 2 — Focused tests and quality

- Add/update frontend unit tests for API mapping, role visibility, filter query construction, profile payloads, and confirmation/error states using mocks.
- Add backend contract tests only for new read-only routes or authorization behavior; use mocks/fixtures and never the existing project database for writes.
- Investigate Vite `spawn EPERM` by retrying the existing command with the already-installed local dependencies and permitted process execution; do not disable security controls or alter unrelated environment settings.
- Address the two React effect lint warnings only if behavior remains unchanged.

## Phase 3 — Review gate

- Report changed files, requirements addressed, exact test outcomes, blocked tests, remaining rubric gaps, and screenshot-impact assessment.
- Stop before live database/account/assistant integration. Live testing requires separate approval and an isolated test setup.

## Prohibited actions

No edits to the original workspace, shared GitHub state, submitted report/screenshots, existing commits/tags, seed data, database contents, or original staged/untracked files. No commit, merge, rebase, reset, amend, tag, push, migration, seed script, or destructive command.
