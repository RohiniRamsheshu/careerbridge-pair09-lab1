from fastapi.testclient import TestClient
from backend.app import main
from backend.app.auth import get_authenticated_user
from backend.app.routes import applications


client = TestClient(main.app)


def test_jobs_include_filtered_total_metadata_without_changing_default_shape(monkeypatch):
    calls = []

    def fake_query(sql, params=(), fetch="all", commit=False):
        calls.append((sql, params, fetch))
        if fetch == "one":
            return {"total": 73}
        return [{"id": 12, "title": "Data internship"}]

    monkeypatch.setattr(main, "query_db", fake_query)
    response = client.get("/jobs?city=San%20Jose&category=internship&limit=50&offset=50&include_total=true")
    assert response.status_code == 200
    assert response.json() == {"items": [{"id": 12, "title": "Data internship"}], "total": 73, "limit": 50, "offset": 50}
    assert len(calls) == 2
    assert calls[0][2] == "one"
    assert "COUNT(*)" in calls[0][0]
    assert calls[0][1] == ("internship", "%San Jose%")
    assert calls[1][1][-2:] == (50, 50)


def test_events_include_filtered_total_metadata(monkeypatch):
    calls = []

    def fake_query(sql, params=(), fetch="all", commit=False):
        calls.append((sql, params, fetch))
        if fetch == "one":
            return {"total": 4}
        return [{"id": 8, "name": "Career event"}]

    monkeypatch.setattr(main, "query_db", fake_query)
    response = client.get("/events?city=Palo%20Alto&limit=50&offset=0&include_total=true")
    assert response.status_code == 200
    assert response.json()["total"] == 4
    assert response.json()["items"] == [{"id": 8, "name": "Career event"}]
    assert calls[0][2] == "one"
    assert "COUNT(*)" in calls[0][0]


def test_company_events_rejects_non_company(monkeypatch):
    main.app.dependency_overrides[get_authenticated_user] = lambda: {"id": 4, "role": "student"}
    try:
        response = client.get("/company/events")
    finally:
        main.app.dependency_overrides.clear()

    assert response.status_code == 403


def test_company_events_is_scoped_to_authenticated_company(monkeypatch):
    captured = {}

    def fake_query(sql, params=(), fetch="all", commit=False):
        captured["sql"] = sql
        captured["params"] = params
        return [{"id": 8, "company_user_id": 9, "name": "Career event"}]

    monkeypatch.setattr(main, "query_db", fake_query)
    main.app.dependency_overrides[get_authenticated_user] = lambda: {"id": 9, "role": "company"}
    try:
        response = client.get("/company/events")
    finally:
        main.app.dependency_overrides.clear()

    assert response.status_code == 200
    assert response.json()[0]["id"] == 8
    assert captured["params"] == (9,)
    assert "WHERE e.company_user_id = %s" in captured["sql"]


def test_job_details_includes_existing_company_contact_data(monkeypatch):
    monkeypatch.setattr(
        main,
        "query_db",
        lambda *args, **kwargs: {
            "id": 12,
            "title": "Data internship",
            "company_name": "Test Company",
            "contact_information": "hr@example.com",
        },
    )

    response = client.get("/jobs/12")

    assert response.status_code == 200
    assert response.json()["contact_information"] == "hr@example.com"


def test_student_profile_rejects_company_user():
    main.app.dependency_overrides[get_authenticated_user] = lambda: {"id": 9, "role": "company"}
    try:
        response = client.get("/student/profile")
    finally:
        main.app.dependency_overrides.clear()

    assert response.status_code == 403


def test_student_profile_uses_authenticated_student_id(monkeypatch):
    captured = {}

    def fake_query(sql, params=(), fetch="all", commit=False):
        captured["params"] = params
        return {"id": 7, "name": "Student", "college": "SJSU"}

    monkeypatch.setattr(main, "query_db", fake_query)
    main.app.dependency_overrides[get_authenticated_user] = lambda: {"id": 7, "role": "student"}
    try:
        response = client.get("/student/profile")
    finally:
        main.app.dependency_overrides.clear()

    assert response.status_code == 200
    assert response.json()["id"] == 7
    assert captured["params"] == (7,)


def test_student_profile_update_changes_authenticated_student_name(monkeypatch):
    calls = []

    def fake_query(sql, params=(), fetch="all", commit=False):
        calls.append((sql, params, commit))
        return 1

    monkeypatch.setattr(main, "query_db", fake_query)
    main.app.dependency_overrides[get_authenticated_user] = lambda: {"id": 7, "role": "student"}
    try:
        response = client.put("/student/profile", json={"name": "Updated Student", "college": "SJSU"})
    finally:
        main.app.dependency_overrides.clear()

    assert response.status_code == 200
    assert any(
        "UPDATE users SET name" in sql and params == ("Updated Student", 7) and commit
        for sql, params, commit in calls
    )


def test_student_profile_update_rejects_company_user():
    main.app.dependency_overrides[get_authenticated_user] = lambda: {"id": 9, "role": "company"}
    try:
        response = client.put("/student/profile", json={"name": "Nope", "college": "SJSU"})
    finally:
        main.app.dependency_overrides.clear()

    assert response.status_code == 403


def test_event_registrants_rejects_student_user():
    main.app.dependency_overrides[get_authenticated_user] = lambda: {"id": 7, "role": "student"}
    try:
        response = client.get("/events/8/registrants")
    finally:
        main.app.dependency_overrides.clear()

    assert response.status_code == 403


def test_event_registrants_rejects_company_that_does_not_own_event(monkeypatch):
    monkeypatch.setattr(
        main,
        "query_db",
        lambda *args, **kwargs: {"id": 8, "company_user_id": 11, "name": "Other event"},
    )
    main.app.dependency_overrides[get_authenticated_user] = lambda: {"id": 9, "role": "company"}
    try:
        response = client.get("/events/8/registrants")
    finally:
        main.app.dependency_overrides.clear()

    assert response.status_code == 403


def test_event_registrants_returns_only_owned_event_registrants(monkeypatch):
    calls = []

    def fake_query(sql, params=(), fetch="all", commit=False):
        calls.append((sql, params, fetch))
        if "FROM events" in sql:
            return {"id": 8, "company_user_id": 9, "name": "Owned event"}
        return [{"student_id": 4, "name": "Student", "email": "student@example.com"}]

    monkeypatch.setattr(main, "query_db", fake_query)
    main.app.dependency_overrides[get_authenticated_user] = lambda: {"id": 9, "role": "company"}
    try:
        response = client.get("/events/8/registrants")
    finally:
        main.app.dependency_overrides.clear()

    assert response.status_code == 200
    assert response.json()[0]["student_id"] == 4
    assert calls[0][1] == (8,)
    assert calls[1][1] == (8,)


def test_applicant_profile_rejects_student_user():
    main.app.dependency_overrides[get_authenticated_user] = lambda: {"id": 7, "role": "student"}
    try:
        response = client.get("/applications/company/jobs/8/applicants/4/profile")
    finally:
        main.app.dependency_overrides.clear()

    assert response.status_code == 403


def test_applicant_profile_requires_owned_job_and_related_application(monkeypatch):
    captured = {}

    def fake_query(sql, params=(), fetch="all", commit=False):
        captured["params"] = params
        return {"student_id": 4, "name": "Student", "email": "student@example.com", "resume_available": 1}

    monkeypatch.setattr(applications, "run_query", fake_query)
    main.app.dependency_overrides[get_authenticated_user] = lambda: {"id": 9, "role": "company"}
    try:
        response = client.get("/applications/company/jobs/8/applicants/4/profile")
    finally:
        main.app.dependency_overrides.clear()

    assert response.status_code == 200
    assert response.json()["student_id"] == 4
    assert "resume_path" not in response.json()
    assert captured["params"] == (9, 4, 8)


def test_applicant_profile_returns_not_found_for_unrelated_application(monkeypatch):
    monkeypatch.setattr(applications, "run_query", lambda *args, **kwargs: None)
    main.app.dependency_overrides[get_authenticated_user] = lambda: {"id": 9, "role": "company"}
    try:
        response = client.get("/applications/company/jobs/8/applicants/99/profile")
    finally:
        main.app.dependency_overrides.clear()

    assert response.status_code == 404


def test_applicant_profile_rejects_cross_company_access(monkeypatch):
    monkeypatch.setattr(applications, "run_query", lambda *args, **kwargs: None)
    main.app.dependency_overrides[get_authenticated_user] = lambda: {"id": 11, "role": "company"}
    try:
        response = client.get("/applications/company/jobs/8/applicants/4/profile")
    finally:
        main.app.dependency_overrides.clear()

    assert response.status_code == 404


def test_event_registrant_profile_requires_company_owned_event_and_registration(monkeypatch):
    captured = {}

    def fake_query(sql, params=(), fetch="all", commit=False):
        captured["params"] = params
        return {"student_id": 4, "name": "Student", "college": "SJSU"}

    monkeypatch.setattr(main, "query_db", fake_query)
    main.app.dependency_overrides[get_authenticated_user] = lambda: {"id": 9, "role": "company"}
    try:
        response = client.get("/company/events/8/registrants/4/profile")
    finally:
        main.app.dependency_overrides.clear()

    assert response.status_code == 200
    assert response.json()["student_id"] == 4
    assert captured["params"] == (4, 8, 9)


def test_event_registrant_profile_rejects_student_user():
    main.app.dependency_overrides[get_authenticated_user] = lambda: {"id": 4, "role": "student"}
    try:
        response = client.get("/company/events/8/registrants/4/profile")
    finally:
        main.app.dependency_overrides.clear()

    assert response.status_code == 403


def test_event_registrant_profile_returns_not_found_for_unregistered_student(monkeypatch):
    monkeypatch.setattr(main, "query_db", lambda *args, **kwargs: None)
    main.app.dependency_overrides[get_authenticated_user] = lambda: {"id": 9, "role": "company"}
    try:
        response = client.get("/company/events/8/registrants/99/profile")
    finally:
        main.app.dependency_overrides.clear()

    assert response.status_code == 404


def test_event_registrant_profile_rejects_cross_company_access(monkeypatch):
    monkeypatch.setattr(main, "query_db", lambda *args, **kwargs: None)
    main.app.dependency_overrides[get_authenticated_user] = lambda: {"id": 11, "role": "company"}
    try:
        response = client.get("/company/events/8/registrants/4/profile")
    finally:
        main.app.dependency_overrides.clear()

    assert response.status_code == 404


def test_applicant_resume_rejects_student_and_cross_company_access(monkeypatch):
    main.app.dependency_overrides[get_authenticated_user] = lambda: {"id": 7, "role": "student"}
    try:
        student_response = client.get("/applications/company/jobs/8/applicants/4/resume")
    finally:
        main.app.dependency_overrides.clear()
    assert student_response.status_code == 403

    monkeypatch.setattr(applications, "run_query", lambda *args, **kwargs: None)
    main.app.dependency_overrides[get_authenticated_user] = lambda: {"id": 11, "role": "company"}
    try:
        other_company_response = client.get("/applications/company/jobs/8/applicants/4/resume")
    finally:
        main.app.dependency_overrides.clear()
    assert other_company_response.status_code == 404


def test_applicant_resume_rejects_missing_invalid_and_non_pdf_files(monkeypatch, tmp_path):
    monkeypatch.setattr(applications, "RESUME_DIR", tmp_path)
    main.app.dependency_overrides[get_authenticated_user] = lambda: {"id": 9, "role": "company"}
    try:
        outside_path = tmp_path.parent / "outside.pdf"
        for stored_path in (tmp_path / "missing.pdf", tmp_path / "unsafe.txt", outside_path):
            if stored_path.suffix == ".txt":
                stored_path.write_text("not a pdf", encoding="utf-8")
            monkeypatch.setattr(applications, "run_query", lambda *args, path=stored_path, **kwargs: {"resume_path": str(path)})
            response = client.get("/applications/company/jobs/8/applicants/4/resume")
            assert response.status_code == 404
    finally:
        main.app.dependency_overrides.clear()


def test_applicant_resume_returns_inline_pdf_without_filesystem_path(monkeypatch, tmp_path):
    resume = tmp_path / "student_resume.pdf"
    resume.write_bytes(b"%PDF-1.7\nmock pdf")
    monkeypatch.setattr(applications, "RESUME_DIR", tmp_path)
    monkeypatch.setattr(applications, "run_query", lambda *args, **kwargs: {"resume_path": str(resume)})
    main.app.dependency_overrides[get_authenticated_user] = lambda: {"id": 9, "role": "company"}
    try:
        response = client.get("/applications/company/jobs/8/applicants/4/resume")
    finally:
        main.app.dependency_overrides.clear()

    assert response.status_code == 200
    assert response.headers["content-type"] == "application/pdf"
    assert "inline" in response.headers["content-disposition"]
    assert str(resume) not in response.text
