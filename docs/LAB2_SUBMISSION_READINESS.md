# Lab 2 Submission Readiness

## Current conclusion

**Not ready for final submission yet.** The repository has meaningful local
implementation and evidence, but the professor's required cloud/Kubernetes
evidence, genuine browser/Redux DevTools screenshots, fresh runtime Kafka
failure capture, and complete CRUD write-load evidence are still incomplete or
blocked. Final local code regression is green.

## Strong evidence currently available

- Backend: 102 passed, one Starlette/httpx deprecation warning.
- Frontend: 24 passed; production build passed.
- Lint exits 0 with three known React effect warnings.
- Python compilation and `git diff --check` passed.
- Deterministic production-module assistant harness: 10/10 passed.
- Prior sanitized Kafka duplicate, worker restart, and poison/DLQ evidence.
- Prior Mongo migration and 60-to-30 consolidation evidence.
- JMeter raw results, summaries, and graphs for recorded workloads.
- Sanitized real Ollama transcripts with the unsupported-claim correction documented.

## Blocking or missing rubric evidence

1. Current Docker runtime verification is blocked by Docker Desktop named-pipe
   permission in this Codex context.
2. Six route-boundary Dockerfiles and Kubernetes preparation manifests now
   exist, but they have not been built/applied in this execution context and
   still reuse the modular FastAPI monolith and shared persistence.
3. AWS ECR/EKS deployment and screenshots are intentionally deferred; local
   build/deploy preparation scripts are present under `scripts/`.
4. Browser screenshots and Redux DevTools screenshots are not captured.
5. Application-submission/event-registration write-load runs at all required
   CRUD levels are not evidenced.
6. The trace artifacts do not separately measure every database and queue stage.
7. The professor-required pair recording and both-partner viva preparation remain
   human deliverables.

## Safe next actions

Use the existing Batch 7 PowerShell environment to capture current health,
Kafka, Mongo, browser, and Redux evidence without resetting volumes. Then close
only the write-load and report gaps that can be demonstrated safely. Defer AWS
until credentials, cost, and deployment approval are explicitly available.
