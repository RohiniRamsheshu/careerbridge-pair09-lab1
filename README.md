# CareerBridge Pair 09 — Lab 2

Pair configuration: `PAIR=09`, `PORT_BASE=9090`, resource/Kafka prefix `p09`,
seed `09`, cities San Jose, Mountain View, and Palo Alto.

## Local checks

```powershell
.\.venv312\Scripts\python.exe -m pytest -q
cd frontend
npm test -- --run
npm run build
npm run lint
cd ..
```

## Deterministic assistant harness

```powershell
$env:PYTHONPATH='.'
py -3.12 -m backend.agent_harness
```

The machine-readable output is `agent_harness.json`; summary metrics are in
`METRICS.md`.

## Local Compose

With the disposable environment variables `DB_PASSWORD`, `DB_ROOT_PASSWORD`,
and `JWT_SECRET` configured locally, validate or start Batch 7 using:

```powershell
docker compose -f docker-compose.yml -f performance/docker-compose.batch7.yml -p p09-performance-batch7 config --quiet
docker compose -f docker-compose.yml -f performance/docker-compose.batch7.yml -p p09-performance-batch7 ps
```

This execution environment could not access the Docker Desktop Linux-engine
named pipe, so no current runtime claim is made here. Never use `down -v` or
reset the retained volumes.

## Evidence and submission

See `docs/evidence/README.md`, `docs/LAB2_REQUIREMENT_TRACEABILITY.md`,
`docs/LAB2_EXECUTION_LOG.md`, `METRICS.md`, and `RUN_LOG.txt`. Kubernetes and
AWS deployment remain deferred and require separate authorization and genuine
cloud evidence.
