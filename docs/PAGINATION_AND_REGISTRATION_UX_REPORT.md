# Pagination and Registration UX Report

## Scope

Batch 15 adds filtered total metadata and user-facing pagination for Jobs and Events, while preserving the legacy list response shape and the existing registration API contract. No database writes, reseeding, migrations, resets, or volume changes were performed for this work.

## Root cause

The Jobs and Events pages used the number of rows returned for the current page as the result count. Because the API default page size is 50, the Jobs page displayed `50 opportunities found` even when more records matched. The pages also requested only the first page and had no previous/next controls.

The backend previously returned arrays only, so the frontend had no efficient way to know the filtered total without downloading every record. The fix adds an opt-in `include_total=true` response envelope containing `items`, `total`, `limit`, and `offset`. Calls without this flag still return the original array response.

The earlier Events `100/0` observation is consistent with a 100-row result set queried at `offset=100`: the total is 100 and the second page is empty. It is not evidence that the first page contained only zero events.

## Implemented behavior

- Jobs and Events request filtered totals from the backend and render `Showing start–end of N` plus `Page X of Y`.
- Previous/Next preserve the active filters and search query.
- Changing a filter or search resets the page to page 1.
- Empty results render a zero range and the existing empty state.
- Backend filter-count queries reuse the same predicates as the item query; page size is never used as the total.
- A request sequence guard prevents an older response from replacing newer filter results.
- The old array response remains available for existing API clients.
- Pagination and registration controls retain the existing Gotham styling and receive consistent responsive spacing.

## Read-only live totals observed

These values were queried from the running Batch 7 backend at `http://localhost:19090` using `include_total=true` and `limit=1`; no records were written.

| Query | Total matches |
|---|---:|
| Jobs, all locations | 300 |
| Jobs, San Jose | 107 |
| Jobs, Mountain View | 90 |
| Jobs, Palo Alto | 103 |
| Jobs, full time | 95 |
| Jobs, part time | 66 |
| Jobs, on campus | 65 |
| Jobs, internship | 74 |
| Jobs, remote | 148 |
| Jobs, on-site | 152 |
| Jobs, San Jose + internship + remote | 12 |
| Events, all locations | 100 |
| Events, San Jose | 32 |
| Events, Mountain View | 42 |
| Events, Palo Alto | 26 |

The all-location totals match the restored Lab 1 counts previously verified for Batch 7: 300 jobs and 100 events.

## Company registration decision

The backend `RegisterRequest` requires `name` for both roles. Company registration also requires `company_name` and `location`, while student registration requires `college`. The API field was therefore preserved for compatibility and the company label now reads **Contact person's full name**, with helper text explaining that it identifies the company representative. The student label remains **Student's full name**.

The existing role-conditional payload behavior is preserved: student submissions send student-specific fields, and company submissions send company name/location. Irrelevant fields are not included in the selected role's request. Company authentication and stored profile behavior are unchanged.

## Files changed

- `backend/app/main.py` — optional filtered count envelopes for `/jobs` and `/events`.
- `backend/tests/test_read_routes.py` — backend count metadata and filter-preservation tests.
- `frontend/src/services/api.js` — optional pagination and total-metadata query parameters.
- `frontend/src/store/slices.js` — paginated jobs/events thunk handling while retaining array compatibility.
- `frontend/src/pages/JobsPage.jsx` — accurate totals, ranges, pagination, page reset, and stale-response protection.
- `frontend/src/pages/EventsPage.jsx` — equivalent event behavior.
- `frontend/src/pages/RegisterPage.jsx` — role-specific company/student naming labels and company helper text.
- `frontend/src/services/api.test.js` — API query mapping regression tests.
- `frontend/src/App.css` — pagination and registration helper styling.

## Verification

- Focused backend route tests: **23 passed** (`py -3.12 -m pytest -q backend/tests/test_read_routes.py`).
- Full backend suite: **87 passed; 2 setup errors**. The two resume tests could not create pytest temp directories because Windows returned `WinError 5` while scanning `C:\Users\Bhushan Waingankar\AppData\Local\Temp\pytest-of-Bhushan Waingankar`; no test assertion ran for those two cases.
- Python compilation: passed (`py -3.12 -m compileall -q backend`).
- Frontend tests: **23 passed across 4 files** (`npm test -- --run`).
- Frontend production build: passed (`npm run build`, Vite 8.3.4).
- Frontend lint: exit 0 with three `react(set-state-in-effect)` warnings: the existing CompanyPage warning and the new page-reset effects in JobsPage and EventsPage. These do not fail lint.
- `git diff --check`: passed; only line-ending conversion notices were emitted.
- Batch 7 live services: backend and frontend containers were healthy during verification; `/health`, `/health/database`, and the new metadata requests returned HTTP 200.
- Legacy compatibility: live `/jobs?limit=1` returned an array, and `/events?limit=1&offset=100` returned an empty array as expected for the page after 100 events.

## Remaining limitations

- Browser-level visual verification was not performed in this execution.
- The final CSS-only frontend container rebuild was not performed because the current shell does not have the disposable Compose secret variables required to interpolate the full Compose file. No credentials were printed or reconstructed. The source production build is green, and the running frontend container remains healthy with the prior Batch 15 application bundle.
- The existing three lint warnings remain; no unrelated refactor was made to remove them.
- The two resume tests require a repaired pytest temp-directory ACL/environment before they can be rerun.

## Data and safety confirmation

The restored Batch 7 MySQL data and existing disposable volumes were not modified. Batch 3 was not accessed for writes. No commit, push, merge, tag, reset, rebase, seed, migration, or destructive database operation was performed.
