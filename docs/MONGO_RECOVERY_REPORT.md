# Batch 11 MongoDB Recovery Report

## Root cause

The Batch 7 Mongo container was running and locally healthy but had no network attachments. Backend, worker and the other Batch 7 services were attached to `p09-performance-batch7_default`; the Mongo container had `networks={}`. Its host binding also conflicted with Batch 3, which already owns host port `27017`.

Consequences:

- `mongo` DNS/TCP selection from the backend failed.
- `MongoRepository` timed out selecting a server.
- Authenticated `/memory` returned the environment-unavailable response.

## Repair

The Batch 7 override now removes only Batch 7's host port publication for Mongo. Batch 3 retains host port `27017`; Batch 7 uses internal Compose DNS (`mongodb://mongo:27017`). The Batch 7 Mongo service was recreated with the existing named volume `p09-performance-batch7_p09-mongo-data`. No volume, database or record was deleted or reset.

## Verification

- Mongo container network: `p09-performance-batch7_default`, alias `mongo`.
- Mongo host port binding: none for Batch 7.
- Backend-side read-only ping: `{'ok': 1.0}`.
- Mongo health: healthy after startup.
- Worker subscription includes `p09.memory.updated` and `p09.memory.consolidate`.
- Synthetic memory event was published to `p09.memory.consolidate` with a trace ID.
- Owning student `/memory`: marker visible.
- Second synthetic student `/memory`: first student's marker not visible; response reported no stored memory.

## Limitations

The repair was runtime/configuration-only. The original Batch 3 Mongo environment and its volume were not touched. Mongo migration completeness and long-running consolidation evidence remain governed by the existing Lab 2 documents.
