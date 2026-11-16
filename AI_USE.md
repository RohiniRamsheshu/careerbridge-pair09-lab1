# AI Use Disclosure — Pair 09 Lab 2

AI assistance was used during development and verification for code inspection,
debugging, targeted implementation, test creation, documentation, and evidence
organization. Human contributors remain responsible for reviewing the code,
running the application, interpreting the professor rubric, and presenting the
architecture and selected implementation during the viva.

## Incorrect output and correction

An earlier real assistant transcript produced an unsupported generic offer even
though no database-backed offer existed. The issue was detected by comparing the
assistant response with the actual tool results. The production agent was then
updated with grounding checks and regression coverage so unsupported job/event
claims are rejected or clarified. The sanitized before/after records are under
`performance/results/ollama-transcript-sanitized.json` and
`performance/results/ollama-batch8-sanitized.json`.

## Verification boundary

The deterministic harness uses production guardrail, validation,
authorization, confirmation, and tool-execution modules. It supplements rather
than replaces real Ollama evidence. No credentials, API keys, passwords, or
private connection strings are included in this disclosure.
