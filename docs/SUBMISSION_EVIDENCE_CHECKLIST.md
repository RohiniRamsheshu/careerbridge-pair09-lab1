# Lab 2 Submission Evidence Checklist

This checklist records evidence that exists, evidence that remains incomplete, and the exact commands or manual actions needed to close gaps. It does not claim evidence that was not captured.

## Existing evidence

- Backend regression suite: 87 passed with `py -3.12 -m pytest -q backend/tests`.
- Frontend suite: 21 passed with `npm test -- --run`.
- Production build: passed with `npm run build`.
- Lint: completed with the existing `CompanyPage.jsx` warning.
- Batch 7 CRUD JMeter results at 100, 200, 300, 400 and 500 users are under `performance/results/`.
- Batch 7 assistant JMeter results at 5, 10, 20 and 50 users are under `performance/results/`.
- Sanitized 50-request trace analysis is under `performance/results/trace-50-summary.json` and `trace-50-sanitized.json`.
- Real Ollama transcript before the fix is under `performance/results/ollama-transcript-sanitized.json` and documents the failed fabricated response.
- Real Ollama transcript after the fix is under `performance/results/ollama-batch8-sanitized.json` and documents the blocked unsupported claim.
- Kafka duplicate, worker restart and poison-message evidence is documented in `docs/KAFKA_EVIDENCE_BATCH2.md`.
- Mongo migration and memory evidence is documented in `docs/MONGODB_MIGRATION.md`, `docs/MEMORY_CONSOLIDATION_EVIDENCE.md` and `docs/ASSISTANT_MEMORY.md`.
- Deterministic harness output is in `agent_harness.json`.

## Incomplete or blocked evidence

- Browser screenshots and Redux DevTools screenshots were not captured in this execution because browser automation was unavailable.
- Assistant navigation-away-and-return persistence still needs a genuine browser demonstration.
- Company applicant, status-update, event-registrant and resume-preview browser evidence remains outstanding.
- CRUD write-load evidence for application submission and event registration was not run at 100–500 users. Existing JMeter write samplers require unique resume paths and controlled unique records; the previous read-only benchmark was kept unchanged.
- Real Ollama fallback latency remains approximately 74 seconds for the corrected request. No performance improvement is claimed.
- Per-request database and Kafka queue timing fields are unavailable in the current telemetry, so the 50-request trace analysis cannot identify those components separately.
- Sessions and activity-log migration categories remain blocked by absent source tables in the Lab 1 schema.
- Independent six-service deployment, Kubernetes and AWS evidence remain incomplete.

## Reproduction commands

Run from the repository root with the isolated environment variables configured locally:

```powershell
$env:PYTHONPATH='.'
py -3.12 -m pytest -q backend/tests
py -3.12 -m compileall -q backend performance/tools
docker compose -f docker-compose.yml -f performance/docker-compose.batch7.yml -p p09-performance-batch7 ps
```

Frontend checks:

```powershell
cd frontend
npm test -- --run
npm run build
npm run lint
```

The real Ollama evidence request must use a disposable synthetic student account and must not print its token or credentials. The live Batch 8 verification used the isolated backend at port `19090` and recorded only sanitized response/metric fields.

## Required manual capture before submission

1. Student login, dashboard, job search, application, event registration and saved-item screenshots.
2. Assistant conversation, confirmation proposal, decline and navigation persistence screenshots.
3. Company dashboard, applicant profile/resume preview, event registrants and status-update screenshots.
4. Redux DevTools screenshots for the assistant conversation slice and one additional meaningful slice.
5. Kafka terminal demonstrations with event IDs, offsets, deduplication and DLQ output.
6. Mongo migration counts, memory consolidation before/after counts and `/memory` output.
7. Required partner recording, viva walkthrough and final report artifacts specified by the professor PDF.

## Lab 1 seed restoration evidence

- Restoration report: `docs/LAB1_SEED_RESTORATION_REPORT.md`.
- Seed-source and recovery audit: `docs/LAB1_SEED_DATA_AUDIT.md`.
- Verified pre-restoration Batch 7 logical backup is outside the repository at:
  `C:\Users\Bhushan Waingankar\AppData\Local\Temp\careerbridge-lab1-batch13-backup\p09-performance-batch7-handshake_lab1_local-verified.sql`.
- Backup SHA-256: `E30A82AB76F7748981067175EE3C15035957B6B2C7AF8BED57141CC2DA55A277`.
- Verified Batch 7 relational totals after restoration: 200 student profiles,
  50 company profiles, 300 jobs, 100 events, and 1,500 applications.
- Existing synthetic registrations, outbox rows, processed-event rows, Mongo
  memory, and conversations were preserved.
- Browser screenshots and visual acceptance after restoration still require
  genuine manual/browser capture; none are claimed here.
