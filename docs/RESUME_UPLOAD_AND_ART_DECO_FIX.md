# Resume Upload and Art Deco UI Fix

## Scope and safety

This change is based on the `handoff/shoury-lab2-progress` handoff at `4fc0638` and is being developed on `fix/student-resume-upload-art-deco`. Existing API contracts, authentication, company ownership checks, Kafka behavior, databases, Batch 3, and the original Lab 1 workspace were preserved. No database writes, reseeding, migrations, volume deletion, commits, pushes, or history rewrites were performed.

## Root cause

The backend already had `POST /applications/resume` and the student Profile page already had a basic file selector, so a duplicate endpoint was not needed. The workflow was still easy to miss and insufficiently robust: the control did not show selected-file metadata, had no client-side size check or upload lock, did not refresh the resume list after success, and the Jobs Apply error did not provide a direct Profile route. The endpoint validated the filename and PDF signature but did not validate the multipart MIME type. The Compose configuration also had no persistent resume-files volume, so uploaded files could disappear when the backend container was recreated.

## Backend implementation

The existing endpoint was reused and hardened:

- Student role is still required; unauthenticated and company requests remain rejected.
- `.pdf` filename, `application/pdf` MIME type, PDF `%PDF-` signature, and 5 MB maximum size are validated.
- Server-generated filenames use the authenticated student ID plus a UUID; user filenames are never used as paths.
- A failed validation or storage operation does not replace an existing resume because uploads use a new destination.
- `RESUME_DIR` is configurable through environment configuration.
- Compose now mounts `p09-resume-data` at `/app/backend/uploads/resumes`, preserving uploaded files across backend container recreation.
- Existing resume ownership and company-authorized preview checks remain unchanged.

The application API still uses the existing resume metadata/path contract because `POST /applications/{job_id}/apply` validates that the selected stored path belongs to the authenticated student. No new application endpoint or schema change was introduced.

## Frontend implementation

### Student Profile

- Added a clear **MY RESUME** section explaining that a PDF is required to apply.
- Added Upload resume / Replace resume states.
- Shows selected filename and file size.
- Shows loading, success, and failure status.
- Prevents another upload while one is in progress.
- Refreshes the resume list after successful upload.
- Keeps the native file input semantics and accessible label; accepts PDF only and communicates the 5 MB limit.

### Job application flow

When no resume is available, the Apply error now includes a direct Profile link to upload one. The backend resume requirement is not bypassed.

### Company Portal

- The Remote control is an explicitly associated checkbox inside the normal form flow, with a comfortable clickable label and keyboard focus behavior.
- The existing boolean `is_remote` API field is unchanged.
- Create job posting and Create event controls use consistent dimensions, typography, spacing, and existing primary/secondary hierarchy.
- Shared upload, checkbox, form-control, focus, disabled, and helper-text styles follow the existing Gotham palette and tokens.

## Tests and checks

- Backend full suite: **92 passed** (`py -3.12 -m pytest -q backend/tests`).
- Added backend coverage for valid student upload, unauthenticated rejection, company rejection, MIME/signature/size validation, and preservation of an existing resume after failed replacement.
- Frontend suite: **24 passed across 4 files** (`npm test -- --run`).
- Added API coverage proving resume upload uses `FormData` without manually setting `Content-Type`.
- Frontend production build: **passed** (`npm run build`, Vite 8.3.4).
- Frontend lint: **exit 0** with three `react(set-state-in-effect)` warnings in EventsPage, JobsPage, and the pre-existing CompanyPage effect. No new lint error was introduced.
- Python compilation: passed (`py -3.12 -m compileall -q backend`).
- `git diff --check`: passed; Git emitted only existing line-ending conversion notices and pytest-directory permission warnings while scanning the worktree.

## Live verification

Computer-use inspection reached the running Batch 7 Company Portal at `http://localhost:15173/company` and confirmed the company form exposes an accessible `Remote` checkbox and the existing job/event controls. A screenshot capture timed out, so no screenshot is claimed.

The complete student upload → application → company applicant workflow was not submitted live in this pass because no disposable student credentials and synthetic PDF were supplied to the browser session. The backend and frontend automated checks cover the validation and request behavior; manual/live acceptance remains required with a synthetic account and PDF.

## Remaining limitations

- Browser-level upload and application submission remain unverified in this pass.
- Existing lint warnings remain and are unrelated to the upload changes.
- Existing old resume files are retained when replacing a resume so prior application records remain valid; cleanup is intentionally not performed.
- The new persistent volume must be included when the Batch 7 Compose environment is rebuilt. No existing volume was deleted or recreated by this change.

## Manual acceptance sequence

1. Use a synthetic student account on Batch 7 (`http://localhost:15173`).
2. Open Profile → My Resume → Upload resume and select a valid PDF under 5 MB.
3. Confirm the selected filename, upload status, and current resume filename.
4. Open Jobs, view a valid job, and Apply.
5. Confirm the application appears in student history.
6. Use the owning synthetic company account to confirm the applicant and preview the PDF.
7. Open Create job posting and verify Remote toggles beside its label on desktop and mobile widths.
