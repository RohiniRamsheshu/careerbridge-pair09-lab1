# CareerBridge Pair 09 — Lab 1 Report

## Team

- Rohini Ramasheshu — Frontend implementation and API integration
- Shoury — FastAPI backend, MySQL database, authentication, and seed data

## 1. Project Objective

CareerBridge is a career platform for students and employers in the Pair 09 region. Students can discover jobs, explore events, manage profiles, upload resumes, save opportunities, and register for events in San Jose, Mountain View, and Palo Alto.

## 2. Technology Stack

- React and Vite
- React Router
- FastAPI
- MySQL
- JWT authentication
- REST APIs
- Git and GitHub

## 3. Rohini’s Contributions

Rohini implemented the React frontend, routing, student dashboard, jobs and events pages, profile editing, resume upload, login and logout, JWT integration, saved jobs and events, event registration, safety testing, API integration, production build verification, GitHub collaboration, and evidence collection.

## 4. Project Setup and Collaboration

The project was developed in a shared GitHub repository using the `rohini-frontend` branch.

![GitHub branch](screenshots/01-github-branch.png)

Figure 1: Shared GitHub repository and frontend branch.

## 5. Backend Verification

The FastAPI backend was verified through Swagger UI.

![Swagger UI](screenshots/02-backend-swagger.png)

Figure 2: FastAPI Swagger documentation.

## 6. Student Authentication

The frontend connects to `POST /auth/login`. After successful login, the backend returns a JWT access token. The frontend stores the token and sends it with protected API requests.

![Student login](screenshots/03-student-login.png)

Figure 3: Student login page.

## 7. Student Dashboard

The dashboard retrieves data from `GET /dashboard/student` and displays application and saved-item counts.

![Student dashboard](screenshots/04-student-dashboard-api.png)

Figure 4: Student dashboard using backend data.

## 8. Jobs

The Jobs page retrieves data from `GET /jobs` and supports search, filtering, job details, saving jobs, removing saved jobs, and saved-job persistence after refresh.

![Jobs API results](screenshots/05-jobs-api-results.png)

Figure 5: Jobs loaded from the backend.

![Save job confirmation](screenshots/06-save-job-confirmation.png)

Figure 6: Save job confirmation dialog.

![Remove job confirmation](screenshots/06.1-remove-job-confirmation.png)

Figure 7: Remove saved job confirmation.

![Saved job persisted](screenshots/07-saved-job-persisted.png)

Figure 8: Saved job remains after refreshing the page.

## 9. Events

The Events page retrieves data from `GET /events` and supports search, filtering, event details, event registration, saving events, and saved-event persistence.

![Events API results](screenshots/08-events-api-results.png)

Figure 9: Events loaded from the backend.

![Event registration](screenshots/09-event-registration-success.png)

Figure 10: Successful event registration.

![Saved event persisted](screenshots/10-save-event-persisted.png)

Figure 11: Saved event remains after refreshing the page.

## 10. Student Profile

The profile page updates student information through `PUT /student/profile`.

![Profile update](screenshots/11-profile-update-success.png)

Figure 12: Successful profile update.

## 11. Resume Upload

The resume upload feature sends PDF files through `POST /applications/resume` using multipart form data.

![Resume upload](screenshots/12-resume-upload-success.png)

Figure 13: Successful resume upload.

## 12. Safety and Prompt-Injection Defense

Job and event descriptions are treated as untrusted content. Prompt-injection instructions are detected and filtered.

![Prompt-injection defense](screenshots/13-safety-prompt-injection-defense.png)

Figure 14: Prompt-injection content detected and filtered.

## 13. Logout

The logout function clears the JWT token and redirects the user to the login page.

![Logout redirect](screenshots/14-logout-redirect.png)

Figure 15: Logout redirect to the login page.

## 14. Testing and Verification

The following features were tested: student login, JWT storage, protected profile update, jobs retrieval, events retrieval, event registration, saved jobs, saved events, resume upload, dashboard API data, logout, and prompt-injection handling.

## 15. Production Build and Git Verification

The frontend production build completed successfully using `npm run build`.

![Production build](screenshots/15-production-build.png)

Figure 16: Successful Vite production build.

The Git working tree was verified as clean.

![Clean Git status](screenshots/16-clean-git-status.png)

Figure 17: Clean Git status after pushing the project.

## 16. Limitations

The backend currently provides a resume-upload endpoint, but a separate job-application creation endpoint was not available in Swagger. Company API operations and job application submission may require additional backend endpoints or request schemas.

## 17. Conclusion

The CareerBridge frontend was implemented and integrated with the FastAPI backend. The completed features include authentication, dashboard data, job and event retrieval, saved items, event registration, profile updates, resume upload, logout, and prompt-injection protection. The project was successfully built and pushed to the shared GitHub repository.
