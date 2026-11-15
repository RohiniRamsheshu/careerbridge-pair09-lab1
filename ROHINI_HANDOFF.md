# Shoury - Lab 2 Progress Handoff

## Purpose
This branch contains Shoury's current Lab 2 implementation and supporting documentation for pair review and integration. It is a progress handoff, not a claim that the entire Lab 2 submission is complete.

## Implemented work

### Backend and assistant
- Assistant tool-loop and response-grounding improvements.
- Tool validation, bounded execution, confirmation handling and guardrails.
- Context management, token accounting and compaction support.
- MongoDB repository, migration and student-memory consolidation components.
- Assistant harness and supporting tests.

### Kafka and distributed processing
- Event contracts, producers, consumers and worker components.
- Transactional outbox and event-processing support.
- Idempotency, retries and dead-letter handling components.
- Architecture and evidence documentation.

### Frontend
- Gotham-inspired visual redesign.
- Redux Toolkit store with slices for authentication, jobs, applications, events, saved items and assistant conversation.
- Jobs and events pagination and API integration.
- Registration form wording improvements.
- Frontend tests and Docker/Nginx configuration.

### Data and performance
- Lab 1 seed-data restoration documentation and audit.
- JMeter CRUD and assistant test plans.
- Performance summaries, graphs and selected sanitized traces.
- Performance analysis scripts and documentation.

## Verification recorded so far
- Backend test suite previously reported 87 passing tests.
- Frontend test suite previously reported 23 passing tests.
- Frontend production build passed.
- Focused backend tests and local API checks passed.
- Batch 7 local Docker environment and restored seed-data counts were verified.

These are previously recorded results; rerun the tests in the current checkout before treating them as a fresh verification.

## Remaining work / evidence
- Manual browser acceptance and screenshots.
- Redux DevTools screenshots and conversation route-persistence evidence.
- Final review of all six Redux slices and end-to-end flows.
- Complete CRUD write-load benchmark and database/Kafka timing isolation.
- Kubernetes manifests, cluster validation and AWS ECR/EKS deployment.
- Final report, pair verification and demo recordings.
- Confirm the final integration with Rohini's latest frontend branch.

## Important integration note
This branch is a separate progress handoff. It has not been merged into Rohini's frontend branch. Review and integrate changes carefully; do not overwrite either partner's work.

## Local environment
The Batch 7 disposable environment uses frontend port 15173 and backend port 19090. Batch 3 uses separate ports and should remain untouched.

## Pair parameters
Pair 09; prefix p09; PORT_BASE 9090; seed 09.
