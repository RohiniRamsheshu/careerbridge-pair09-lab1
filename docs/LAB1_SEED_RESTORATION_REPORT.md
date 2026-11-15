# Lab 1 Seed Restoration Report

Date: 2026-11-14  
Environment: `p09-performance-batch7`  
Branch: `feature/gotham-premium-redesign`  
HEAD: `2a5dd788f4f83029e6202d8e893455f77aeeae01`

## Scope and safety

The original Lab 1 workspace and Batch 3 environment were not modified. No Git
history operation, AWS operation, volume deletion, schema destruction, or
database reset was performed. Restoration was limited to the disposable Batch
7 MySQL database and its existing Lab 2 Mongo database through the existing
additive migration.

## Source and compatibility

Source: `C:\Users\Bhushan Waingankar\Desktop\handshake-lab1\seed_data.py`.

The source imports only Python standard-library modules, `bcrypt`, and the
existing database connection helper. It does not call `DROP`, `TRUNCATE`, or
`DELETE`; it computes missing counts and inserts rows. It uses auto-increment
IDs, foreign-key-safe insertion order, bcrypt hashes, Pair 09 seed value 9,
and the three required cities. It creates student/company accounts with the
generated password documented in the local source, but that credential was not
printed or included in this report.

The current schema is backward-compatible with all source insert columns. Lab 2
adds `event_outbox` and `processed_events`; the seed source does not touch those
tables. Existing synthetic records therefore remain in place and their IDs are
not reused.

Before active restoration, the source was run against a fresh staging database
using the current schema. It produced exactly 200 students, 50 companies, 300
jobs, 100 events, and 1,500 applications.

## Backup verification

Verified backup:

`C:\Users\Bhushan Waingankar\AppData\Local\Temp\careerbridge-lab1-batch13-backup\p09-performance-batch7-handshake_lab1_local-verified.sql`

- Size: 23,480 bytes
- SHA-256: `E30A82AB76F7748981067175EE3C15035957B6B2C7AF8BED57141CC2DA55A277`
- Dump exit code: 0
- Method: single-transaction, quick, no-tablespaces logical dump
- Coverage: all 12 Batch 7 MySQL tables

## Restoration results

| Table | Before | After |
|---|---:|---:|
| `student_profiles` | 5 | 200 |
| `company_profiles` | 3 | 50 |
| `jobs` | 2 | 300 |
| `events` | 2 | 100 |
| `applications` | 2 | 1,500 |
| `event_registrations` | 2 | 2 |
| `saved_items` | 0 | 0 |
| `event_outbox` | 8 | 8 |
| `processed_events` | 10 | 10 |

Imported records were additive. No records were skipped for schema or foreign
key errors. Existing synthetic records remained present. A second generator run
left all target totals unchanged.

Because the original generator writes directly to MySQL, the restored historical
rows do not have corresponding Kafka outbox events. This is intentional: the
restore did not fabricate historical business events. New application/job/event
operations continue to use the existing Lab 2 outbox path.

## Mongo migration results

The existing migration command was run twice after restoration:

```powershell
docker exec p09-performance-batch7-backend-1 python -m backend.app.mongo_migration
```

Both runs returned zero errors and identical source counts: 250 users, 200
student profiles, 50 company profiles, 300 jobs, 1,500 applications, 100
events, 2 registrations, 0 saved items, and 1,500 resume metadata documents.
The migration reported missing source categories `sessions` and
`activity_logs`, matching the existing Lab 1 schema limitation.

Mongo memory and conversation documents remained present. Collections were not
cleared. Resume files were not copied; only metadata/path records were migrated,
consistent with the existing security design.

## Application acceptance checks

Read-only checks against Batch 7 after restoration:

- `/health` and `/health/database` returned healthy responses.
- Student and company login returned the correct roles.
- Frontend port 15173 returned HTTP 200.
- Jobs paged at 100/100/100, confirming 300 API-visible jobs.
- Events paged at 100/0, confirming 100 API-visible events.
- San Jose job and event searches returned seeded records.
- Authenticated student application history returned records.

Browser screenshots, company-management UI actions, event registration writes,
saved-item writes, and live assistant write flows were not performed as part of
this restoration verification.

## Rollback

Do not roll back in place casually. Preserve both the pre-restoration dump above
and a new post-restoration dump if rollback becomes necessary. The safest
rollback is to create a separate disposable MySQL project/volume, load the
pre-restoration dump there, validate health/counts, and point a separate backend
and frontend at it. Any in-place rollback requires explicit approval and a
controlled write freeze.

## Remaining gaps

- Original sessions and activity logs cannot be migrated because their source
  tables do not exist.
- Historical seed rows do not emit Kafka events; only future writes do.
- Browser-level acceptance and screenshot evidence remain outstanding.
- No AWS/Kubernetes operation was performed.

## Operational note

During staging setup, an early shell-quoting mistake created an empty database
named `$stagingDb` inside the Batch 7 MySQL container. Read-only inspection
confirmed it has zero tables and no records. It was not used by the application,
was not dropped because this batch prohibits destructive cleanup, and remains a
known disposable-environment cleanup item requiring explicit approval.
