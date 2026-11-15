# Restored Data Visibility Report

Date: 2026-11-14  
Environment: `p09-performance-batch7`  
Frontend: `http://localhost:15173`  
Backend: `http://localhost:19090`  
Branch: `feature/gotham-premium-redesign`  
HEAD: `2a5dd788f4f83029e6202d8e893455f77aeeae01`

## Root cause

The Batch 7 frontend image was built with the default Vite API URL
`http://localhost:9090`. The Batch 7 Compose override changed the published
frontend port to 15173 and backend port to 19090, but did not override the
frontend build argument. The running browser therefore called port 9090, which
belongs to the preserved Batch 3 backend.

Read-only comparison proved the mismatch:

| Backend URL | Jobs page 1 | Events page 1 | Representative data |
|---|---:|---:|---|
| `http://localhost:19090` | 100 with `limit=100` | 100 with `limit=100` | `Seed Job 0224`, `Seed Career Event 0036` |
| `http://localhost:9090` | 2 with `limit=100` | 2 with `limit=100` | `Closeout Migration Internship`, `Mongo Migration Career Event` |

The running Batch 7 frontend bundle directly contained
`http://localhost:9090`, confirming this was a build-time configuration issue,
not a database visibility or “All locations” filter issue.

## Changes made

### `performance/docker-compose.batch7.yml`

Added the Batch 7-specific Vite build argument:

```yaml
frontend:
  build:
    args:
      VITE_API_URL: ${VITE_API_URL:-http://localhost:19090}
```

The base Compose default remains port 9090 for the Batch 3/base environment.
No backend route, schema, authentication, authorization, or database code was
changed.

### Pagination correction

The frontend was also requesting only `limit=50&offset=0` and had no controls
to reach later pages. The backend already supports `limit` and `offset`, so the
smallest compatible correction was made in:

- `frontend/src/services/api.js`
- `frontend/src/store/slices.js`
- `frontend/src/pages/JobsPage.jsx`
- `frontend/src/pages/EventsPage.jsx`
- `frontend/src/services/api.test.js`

Jobs and Events now preserve supported server filters, request the current
50-record page, and expose Previous/Next controls. Page size was not increased
to conceal pagination.

## Runtime verification

The frontend image was rebuilt and only the Batch 7 frontend container was
force-recreated. The bundle now contains `http://localhost:19090`, the
container is healthy, and `http://localhost:15173` returns HTTP 200.

Read-only API verification against Batch 7:

- Jobs: page 1 = 50, page 2 = 50 using `limit=50` and offsets 0/50.
- Events: page 1 = 50, page 2 = 50 using `limit=50` and offsets 0/50.
- Seeded jobs were present on page 2.
- Seeded events were present on page 2.
- The restored database remains the source of the results; no synthetic
  fallback data was added.

The earlier full-size API checks also returned 300 jobs and 100 events through
Batch 7.

## Tests and checks

- Frontend tests: 22 passed across 4 test files.
- Production build: passed.
- Lint: exit code 0. Existing React effect warnings remain in
  `JobsPage.jsx`, `EventsPage.jsx`, and `CompanyPage.jsx`.
- `git diff --check`: passed; Git emitted existing LF/CRLF normalization warnings.
- Backend tests were not rerun because no backend source or contract changed in
  this fix.
- Browser automation was not available, so no browser-level visual claim or
  screenshot is made.

## Before/after behavior

Before, the Batch 7 frontend showed two Batch 3 synthetic jobs/events because
its compiled API URL pointed to port 9090. After the rebuild, it targets port
19090 and can navigate through the restored Batch 7 pages. The first page shows
50 records and later pages expose the remainder through supported offsets.

## Remaining limitations

- A real browser session should still be opened manually to confirm the rendered
  cards and pagination controls in the professor’s presentation browser.
- The backend does not expose a total-count field, so the UI disables Next when
  the returned page contains fewer than 50 records rather than displaying an
  exact total.
- The known CompanyPage effect lint warning remains unchanged.
- Batch 3 was not modified.
