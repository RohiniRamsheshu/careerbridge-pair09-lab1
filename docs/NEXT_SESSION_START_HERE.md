# Next Session Start Here

## Workspace and safety

Work only in `C:\Users\Bhushan Waingankar\Desktop\handshake-lab1-codex`.

- Branch: `feature/gotham-premium-redesign`
- Expected HEAD: `2a5dd788f4f83029e6202d8e893455f77aeeae01`
- Original workspace: `C:\Users\Bhushan Waingankar\Desktop\handshake-lab1`
- Checkpoint branch: `backup/lab1-before-redesign`
- Independent backup: `C:\Users\Bhushan Waingankar\Desktop\handshake-lab1-codex-backup-20261112`

Before continuing, run only these read-only checks:

`git status --short --branch`, `git branch --show-current`, `git rev-parse HEAD`, and
`git diff --check`.

Preserve all modified/untracked files. Do not reset, clean, stash, commit, push, tag, merge,
rebase, or touch the original workspace.

## Current checkpoint

Verified results:

- Backend: 70 tests passed under Python 3.12.10.
- Frontend: 15 tests passed.
- Frontend production build passed.
- Backend/frontend Docker images built.
- Disposable Compose MySQL/backend/frontend health checks passed.

Implemented code includes Pair 09 configuration, Student and Application in-process service
boundaries, typed event contracts, container definitions, and a small Gotham CSS foundation.
These are not six independently deployed services.

Read these existing documents instead of repeating audits:

- `docs/ACCOUNT_HANDOVER.md`
- `docs/CODEX_EXECUTION_STATE.md`
- `docs/LAB2_BASELINE_AUDIT.md`
- `docs/LAB2_REQUIREMENT_TRACEABILITY.md`
- `docs/LAB2_SERVICE_ARCHITECTURE.md`

## Highest-priority next work

1. Add Redux safely and integrate the six required slices, including conversation persistence.
2. Extract Company, Job, Event, and AI Assistant boundaries behind existing API adapters.
3. Add a real local Kafka broker, post-commit producers, consumers, trace IDs, idempotency,
   retries, DLQ, and the three exact professor failure demonstrations.
4. Implement isolated MongoDB migration/repositories, three memory layers, `/memory`, and
   Kafka-based consolidation with 60-entry before/after evidence.
5. Implement the production-integrated agent harness, token/context telemetry, compaction,
   recall, and guardrail evidence.
6. Add reproducible JMeter plans and controlled results.
7. Add Kubernetes manifests from verified service entrypoints.
8. Continue the Gotham redesign across existing screens without changing API contracts.
9. Prepare AWS ECR/EKS scripts and restoration runbook locally only.

## Suggested regression commands

Backend: `$env:PYTHONPATH='.'; & 'C:\Users\Bhushan Waingankar\AppData\Local\Python\pythoncore-3.12-64\python.exe' -m pytest -q`

Frontend from `frontend`: `npm test -- --run`, `npm run build`, `npm run lint`.

Use elevated local execution only when the known Windows Vite `spawn EPERM` or pytest temp
directory permission issue occurs, and report that mode accurately.

## AWS approval gate

AWS work is preparation-only until explicit approval. Before cloud commands, show the planned
ECR/EKS/networking/LoadBalancer resources, permissions, approximate and ongoing costs,
authentication assumptions, and restoration steps. Never request credentials in chat and do
not modify IAM or create billable resources without approval.

## Do not repeat completed work

Do not restart the Lab 1 audit, redo the PDF reconciliation, rebuild the working backend from
scratch, or treat the 70/15 results as unverified unless code changes invalidate them. Do not
claim Kafka, MongoDB, Redux, Kubernetes, AWS, JMeter, full Gotham redesign, or six independent
services are complete without implementation and evidence.
