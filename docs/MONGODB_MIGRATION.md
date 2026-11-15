# MongoDB migration and ownership

## Scope

MongoDB is the document-oriented layer for migrated records, assistant memory, and
conversation persistence. MySQL remains the authoritative transactional system for
the existing Lab 1 API, authentication, jobs, applications, events, registrations,
and saved-item writes. The migration is additive and does not alter the retained
`handshake_lab1` database.

## Mapping and safety

`backend/app/mongo_migration.py` maps stable source IDs (`<table>:<id>`) into:

| MySQL source | Mongo collection |
|---|---|
| student users | `student_accounts` |
| `student_profiles` | `student_profiles` |
| `student_preferences` | `preferences` |
| company users/profiles | `companies` |
| `jobs` | `jobs` |
| `applications` | `applications` |
| application resume paths | `resumes` metadata-only records |
| `events` | `events` |
| `event_registrations` | `registrations` |
| `saved_items` | `saved_items` |

The migration uses `replace_one(..., upsert=True)`, JSON-safe date/time/decimal
conversion, per-table counts, error collection, and repeatable execution. Resume
bytes are not copied; existing path authorization remains a MySQL/API concern.
Bcrypt hashes are copied as opaque strings and are never printed or converted to
plaintext.

The Lab 1 schema has no `sessions` or `activity_logs` source tables. The migration
reports those categories explicitly as missing rather than claiming coverage.
Session expiration is represented by a TTL index on `sessions` when a source is
available, but live session migration is not verified in this repository state.

## Commands

Use a disposable Compose project and local-only credentials:

```powershell
$env:DB_PASSWORD='...'; $env:DB_ROOT_PASSWORD='...'; $env:JWT_SECRET='...'
docker compose -p p09-mongo-batch3 up --build -d
docker compose -p p09-mongo-batch3 exec -T backend python -m backend.app.mongo_migration
```

Do not run this against the retained project database. The migration CLI emits
JSON counts and errors; rerunning it should preserve collection cardinality through
stable upserts.

## Verification recorded 2026-11-13

In disposable project `p09-mongo-batch3`, synthetic records were created through
the real API, then migration was run twice before adding the `/memory` demo student.
Those two runs reported:

```text
users=2, student_profiles=1, company_profiles=1, jobs=1, events=1,
applications=0, event_registrations=0, saved_items=0, errors=0
missing_source_tables=[sessions, activity_logs]
```

Sanitized Mongo inspection showed `password_hash_preserved=true` (only a boolean
check was printed). After adding the synthetic closeout fixture, the final migration
reported users=5, student_profiles=3, company_profiles=2, jobs=2, applications=1,
events=2, event_registrations=1, saved_items=2, and resumes_metadata=1 with zero
errors. The rerun produced the same counts; Mongo showed zero duplicate source IDs
and one metadata-only resume document. Sessions and activity logs remain absent from
the source schema.
