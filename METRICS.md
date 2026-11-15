# Lab 2 metrics and deterministic harness

## Deterministic harness

Run from the repository root:

```powershell
$env:PYTHONPATH='.'
python -m backend.agent_harness
```

The harness imports the production `run_assistant`, `_valid_args`, `execute_tool`,
and confirmation modules. It uses synthetic repository doubles and does not call
Ollama or write the retained database. The 2026-11-13 run produced:

```text
harness=production-agent-modules
pass_count=10
fail_count=0
```

Cases covered: read-only job/event retrieval, history follow-up, malformed
arguments, unknown tool, injected retrieved data, accepted save proposal, declined
save, one repair attempt, and iteration ceiling. The machine-readable result is
`agent_harness.json`.

## Token/context telemetry

`backend/app/ai_model.py` uses Ollama provider counters when present. If the
provider omits them, it records a clearly marked character-based estimate. The API
returns prompt/completion totals, context-window utilization, a 70% warning flag,
model/tool/repair counts, trace ID, and timing fields. The frontend displays the
utilization and whether it is estimated or provider-reported.

No real Ollama transcript or latency benchmark was run in this batch; those remain
unverified and must not be inferred from the deterministic harness.

## Performance batch (2026-11-13)

JMeter plans and an actual-JTL analyzer were added under `performance/`. JMeter is not installed
in the current environment, Docker API access failed with permission denied, and no backend was
running. Consequently CRUD results at 100/200/300/400/500 users, assistant results at 5/10/20/50
users, percentile graphs, and the required 50-request trace analysis remain **not verified**.
Ollama itself was reachable at version 0.40.16, but no CareerBridge assistant request was made;
Ollama availability is not evidence of an application transcript.

Batch 7 recovery recheck found Docker Desktop processes running but the engine pipe still denied
access; Java and JMeter were absent. No benchmark values were added.

## Existing verification carried forward

- Backend: 85 tests passed.
- Frontend: 15 tests passed.
- Frontend production build passed.
- Lint passed with one pre-existing `CompanyPage.jsx` warning.
- Disposable Compose services were healthy during the Mongo verification.
## Batch 7 measured performance

Real JMeter runs completed in isolated project `p09-performance-batch7`. CRUD HTTP samples were
300/600/900/1,200/1,500 at 100/200/300/400/500 users, all with 0% HTTP errors. Assistant chat
samples were 5/10/20/50 at the required levels, all with 0% HTTP errors. Exact percentiles, raw
JTLs, summaries, and SVG graphs are under `performance/results/`.

The 50-request trace workload returned 50 successful deterministic assistant responses with
trace IDs and 50 tool calls; tokens were estimated because that route did not call Ollama. A
separate real Ollama fallback call reported provider tokens but failed accuracy by inventing an
unsupported generic offer. This failure is documented and is not counted as a pass.

## Batch 8 correctness verification

- Added grounding guards and regression coverage for unsupported model-generated offer/search claims.
- Focused assistant suite: 45 passed.
- Full backend suite: 87 passed.
- Live isolated request after rebuilding the backend: HTTP 200, safe clarification returned, provider-reported
  tokens 1,049, two model calls, approximately 74.3 seconds total. Latency remains a known limitation.
