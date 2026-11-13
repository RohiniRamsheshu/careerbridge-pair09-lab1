# DATA 260 Lab 1 Missing Evidence Checklist

Date: 2026-10-27  
Branch: `codex/frontend-integration`

This checklist is separate from the submitted report. It does not replace, rewrite, or add claims to the submitted PDF or screenshots.

## Part A — platform evidence

- [ ] Live student registration and login run with a safe test account.
- [ ] Live company registration and login run with a safe test account.
- [ ] Student/company role-routing demonstration after login and refresh.
- [ ] Student profile evidence covering supported fields and persistence.
- [ ] Evidence for skills, profile picture, and email editing, or explicit documentation that backend support is absent.
- [ ] Company profile persistence evidence, including supported contact and website fields.
- [ ] Job search evidence for title/company, all four categories, city, remote/on-site, and detail fields.
- [ ] Student application evidence showing PDF resume upload, application date, and Pending/Reviewed/Declined filtering.
- [ ] Company applicant evidence showing profile/resume access and status updates.
- [ ] Student event evidence showing search, detail, registration, and registered-event history.
- [ ] Company event evidence showing CRUD and registered-student/profile viewing.
- [ ] Student search evidence for name, college, and major. Skillset support must be marked unavailable unless a backend contract is added and approved.
- [ ] AI assistant availability from the student home/dashboard experience.
- [ ] Swagger/OpenAPI or exported Postman evidence with parameters, headers, and sample responses.
- [ ] Safe verification of required seed counts: 300 jobs, 1,500 applications, 200 students, 50 companies, and 100 events. Do not regenerate existing data.

## Part B — hand-built agent evidence (12 points)

- [x] Single Ollama client interface with `complete(messages, tools)` in `backend/app/ai_model.py`.
- [x] Hand-built bounded loop in `backend/app/agent.py`; no agent framework.
- [x] Five required tools and JSON schemas in `backend/app/agent.py`.
- [ ] Captured evidence explicitly showing one tool-call line with tool name/arguments and a tool-call count for every live run.
- [ ] Complete live transcript: internship in the student's city, including preferences first.
- [ ] Complete live transcript: remote data-science internship with category/location/skills filters.
- [ ] Complete live transcript: computer-science event next month with date/eligibility filters.
- [ ] Complete live same-conversation refinement transcript.
- [ ] Complete live absent-job/company transcript with truthful no-match response.
- [ ] Fresh review confirming all transcript tool results are database-backed and not fixtures.

## Part C — safety and reliability evidence (6 points)

- [x] Confirmation action is isolated in `backend/app/confirmation.py`.
- [x] Save action is gated, user-bound, expiring, single-use, and revalidated by the API.
- [ ] Captured refusal transcript showing cancellation acknowledgement without retrying.
- [ ] Five before-defense prompt-injection verification queries with recorded unsafe behavior.
- [ ] Five after-defense verification queries with exact changed behavior, `<retrieved_data>` delimiters, and no unauthorized save.
- [x] Automated malformed/unknown/wrong-type/tool-failure/repair-path coverage exists in `backend/tests/test_agent_part_bc.py`.
- [ ] Evidence table explicitly reports valid and failed calls across at least 20 assistant turns, classified by required failure modes.
- [ ] Fresh live reliability measurement with timing/turn counts, if required by the instructor's interpretation.

## Required submission artifacts

- [ ] Repository `README.md` with setup/startup instructions.
- [ ] `RUN_LOG.txt` for the lab.
- [ ] `METRICS.md` with reliability measurements.
- [ ] `AI_USE.md` with each partner's AI-use disclosure and incorrect-output correction.
- [ ] API documentation or exported Postman collection.
- [ ] Final PDF report containing goals, design, screenshots, API tests, pair parameters, seed counts, transcripts, reliability table, and injection before/after evidence.
- [ ] One five-minute Lab 1 screen recording with both partners running/explaining the system.
- [ ] Pair verification recording and Git history evidence, if required separately by Canvas.
- [ ] Instructor/grader access invitation to the private repository.

## Current automated verification

- Frontend Vitest: 7 passed.
- Frontend production build: passed.
- Backend pytest: 33 passed.
- Frontend lint: one non-blocking `react/set-state-in-effect` warning in `frontend/src/pages/CompanyPage.jsx`.

## Explicitly not performed

- No live database writes.
- No live account creation.
- No live Ollama calls.
- No seed/migration commands.
- No screenshot or transcript generation.
- No report modification.
- No commit, push, merge, rebase, reset, amend, tag, or shared GitHub change.
