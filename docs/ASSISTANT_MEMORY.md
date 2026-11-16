# Assistant memory architecture

## Collections

`backend/app/mongo_repository.py` defines the following logical collections:

- `assistant_rules`: active system-level rules. Rules are context only and cannot
  authorize a write or override application policy.
- `student_memory`: student-scoped facts/preferences with `memory_key`, value,
  kind, confidence, source, temporary flag, provenance, and timestamps.
- `conversations`: per-student, per-conversation message history, bounded to the
  latest 100 messages.

Indexes include unique rule keys, student/active and student/memory-key indexes,
and a unique `(student_user_id, conversation_id)` conversation key. A TTL index is
defined for a future `sessions` collection.

## Assistant integration

`backend/app/main.py` lazily connects to Mongo and preserves normal assistant
behavior if Mongo is unavailable. The `/assistant/chat` route scopes memory and
conversation reads by the authenticated student ID. `/memory` returns only the
current student's active memories. `backend/app/agent.py` injects relevant memory
inside explicit `<memory_context>` delimiters and tells the model that memory is
context, never authority. Retrieved descriptions, eligibility text, and memory are
not allowed to override authorization or confirmation gates.

The existing five-tool hand-built agent loop and save-confirmation workflow remain
the authority for tool execution and writes. Memory is not a substitute for live
database results.

Explicit user memory writes are supported through `POST /assistant/memory` with
`memory_key`, `value`, and optional `kind`. The endpoint requires an authenticated
student and uses that authenticated user's ID; a client-supplied student ID is
not part of the request model. Explicit natural-language phrases matching the
structured `Remember this: My <key> is <value>` form use the same repository
upsert. Ordinary conversation text does not write memory. Repeated explicit
writes for the same active student/key update the existing memory instead of
creating another active record and preserve the existing `memory.updated` Kafka
publication path.

## Kafka relationship

`student_memory` writes can publish the existing typed `memory.updated` event. The
worker consumes it and publishes `memory.consolidate`; consolidation is then run by
the worker, not by the blocking assistant request. The current Mongo write followed
by Kafka publish is best-effort rather than a cross-database transaction. This
limitation is explicit: a Mongo/Kafka outbox is not yet implemented, so the memory
event path is not claimed as lossless.

## Verification recorded 2026-11-13

- An authenticated synthetic student called `/memory` and received only its own
  stored `preferred_city: San Jose` entry.
- A 60-entry synthetic fixture consolidated to 30 active entries with 30 recorded
  merge decisions, satisfying the `<40` experiment threshold in the disposable
  Mongo volume.
- A real worker log showed publication of `p09.memory.consolidate` for the synthetic
  student after a memory update.
- Ownership and consolidation behavior have deterministic unit coverage; real
  cross-student browser coverage, rule seeding, and a full conversation round-trip
  remain additional evidence items.
