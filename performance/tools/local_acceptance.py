"""Run a bounded synthetic local acceptance workflow against a disposable API."""

import json
import os
import uuid
from datetime import date, timedelta

import requests


BASE = os.getenv("CB_BASE", "http://127.0.0.1:19090").rstrip("/")
STUDENT_EMAIL = os.environ["CB_STUDENT_EMAIL"]
STUDENT_PASSWORD = os.environ["CB_STUDENT_PASSWORD"]
COMPANY_PASSWORD = "Batch10-Disposable-Company-Password!"


def request(session, method, path, **kwargs):
    response = session.request(method, BASE + path, timeout=30, **kwargs)
    response.raise_for_status()
    return response.json() if response.content else {}


def authenticated(email, password):
    session = requests.Session()
    payload = request(session, "POST", "/auth/login", json={"email": email, "password": password})
    session.headers.update({"Authorization": f"Bearer {payload['access_token']}"})
    return session, payload["user"]


def main():
    student, student_user = authenticated(STUDENT_EMAIL, STUDENT_PASSWORD)
    student_checks = {
        "me": request(student, "GET", "/auth/me")["role"],
        "dashboard": request(student, "GET", "/dashboard/student").get("user_id"),
        "jobs": len(request(student, "GET", "/jobs?city=San%20Jose")),
        "events": len(request(student, "GET", "/events?city=San%20Jose")),
        "saved": len(request(student, "GET", "/saved-items")),
        "applications": len(request(student, "GET", "/applications/student")),
        "registrations": len(request(student, "GET", "/events/student/registrations")),
        "memory_status": request(student, "POST", "/assistant/chat", json={"message": "/memory"}).get("answer", "")[:40],
    }

    suffix = uuid.uuid4().hex[:10]
    company_email = f"batch10.company.{suffix}@example.com"
    request(requests.Session(), "POST", "/auth/register", json={
        "name": "Batch 10 Synthetic Company",
        "email": company_email,
        "password": COMPANY_PASSWORD,
        "role": "company",
        "company_name": "Batch 10 Synthetic Company",
        "location": "San Jose",
    })
    company, company_user = authenticated(company_email, COMPANY_PASSWORD)
    future = date.today() + timedelta(days=30)
    job_id = request(company, "POST", "/jobs", json={
        "title": f"Batch 10 Synthetic Analyst {suffix}",
        "deadline": str(future),
        "location": "San Jose",
        "salary": 90000,
        "description": "Synthetic local acceptance job.",
        "category": "internship",
        "is_remote": False,
    })["id"]
    event_id = request(company, "POST", "/events", json={
        "name": f"Batch 10 Synthetic Career Event {suffix}",
        "description": "Synthetic local acceptance event.",
        "event_date": str(future),
        "event_time": "10:00:00",
        "location": "San Jose",
        "eligibility": "Students",
    })["id"]

    resumes = request(student, "GET", "/applications/resume")
    if resumes:
        resume_path = resumes[0]["resume_path"]
    else:
        upload = student.post(
            BASE + "/applications/resume",
            files={"file": ("batch10.pdf", b"%PDF-1.4 synthetic resume", "application/pdf")},
            timeout=30,
        )
        upload.raise_for_status()
        resume_path = upload.json()["resume_path"]
    application = request(student, "POST", f"/applications/{job_id}/apply", json={"resume_path": resume_path})
    registration = request(student, "POST", f"/events/{event_id}/register")
    application_id = application["id"]

    company_checks = {
        "role": request(company, "GET", "/auth/me")["role"],
        "dashboard": request(company, "GET", "/dashboard/company"),
        "owned_jobs": len(request(company, "GET", "/company/jobs")),
        "owned_events": len(request(company, "GET", "/company/events")),
        "applicants": len(request(company, "GET", f"/applications/company/jobs/{job_id}/applicants")),
        "registrants": len(request(company, "GET", f"/events/{event_id}/registrants")),
    }
    status = request(company, "PATCH", f"/applications/company/jobs/{job_id}/applicants/{application_id}/status", json={"status": "Reviewed"})
    print(json.dumps({
        "student_id": student_user["id"],
        "student_checks": student_checks,
        "company_id": company_user["id"],
        "job_id": job_id,
        "event_id": event_id,
        "application_id": application_id,
        "registration_id": registration["id"],
        "company_checks": company_checks,
        "status_update": status,
    }, default=str, indent=2))


if __name__ == "__main__":
    main()
