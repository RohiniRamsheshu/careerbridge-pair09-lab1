# AI Use Disclosure

## Project

CareerBridge Pair 09 — Lab 1

## AI Tool Used

ChatGPT/Codex was used as an assistance and guidance tool during development.

## How AI Assistance Was Used

AI assistance was used for:

- Explaining GitHub repository and branch workflows
- Explaining VS Code and terminal setup
- Guiding React/Vite project setup
- Suggesting React routing and component structure
- Helping debug Vite, React, and JavaScript errors
- Suggesting frontend API-service functions for REST requests
- Explaining JWT authentication and Authorization headers
- Guiding FastAPI, MySQL, CORS, and environment-variable troubleshooting
- Helping connect the frontend to jobs, events, dashboard, profile, saved-item, event-registration, and resume-upload endpoints
- Suggesting testing steps for login, profile updates, saving items, event registration, logout, and production builds
- Organizing screenshots and drafting report documentation
- Preparing the five-minute demonstration script

## Human Contributions and Verification

Rohini and Shoury made the final implementation decisions, entered and reviewed the code, ran the application locally, tested the API endpoints, verified the UI behavior, captured screenshots, committed the work, and pushed the final changes to GitHub.

AI-generated suggestions were reviewed and adapted to the project. The team did not rely on AI output without testing it. Errors were identified through the terminal, browser console, Vite build output, Swagger UI, and manual user-flow testing.

## Testing Performed

- React/Vite production build
- Student login with JWT authentication
- Protected student dashboard request
- Jobs API retrieval
- Events API retrieval
- Saved jobs and saved events
- Event registration
- Student profile update
- PDF resume upload
- Logout and login redirect
- Prompt-injection filtering demonstration
- Git status and GitHub push verification

## Data and Privacy

No passwords, JWT tokens, database credentials, or `.env` files were intentionally included in the repository or report. Test credentials were used only for local verification.

## Limitations

The backend exposed a resume-upload endpoint, but a separate job-application creation endpoint was not available during frontend integration. Company API operations may require additional backend endpoint schemas.
