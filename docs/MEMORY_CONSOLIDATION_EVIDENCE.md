# Memory consolidation evidence

This document records only executions actually performed in the disposable
`p09-mongo-batch3` environment.

## Reproducible command

```powershell
docker compose -p p09-mongo-batch3 exec -T -e KAFKA_ENABLED=0 backend python -c "from backend.app.mongo_repository import MongoRepository; from backend.app.memory_consolidation import seed_synthetic_memories, consolidate_student; r=MongoRepository(); r.ensure_indexes(); seed_synthetic_memories(r, 9003, 60); print(consolidate_student(r, 9003))"
```

## Result

The run returned `before=60`, `after=30`, and `30` decisions. The fixture uses 30
memory keys, duplicate entries, and contradictory values. The deterministic winner
rule is, in order: confidence, source priority (`user` > `profile` > `inferred` >
`synthetic`), then recency. Losers are marked inactive with `consolidated_into`,
`consolidated_at`, and retained provenance rather than physically deleted.

One observed decision kept the higher-ranked entry for `synthetic.fact.3` and
merged the other entry because the rule compared confidence/source/recency. This
is intentionally deterministic; an incorrect source or confidence value could
still cause an incorrect winner, so provenance and inactive history remain
available for review. No LLM is required for correctness.

## Asynchronous path

A synthetic `student_memory` update was published with Kafka enabled. After the
worker processed it, the worker log contained a `p09.memory.consolidate` publish
for aggregate `9003`; Mongo showed 30 active and 31 consolidated/inactive records.
This verifies the worker path in the disposable stack, but not cross-database
transactional durability. The current limitation is documented in
`docs/ASSISTANT_MEMORY.md`.

## Test status

`backend/tests/test_mongo_memory.py` covers the 60-entry reduction, merge decision
creation, password/date/time/decimal migration conversion, and student-scoped
memory retrieval using isolated fakes. Full backend verification after this batch:
`83 passed in 3.05s`.
