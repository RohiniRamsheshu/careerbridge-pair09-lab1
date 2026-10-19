# Part B / Part C implementation report

## Current evidence status — final repair pass

This is the primary status summary. The earlier failed runs and the original checklist claims remain below as historical context, but are superseded where this section and the final live-transcript section provide newer evidence.

- Automated tests: **30 passed, 1 warning** in the recorded full-suite run.
- Live Scenario 1: **verified complete**; preferences were checked first and real San Jose internship rows were returned.
- Live Scenario 2: **verified complete**; the real remote/internship/data-science search returned a complete truthful no-match response.
- Live Scenario 3: **verified complete**; the real November 1–30 computer-science event search returned a complete truthful no-match response.
- Live Scenario 4: **live conversation and tool refinement verified**, but the captured live model prose was truncated. The final-response formatter was separately validated against the retrieved rows; this is not a complete captured live transcript.
- Live Scenario 5: **verified complete**; the real absent-company search returned a complete truthful no-match response after bounded tool-call recovery.
- Screenshots: **not captured or verified**. No screenshot evidence is claimed.
- Remaining evidence gaps: the professor PDF was unavailable; frontend confirmation wiring is outside this repository; Scenario 4 needs a fresh captured run if a complete live prose transcript is required.

## Scope and audit

The repository had no assignment PDF, so the supplied Part B/Part C requirements were used as the working rubric. Existing Git history and tags were not changed. Existing frontend files, database schema, seed records, auth, CRUD routes, and teammate work were left intact.

Before this work, the five tools and Ollama client existed, but saves used terminal `input()`, `/assistant/chat` reset history, malformed JSON became `{}`, tool results used a custom `tool_name` field, and there was no API confirmation flow or reliability evidence.

## Changes

- `backend/app/agent.py`: validated schemas and arguments; five SQL-backed tools; safe strings for errors; bounded six-iteration loop; 12-call safety cap; standard tool-result messages; logging count; untrusted retrieved-data delimiters.
- `backend/app/confirmation.py`: own-module `confirm_action(tool_name, arguments, auto_approve=False, user_id=...)`; expiring, user-bound, single-use pending actions.
- `backend/app/main.py`: optional per-user `conversation_id`; `/assistant/confirm` approval/decline contract; exact-item revalidation before the only insert.
- `backend/app/ai_model.py`: rejects malformed Ollama responses, bounds generation with `num_predict`/temperature options, and converts timeout/JSON failures to safe model errors.
- `backend/tests/test_agent_part_bc.py`: deterministic mocked confirmation, tool-validation, five-payload injection-boundary, and 20-turn reliability coverage.
- `docs/live_transcripts_2026-10-19.md`: actual live Ollama/database scenario evidence with durations and failure classifications.

Intentionally unchanged: database schema/tables/seed data, login/JWT, existing API routes, frontend, commits, and tags. The confirmation flow needs no migration.

## Checklist

| Area | Status |
|---|---|
| One `OllamaModel.complete(messages, tools)` client | Verified complete |
| Five required tools and parameterized SQL | Verified complete by tests and DB smoke checks |
| Bounded multi-call loop and tool-result reinjection | Verified complete by tests |
| Per-user follow-up conversation state | Implemented but not verified with live frontend |
| Explicit save confirmation, decline, replay/expiry/user binding | Verified complete by unit tests |
| Prompt-injection defense | Verified for five malicious payloads and delimiter/non-authority behavior by tests; not complete protection against all future model failures |
| 20 reliability turns | Verified complete: 20 parameterized executions |
| Exact professor PDF rubric | Blocked: no PDF exists in repository |
| Five live Ollama transcripts | Partial: Scenarios 1, 2, 3, and 5 have complete final evidence; Scenario 4 verifies live context/tool refinement but its captured model prose was truncated |
| Screenshots | Incomplete: no screenshots were captured or verified |

## Tests and actual results

Commands:

```text
backend\.venv312\Scripts\python.exe -m pytest backend/tests/test_health.py backend/tests/test_agent_part_bc.py -q
30 passed, 1 warning in the final run

backend\.venv312\Scripts\python.exe -m pytest -q
30 passed, 1 warning in the final run
```

Additional checks: app import succeeded; `/assistant/chat` and `/assistant/confirm` registered; MySQL health returned `{'status': 'ok', 'database': 'connected'}`; one direct Ollama smoke call returned `{'role': 'assistant', 'content': 'OK'}`.

Live attempt command shape: `backend\\.venv312\\Scripts\\python.exe -u -` with one `run_assistant(...)` scenario per process. Before the fix, plain chat returned `OK`, while tool-schema startup timed out because model loading was aborted. Ollama logs showed `llama3.2:3b` loading 1.87 GiB with mixed CPU/GPU offload and only about 1.9 GiB free GPU memory.

The application fix uses a bounded tool-turn limit of 48 tokens and a larger final-answer limit, with temperature `0.2` and environment overrides. A bounded minimal tool request completed and returned a real `tool_calls` response. Full live evidence is in [live_transcripts_2026-10-19.md](live_transcripts_2026-10-19.md).

## Required scenario transcripts (mocked, deterministic)

These are test-fixture transcripts, not claimed live Ollama runs. The fixture is deterministic and is not presented as the current MySQL contents. A separate direct MySQL check below records the actual current outcomes.

1. Internship in the student's city

```text
USER: Find an internship in my city.
TOOL: get_student_preferences {}
RESULT: {"preferred_categories":["internship"],"preferred_cities":["San Jose"],"preferred_skills":["Python"],"remote_only":0,"minimum_salary":20}
TOOL: search_jobs {"category":"internship","city":"San Jose","skill":"Python","minimum_salary":20}
RESULT: <retrieved_data>[{"id":1,"title":"Data Analyst Intern","company":"Test Company","location":"San Jose","category":"internship","salary":25,"deadline":"2026-12-31"}]</retrieved_data>
ASSISTANT: I found Data Analyst Intern at Test Company in San Jose, paying 25, with a 2026-12-31 deadline.
```

2. Remote data science internship

```text
USER: Find a remote data science internship with relevant skills.
TOOL: search_jobs {"category":"internship","remote_only":true,"skill":"data science"}
RESULT: No matching jobs found.
ASSISTANT: I found no matching remote data-science internship in the database.
```

3. Computer science event next month

```text
USER: Find an event for computer science students next month.
TOOL: search_events {"date_from":"2026-11-01","date_to":"2026-11-30","major":"computer science"}
RESULT: No matching events found.
ASSISTANT: I found no eligible computer-science event between 2026-11-01 and 2026-11-30.
```

4. Follow-up refinement

```text
USER: Find internship jobs.
TOOL: search_jobs {"category":"internship"}
RESULT: <retrieved_data>[{"id":1,"title":"Data Analyst Intern",...}]</retrieved_data>
ASSISTANT: I found Data Analyst Intern.
USER: Make those results closer and higher-paying.
TOOL: search_jobs {"category":"internship","city":"San Jose","minimum_salary":20}
RESULT: <retrieved_data>[{"id":1,"title":"Data Analyst Intern",...}]</retrieved_data>
ASSISTANT: I refined the search to San Jose jobs meeting the higher salary threshold.
```

5. No matching company

```text
USER: Find jobs at DefinitelyNotInSeedData.
TOOL: search_jobs {"keyword":"DefinitelyNotInSeedData"}
RESULT: No matching jobs found.
ASSISTANT: I found no matching jobs and did not invent a company or job ID.
```

## Prompt-injection evidence

Before defense, raw retrieved descriptions were passed as ordinary model context, so a malicious description could be confused with instructions. After defense, five actual mocked test executions used descriptions containing: automatic-save instructions, direct approval instructions, system-prompt exfiltration, policy override, and administrator impersonation. Each result was wrapped in `<retrieved_data>...</retrieved_data>`, retained as data, and produced no save confirmation or database write. The system message explicitly says those contents are untrusted and cannot authorize saving or override rules. This is defense in depth, not a claim of complete prompt-injection elimination.

## Direct MySQL tool checks

Against the current database on 2026-10-19: `get_student_preferences {}` returned `No saved preferences for this student.`; an internship/San Jose search returned ten database-backed `Seed Job` records; remote internship plus `data science` returned `No matching jobs found.`; events from 2026-11-01 through 2026-11-30 for computer science returned `No matching events found.`; and `DefinitelyNotInSeedData` returned `No matching jobs found.`. These were direct tool executions, not model transcripts.

## Reliability report

All rows below are actual executions of the parameterized mocked test; `repair` means no repeated repair prompt was issued.

| ID | Scenario | Expected/actual | Class | Repair |
|---:|---|---|---|---|
| 1 | malformed JSON | error string, no tool | malformed args | yes |
| 2 | JSON array | error string, no tool | wrong shape | yes |
| 3 | unknown tool | error string | unknown tool | yes |
| 4 | missing job_id | validation error | missing required | yes |
| 5 | string job_id | validation error | wrong type | yes |
| 6 | unknown argument | validation error | schema violation | yes |
| 7 | preferences | fixture result | valid read | n/a |
| 8 | job search | fixture result | valid read | n/a |
| 9 | event search | fixture result | valid read | n/a |
| 10 | job details | fixture result | valid read | n/a |
| 11 | database exception | safe error string | tool failure | yes |
| 12 | direct answer | final text | valid no-tool | n/a |
| 13 | model text when tool expected | returned text safely | model behavior | yes |
| 14 | lost-chain-shaped call | tool result paired | chain handling | yes |
| 15 | malicious description | delimited data | injection | yes |
| 16 | null arguments | validation error | malformed args | yes |
| 17 | bad date | validation error | wrong format | yes |
| 18 | save proposal | pending action, zero writes | confirmation gate | yes |
| 19 | model exception | safe unavailable text | model failure | yes |
| 20 | repeated tool calls | safe ceiling | iteration bound | yes |

## Confirmation API contract

`POST /assistant/chat` with `{ "message": "...", "conversation_id": "optional-existing-id" }` returns `{ "answer": "...", "conversation_id": "..." }`. A save proposal appears in the answer as a server-created pending action containing the exact `item_type`, `item_id`, and `action_id`.

`POST /assistant/confirm` with `{ "action_id": "...", "approved": true|false }` requires the authenticated student. Approval revalidates existence and duplicate status, then performs exactly one insert. Decline returns HTTP 200 with `status: cancelled` and zero writes. Unknown, expired, replayed, or cross-student actions return an error and cannot write. The client cannot set `auto_approve`.

## AI-use disclosure notes

The implementation uses a local Ollama model through a hand-built Python tool loop. The model selects among five JSON-schema tools; SQL execution, validation, authentication, confirmation, and writes remain application-controlled. No paid AI API or agent framework is used. Historical timeout and malformed-tool runs are retained below the final repair evidence; the fixture transcripts in this report remain explicitly mocked. No screenshots were captured or verified.

## Historical submission-readiness assessment (superseded)

## Final repair-pass update (2026-10-19)

The prior assessment above is retained as historical evidence. The final repair pass verified 30 automated tests passed (one pre-existing warning) and produced the current live evidence summarized at the top of this report. It did not produce a complete captured live final-response transcript for Scenario 4; that limitation is recorded explicitly in [live_transcripts_2026-10-19.md](live_transcripts_2026-10-19.md).

Root cause was not unsupported Ollama tools: the installed model advertises `tools`, and a minimal tool request succeeded. Under the local mixed CPU/GPU runtime, tool calls were slow and the model sometimes emitted truncated JSON-like requests in `message.content`; a shared short output limit also truncated final prose. The targeted fix uses a 48-token tool-turn cap and a larger final cap, recovers only known tool names and schema keys from JSON-like content, preserves explicit user search filters, normalizes ambiguous event eligibility, and returns a complete summary only from already retrieved database rows when model prose is cut off. No framework, schema, or seed-data change was made.

Current status: the backend implementation and four complete live scenario outcomes are supported by tests/evidence; Scenario 4’s live context/tool behavior is supported, but its complete final prose transcript remains an evidence gap. The repository contains no frontend source, so `/assistant/chat` and `/assistant/confirm` remain documented for Rohini’s UI integration. No screenshots were captured or verified. No commit or push was made; existing history, branch, database, and teammate files were preserved.
