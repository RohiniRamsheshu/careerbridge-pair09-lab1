# Manual Browser Evidence Guide

Use the rebuilt isolated frontend at `http://127.0.0.1:15173`. Use only synthetic accounts and redact email addresses, tokens and personal data from screenshots.

## Student evidence

1. Log in as a synthetic student and capture the landing dashboard.
2. Open Jobs, search San Jose, open a detail view, and capture the result.
3. Submit one application using a synthetic PDF; capture the success state and My Applications history.
4. Open Events, register for one synthetic event, and capture registration history.
5. Save a job and event, refresh, and capture Saved Items.
6. Open Assistant, perform a read-only search and a city follow-up.
7. Request a save, capture the proposal, then capture both Decline and a separate approved synthetic save. Verify the UI never claims success before approval.
8. Navigate away from Assistant and return; capture conversation persistence. Do not claim refresh persistence unless separately observed.
9. Open Redux DevTools and capture the assistant conversation slice plus applications or auth state and its actions.

## Company evidence

1. Log in as a synthetic company and capture the distinct Dashboard and Company routes.
2. Create/manage a synthetic job and event.
3. Open applicants, applicant profile and authorized resume preview.
4. Update an application status and capture the result.
5. Open event registrants and capture the authorized profile view.

## Responsive evidence

Capture the dashboard, Jobs and Assistant at desktop, tablet and mobile widths. Check for horizontal overflow, clipped navigation, unreadable text, inaccessible controls and missing focus indicators.

## Safety

Do not include passwords, bearer tokens, real student/company information, filesystem paths or private Mongo/MySQL details in screenshots.
