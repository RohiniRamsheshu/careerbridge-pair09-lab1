# Live Ollama transcript evidence — 2026-10-19

## Current verified status

This summary is primary. The historical pre-repair runs below are retained for auditability and are superseded by the final repair-pass results where newer evidence exists.

Environment: Ollama 0.40.5, `llama3.2:3b`, MySQL connected, real `run_assistant`, real database. Durations include model calls. Fixture examples remain in `PART_BC_REPORT.md` and are not live evidence.

- Scenario 1: complete live tool flow and complete final database-backed summary verified.
- Scenario 2: complete live search and truthful no-match final verified.
- Scenario 3: complete live date/eligibility search and truthful no-match final verified.
- Scenario 4: live conversation history, refinement, and database tool results verified; captured model final prose was truncated. A separate formatter check produced a complete summary from retrieved rows, but this is not a complete captured live transcript.
- Scenario 5: complete live search and truthful no-match final verified.
- Screenshots: none captured or verified.

## Historical pre-repair runs — superseded

## Scenario 1 — internship in San Jose

Duration: 128.83 seconds. Result: completed with safe repair and real database results.

User: `Find an internship in San Jose. Check my student preferences first and use them if present.`

Observed tool sequence:

1. `get_student_preferences {}` → `No saved preferences for this student.` (agent preflight)
2. Model requested `search_jobs` with `city=San Jose`, `minimum_salary=0`, and `deadline_by=""`; validation rejected it: `argument deadline_by must be YYYY-MM-DD`. No write occurred.
3. Model requested `get_student_preferences {}` again.
4. Model requested `search_jobs {"city":"San Jose","minimum_salary":0}` → real `<retrieved_data>` containing San Jose jobs including internship records such as job 36, `Seed Job 0034`, `Seed Company 0019`, salary `106796.00`, deadline `2027-01-05`.

Final model response began: `Here are some internships in San Jose:` and listed database-backed Seed Job records. The first malformed request was repaired safely; no invented record was used by the tool layer.

## Scenario 2 — remote data science internship

Duration: 112.99 seconds. Result: failed final-answer completion; tool safety passed.

User: `Find a remote data science internship. Use search_jobs with category internship, remote_only true, and a relevant data science skill; do not invent results.`

Observed calls:

- `search_jobs` with empty-string optional values → validation rejected empty `deadline_by`.
- `search_jobs {"category":"internship","remote_only":true,"skill":"data science"}` → `No matching jobs found.`
- Same valid search repeated twice → `No matching jobs found.`
- `get_student_preferences {}` → `No saved preferences for this student.`

Final response asked to restart and request preferences instead of reporting the valid no-match result. No records were invented and no write occurred. The bounded loop stopped.

## Scenario 3 — computer science event next month

Duration: 23.10 seconds. Result: failed model tool-call formatting.

User: `Find an event for computer science students next month. Call search_events with the exact date window 2026-11-01 through 2026-11-30 and an eligibility or major filter.`

The model returned truncated text beginning `{"name": "search_events", "parameters": {"city": "", "date_from": "2026-11-01", "date_to": "2026-11-30", "eligibility": "computer science students"...}` with no `tool_calls` field. The application did not execute it, did not invent an event, and returned the bounded model text.

## Scenario 4 — same-conversation refinement

Duration: 137.07 seconds. Result: completed with real context preservation and real database results.

Turn 1: `Find internship jobs in San Jose.`

Tool: `search_jobs {"city":"San Jose"}` → real results. The conversation retained the user turn, assistant tool call, tool result, and final answer.

Turn 2: `Make those results closer and higher-paying.`

Tool: `search_jobs {"category":"internship","city":"San Jose","minimum_salary":100000,"remote_only":false}` → real results including job 36 (`106796.00`), job 85 (`106976.00`), job 102 (`113946.00`), and others.

Final response began: `Here are some higher-paying internship job opportunities in San Jose:`. The second request used prior conversation context and applied location/category/salary refinement.

## Scenario 5 — absent company

Duration: 26.02 seconds. Result: failed model tool-call formatting.

User: `Find jobs at DefinitelyNotInSeedData and report no matches if none exist. Use search_jobs.`

The model returned truncated text beginning `{"name": "search_jobs", "parameters": {"category": "", "city": "DefinitelyNotInSeedData", "deadline_by": "", "keyword": "jobs at DefinitelyNotInSeedData"...}` with no `tool_calls` field. The application executed no search and invented no result.

## Live verdict

1 and 4 completed; 2 produced a truthful database no-match but failed to finalize; 3 and 5 failed before tool execution because the model emitted truncated JSON as ordinary text. These failures are not presented as passing transcripts.

## Final repair pass — verified results

The earlier section records the pre-repair failures and is retained for audit history. The following runs used the same real `llama3.2:3b` Ollama model, MySQL database, and `run_assistant`; no fixture results were substituted.

| Scenario | Duration | Tool evidence | Final result |
|---|---:|---|---|
| 1. Internship in San Jose | 54.36 s | `get_student_preferences {}` → no saved preferences; `search_jobs {city: "San Jose"}` → real San Jose internship rows | Passed. Complete database-backed summary returned; no invented records. |
| 2. Remote data science internship | 56.77 s | `search_jobs {category: "internship", remote_only: true, skill: "data science"}` → `No matching jobs found.` | Passed. Complete truthful no-match response. |
| 3. CS event next month | 59.82 s | `search_events {date_from: "2026-11-01", date_to: "2026-11-30", eligibility: "computer science"}` → `No matching events found.` | Passed. Complete truthful no-match response. |
| 4. Follow-up refinement | 131.51 s | Turn 1 San Jose search; turn 2 `category=internship, city=San Jose, minimum_salary=100000`; conversation grew from 5 to 9 messages | Passed for live context/tool behavior. The captured model prose was truncated; the bounded retrieved-row formatter was then validated on the scenario-1 rerun and is the current final-answer safeguard. |
| 5. Absent company | 47.11 s | Recovered truncated content request as `search_jobs {keyword: "jobs at DefinitelyNotInSeedData", city: "DefinitelyNotInSeedData"}` → no match | Passed. Complete truthful no-match response. |

The final repair also fixed a recovered optional numeric value of `"None"` and normalizes ambiguous event eligibility when the user explicitly requests computer science. Positive-result final prose is bounded: if Ollama stops mid-list, the assistant summarizes only records already returned by the database tool.
