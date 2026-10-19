# Development Log

## CareerBridge Pair 09 — Lab 1

### Phase 1 — Repository and Frontend Setup

- Created the shared GitHub repository and frontend branch.
- Set up the React/Vite frontend.
- Configured VS Code and Git workflows.
- Added the initial application layout and React Router routes.

### Phase 2 — Frontend Features

- Implemented the student dashboard UI.
- Implemented job search, filtering, details, save, and apply interface behavior.
- Implemented event search, filtering, details, save, and registration interface behavior.
- Implemented the student profile editing page.
- Implemented the resume upload interface.
- Implemented the company dashboard and job-posting interface.
- Implemented the assistant interface.
- Implemented the safety and prompt-injection testing page.
- Implemented login and logout navigation.

### Phase 3 — Backend Integration

- Merged the backend branch into the shared frontend branch.
- Configured the local MySQL database and loaded the schema and seed data.
- Added the frontend API service layer.
- Connected jobs to `GET /jobs`.
- Connected events to `GET /events`.
- Connected student login to `POST /auth/login`.
- Added JWT Authorization headers to protected requests.
- Connected profile updates to `PUT /student/profile`.
- Connected the student dashboard to `GET /dashboard/student`.
- Connected event registration to `POST /events/{event_id}/register`.
- Connected saved jobs and events to the saved-items endpoints.
- Connected PDF resume upload to `POST /applications/resume`.

### Phase 4 — Debugging and Verification

- Fixed duplicate JavaScript exports.
- Fixed missing API exports.
- Fixed React state-scope and misplaced JSX errors.
- Fixed JWT secret configuration and environment-variable naming.
- Verified CORS behavior between ports 5173 and 9090.
- Used Swagger UI to verify protected endpoints.
- Tested login, dashboard loading, jobs, events, profile updates, resume upload, saved items, registration, and logout.
- Completed the Vite production build successfully.

### Phase 5 — Evidence and Submission Preparation

- Captured screenshots for the GitHub branch, Swagger UI, login, dashboard, jobs, events, saved items, profile, resume upload, safety test, logout, build, and Git status.
- Added screenshots under `report/screenshots/`.
- Created the Lab 1 report with relative screenshot references.
- Prepared the five-minute presentation flow for Rohini and Shoury.

## Final Status

- Frontend branch pushed to GitHub.
- Production build completed successfully.
- Git working tree verified clean.
- Frontend and backend integration demonstrated locally.
